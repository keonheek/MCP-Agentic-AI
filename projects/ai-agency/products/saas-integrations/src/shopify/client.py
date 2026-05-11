"""
shopify/client.py
Shopify Admin REST API client.

Auth: Custom App access token (simplest for agency clients)
     or OAuth for public/partner apps.
API version: 2025-04 (stable as of 2026, quarterly releases)

Docs: https://shopify.dev/docs/api/admin-rest
"""

import json
import hmac
import hashlib
import base64
from typing import Optional
import urllib.request
import urllib.error
from urllib.parse import urlencode

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from src.unified import PlatformAdapter, Order, Customer, WebhookEvent


API_VERSION = "2025-04"


class ShopifyClient(PlatformAdapter):
    """
    Shopify Admin REST API client.

    For agency use, recommend Custom App tokens (no OAuth flow needed).

    Required:
        shop_domain    - e.g. "mybrand.myshopify.com"
        access_token   - Custom App access token (Admin API)
        webhook_secret - Webhook HMAC secret (from app settings)
    """

    platform_name = "shopify"

    def __init__(
        self,
        shop_domain: str,
        access_token: str,
        webhook_secret: str = "",
        _mock_transport=None,
    ):
        self.shop_domain = shop_domain
        self.access_token = access_token
        self.webhook_secret = webhook_secret
        self._mock_transport = _mock_transport

        self._base_url = f"https://{shop_domain}/admin/api/{API_VERSION}"

    # ------------------------------------------------------------------ #
    # Internal HTTP
    # ------------------------------------------------------------------ #

    def _headers(self) -> dict:
        return {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json",
        }

    def _get(self, path: str, params: dict = None) -> dict:
        url = f"{self._base_url}{path}"
        if params:
            url = f"{url}?{urlencode(params)}"
        if self._mock_transport:
            return self._mock_transport("GET", url, None)
        req = urllib.request.Request(url, headers=self._headers())
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    def _post(self, path: str, body: dict) -> dict:
        url = f"{self._base_url}{path}"
        data = json.dumps(body).encode()
        if self._mock_transport:
            return self._mock_transport("POST", url, body)
        req = urllib.request.Request(url, data=data, headers=self._headers(), method="POST")
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    # ------------------------------------------------------------------ #
    # Auth
    # ------------------------------------------------------------------ #

    def authenticate(self) -> bool:
        """Validate token by calling /shop.json."""
        try:
            result = self._get("/shop.json")
            return "shop" in result
        except Exception:
            return bool(self.access_token)

    def refresh_token(self) -> bool:
        """Custom App tokens do not expire. No-op."""
        return False

    # ------------------------------------------------------------------ #
    # Orders
    # ------------------------------------------------------------------ #

    def list_orders(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Order]:
        params = {"limit": min(limit, 250)}  # Shopify max 250 per page
        if start_date:
            params["created_at_min"] = start_date
        if end_date:
            params["created_at_max"] = end_date
        if status:
            params["financial_status"] = status

        resp = self._get("/orders.json", params)
        return [self._normalize_order(o) for o in resp.get("orders", [])]

    def get_order(self, order_id: str) -> Order:
        resp = self._get(f"/orders/{order_id}.json")
        return self._normalize_order(resp.get("order", resp))

    def _normalize_order(self, raw: dict) -> Order:
        customer = raw.get("customer", {})
        addr = raw.get("shipping_address", {})
        return Order(
            order_id=str(raw.get("id", "")),
            platform="shopify",
            customer_id=str(customer.get("id", "")),
            customer_name=f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip(),
            customer_email=customer.get("email", raw.get("email", "")),
            customer_phone=customer.get("phone", addr.get("phone", "")),
            status=raw.get("financial_status", raw.get("fulfillment_status", "")),
            total_price=int(float(raw.get("total_price", 0))),
            items=[
                {
                    "product_id": li.get("product_id"),
                    "variant_id": li.get("variant_id"),
                    "title": li.get("title"),
                    "quantity": li.get("quantity"),
                    "price": li.get("price"),
                }
                for li in raw.get("line_items", [])
            ],
            created_at=raw.get("created_at", ""),
            raw=raw,
        )

    # ------------------------------------------------------------------ #
    # Customers
    # ------------------------------------------------------------------ #

    def list_customers(self, limit: int = 50, offset: int = 0) -> list[Customer]:
        params = {"limit": min(limit, 250)}
        resp = self._get("/customers.json", params)
        return [self._normalize_customer(c) for c in resp.get("customers", [])]

    def _normalize_customer(self, raw: dict) -> Customer:
        return Customer(
            customer_id=str(raw.get("id", "")),
            platform="shopify",
            name=f"{raw.get('first_name', '')} {raw.get('last_name', '')}".strip(),
            email=raw.get("email", ""),
            phone=raw.get("phone", ""),
            joined_at=raw.get("created_at", ""),
            total_orders=int(raw.get("orders_count", 0)),
            total_spent=int(float(raw.get("total_spent", 0))),
            raw=raw,
        )

    # ------------------------------------------------------------------ #
    # Webhooks
    # ------------------------------------------------------------------ #

    def subscribe_webhook(self, event_type: str, callback_url: str) -> dict:
        """
        event_type (Shopify topic) examples:
            orders/create, orders/paid, customers/create, inventory_levels/update
        """
        body = {
            "webhook": {
                "topic": event_type,
                "address": callback_url,
                "format": "json",
            }
        }
        return self._post("/webhooks.json", body)

    def list_webhook_subscriptions(self) -> list[dict]:
        resp = self._get("/webhooks.json")
        return resp.get("webhooks", [])

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Shopify signs webhook body with HMAC-SHA256 using webhook_secret.
        Header: X-Shopify-Hmac-Sha256 (Base64-encoded)
        """
        expected = base64.b64encode(
            hmac.new(self.webhook_secret.encode(), payload, hashlib.sha256).digest()
        ).decode()
        return hmac.compare_digest(expected, signature)

    def parse_webhook_event(self, raw_payload: dict) -> WebhookEvent:
        # Shopify sends topic in X-Shopify-Topic header, not body
        # Caller must pass topic in raw_payload["_topic"]
        event_type = raw_payload.pop("_topic", "unknown")
        return WebhookEvent(
            event_id=str(raw_payload.get("id", "")),
            platform="shopify",
            event_type=event_type,
            payload=raw_payload,
        )
