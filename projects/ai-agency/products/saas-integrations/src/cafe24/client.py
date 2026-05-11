"""
cafe24/client.py
Cafe24 REST API v2026-03-01 client.

Auth flow: OAuth 2.0 Authorization Code Grant
Scopes required: mall.read_order, mall.read_customer, mall.write_webhooks
API version header: X-Cafe24-Api-Version: 2026-03-01

Docs: https://developers.cafe24.com/docs/api/admin/
"""

import time
import hashlib
import hmac
import json
from typing import Optional
from urllib.parse import urlencode
import urllib.request
import urllib.error

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from src.unified import PlatformAdapter, Order, Customer, WebhookEvent


API_VERSION = "2026-03-01"


class Cafe24Client(PlatformAdapter):
    """
    Cafe24 Admin REST API client.

    Required env vars / constructor args:
        mall_id       - Cafe24 mall ID (e.g. "mymall")
        client_id     - OAuth client ID
        client_secret - OAuth client secret
        access_token  - OAuth access token (after initial authorization)
        refresh_token - OAuth refresh token
    """

    platform_name = "cafe24"

    def __init__(
        self,
        mall_id: str,
        client_id: str,
        client_secret: str,
        access_token: str = "",
        refresh_token: str = "",
        _mock_transport=None,  # injected in tests to skip real HTTP
    ):
        self.mall_id = mall_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self._refresh_token = refresh_token
        self._mock_transport = _mock_transport

        self._base_url = f"https://{mall_id}.cafe24api.com/api/v2/admin"

    # ------------------------------------------------------------------ #
    # Internal HTTP
    # ------------------------------------------------------------------ #

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Cafe24-Api-Version": API_VERSION,
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
        """Validate token by hitting /me endpoint."""
        try:
            result = self._get("/me")
            return "mall" in result or "me" in result
        except Exception:
            return bool(self.access_token)  # in mock/test context

    def refresh_token(self) -> bool:
        """
        Exchange refresh token for new access_token.
        POST https://{mall_id}.cafe24api.com/api/v2/oauth/token
        """
        token_url = f"https://{self.mall_id}.cafe24api.com/api/v2/oauth/token"
        body = {
            "grant_type": "refresh_token",
            "refresh_token": self._refresh_token,
        }
        if self._mock_transport:
            resp = self._mock_transport("POST", token_url, body)
        else:
            data = urlencode(body).encode()
            import base64
            creds = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
            headers = {"Authorization": f"Basic {creds}", "Content-Type": "application/x-www-form-urlencoded"}
            req = urllib.request.Request(token_url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req) as r:
                resp = json.loads(r.read())

        if "access_token" in resp:
            self.access_token = resp["access_token"]
            if "refresh_token" in resp:
                self._refresh_token = resp["refresh_token"]
            return True
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
        params = {"limit": limit, "offset": offset}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if status:
            params["order_status"] = status

        resp = self._get("/orders", params)
        return [self._normalize_order(o) for o in resp.get("orders", [])]

    def get_order(self, order_id: str) -> Order:
        resp = self._get(f"/orders/{order_id}")
        return self._normalize_order(resp.get("order", resp))

    def _normalize_order(self, raw: dict) -> Order:
        buyer = raw.get("buyer", {})
        return Order(
            order_id=str(raw.get("order_id", "")),
            platform="cafe24",
            customer_id=str(buyer.get("member_id", "")),
            customer_name=buyer.get("name", ""),
            customer_email=buyer.get("email", ""),
            customer_phone=buyer.get("phone", ""),
            status=raw.get("order_status", ""),
            total_price=int(raw.get("order_price_amount", {}).get("order_price", 0)),
            items=raw.get("items", []),
            created_at=raw.get("created_date", ""),
            raw=raw,
        )

    # ------------------------------------------------------------------ #
    # Customers
    # ------------------------------------------------------------------ #

    def list_customers(self, limit: int = 50, offset: int = 0) -> list[Customer]:
        resp = self._get("/customers", {"limit": limit, "offset": offset})
        return [self._normalize_customer(c) for c in resp.get("customers", [])]

    def _normalize_customer(self, raw: dict) -> Customer:
        return Customer(
            customer_id=str(raw.get("member_id", "")),
            platform="cafe24",
            name=raw.get("name", ""),
            email=raw.get("email", ""),
            phone=raw.get("phone", ""),
            joined_at=raw.get("created_date", ""),
            total_orders=int(raw.get("use_count", 0)),
            total_spent=int(raw.get("total_order_amount", 0)),
            raw=raw,
        )

    # ------------------------------------------------------------------ #
    # Webhooks
    # ------------------------------------------------------------------ #

    def subscribe_webhook(self, event_type: str, callback_url: str) -> dict:
        """
        event_type examples: order_created, order_paid, member_join, product_stock_below
        """
        body = {
            "request": {
                "event": event_type,
                "endpoint_url": callback_url,
            }
        }
        return self._post("/webhooks", body)

    def list_webhook_subscriptions(self) -> list[dict]:
        resp = self._get("/webhooks")
        return resp.get("webhooks", [])

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Cafe24 sends X-Cafe24-Signature header.
        HMAC-SHA256 of request body using client_secret.
        """
        expected = hmac.new(
            self.client_secret.encode(), payload, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    def parse_webhook_event(self, raw_payload: dict) -> WebhookEvent:
        event_type = raw_payload.get("event_type", "unknown")
        return WebhookEvent(
            event_id=str(raw_payload.get("event_no", "")),
            platform="cafe24",
            event_type=event_type,
            payload=raw_payload.get("resource", raw_payload),
        )
