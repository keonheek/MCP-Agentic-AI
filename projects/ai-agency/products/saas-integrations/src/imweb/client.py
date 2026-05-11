"""
imweb/client.py
Imweb API client.

Auth: API Key + Secret -> access_token (POST /v2/api/auth/token)
Token expires every 24 hours. No OAuth redirect needed.

Docs: https://api.imweb.me/v2/doc
"""

import json
import time
import hmac
import hashlib
from typing import Optional
import urllib.request
import urllib.error
from urllib.parse import urlencode

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from src.unified import PlatformAdapter, Order, Customer, WebhookEvent


class ImwebClient(PlatformAdapter):
    """
    Imweb API v2 client.

    Required:
        api_key    - Imweb API key (from dashboard > Settings > Developer)
        api_secret - Imweb API secret
    """

    platform_name = "imweb"
    BASE_URL = "https://api.imweb.me/v2"

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        access_token: str = "",
        _mock_transport=None,
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self._token_expires_at: float = 0
        self._mock_transport = _mock_transport

    # ------------------------------------------------------------------ #
    # Internal HTTP
    # ------------------------------------------------------------------ #

    def _headers(self) -> dict:
        return {
            "access-token": self.access_token,
            "Content-Type": "application/json",
        }

    def _get(self, path: str, params: dict = None) -> dict:
        url = f"{self.BASE_URL}{path}"
        if params:
            url = f"{url}?{urlencode(params)}"
        if self._mock_transport:
            return self._mock_transport("GET", url, None)
        req = urllib.request.Request(url, headers=self._headers())
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    def _post(self, path: str, body: dict) -> dict:
        url = f"{self.BASE_URL}{path}"
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
        """Exchange api_key + api_secret for access_token."""
        token_url = f"{self.BASE_URL}/api/auth/token"
        body = {"key": self.api_key, "secret": self.api_secret}
        if self._mock_transport:
            resp = self._mock_transport("POST", token_url, body)
        else:
            data = json.dumps(body).encode()
            req = urllib.request.Request(
                token_url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req) as r:
                resp = json.loads(r.read())

        if resp.get("code") == 200 and "access_token" in resp.get("data", {}):
            self.access_token = resp["data"]["access_token"]
            self._token_expires_at = time.time() + 86400  # 24h
            return True
        return bool(self.access_token)  # mock/test fallback

    def refresh_token(self) -> bool:
        """Imweb tokens expire in 24h. Re-authenticate to refresh."""
        if time.time() < self._token_expires_at - 300:
            return False  # not expired yet
        return self.authenticate()

    def _ensure_token(self):
        if not self.access_token or time.time() >= self._token_expires_at - 300:
            self.authenticate()

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
        self._ensure_token()
        params = {"limit": limit, "offset": offset}
        if start_date:
            params["orderDateStart"] = start_date
        if end_date:
            params["orderDateEnd"] = end_date
        if status:
            params["orderStatus"] = status

        resp = self._get("/api/shop/orders", params)
        orders_data = resp.get("data", {}).get("list", [])
        return [self._normalize_order(o) for o in orders_data]

    def get_order(self, order_id: str) -> Order:
        self._ensure_token()
        resp = self._get(f"/api/shop/orders/{order_id}")
        return self._normalize_order(resp.get("data", resp))

    def _normalize_order(self, raw: dict) -> Order:
        member = raw.get("memberInfo", {})
        return Order(
            order_id=str(raw.get("orderCode", "")),
            platform="imweb",
            customer_id=str(raw.get("memberCode", "")),
            customer_name=member.get("name", raw.get("orderName", "")),
            customer_email=member.get("email", raw.get("orderEmail", "")),
            customer_phone=raw.get("orderPhone", ""),
            status=raw.get("orderStatus", ""),
            total_price=int(raw.get("payPrice", 0)),
            items=raw.get("prodList", []),
            created_at=raw.get("addTime", ""),
            raw=raw,
        )

    # ------------------------------------------------------------------ #
    # Customers
    # ------------------------------------------------------------------ #

    def list_customers(self, limit: int = 50, offset: int = 0) -> list[Customer]:
        self._ensure_token()
        resp = self._get("/api/member/members", {"limit": limit, "offset": offset})
        members = resp.get("data", {}).get("list", [])
        return [self._normalize_customer(c) for c in members]

    def _normalize_customer(self, raw: dict) -> Customer:
        return Customer(
            customer_id=str(raw.get("memberCode", "")),
            platform="imweb",
            name=raw.get("name", ""),
            email=raw.get("email", ""),
            phone=raw.get("phone", ""),
            joined_at=raw.get("addTime", ""),
            total_orders=int(raw.get("orderCount", 0)),
            total_spent=int(raw.get("orderAmount", 0)),
            raw=raw,
        )

    # ------------------------------------------------------------------ #
    # Webhooks
    # ------------------------------------------------------------------ #

    def subscribe_webhook(self, event_type: str, callback_url: str) -> dict:
        """
        event_type examples: order.create, order.pay, member.create
        """
        body = {
            "event": event_type,
            "hookUrl": callback_url,
        }
        return self._post("/api/hook", body)

    def list_webhook_subscriptions(self) -> list[dict]:
        resp = self._get("/api/hook")
        return resp.get("data", {}).get("list", [])

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Imweb signs with HMAC-SHA256 of payload using api_secret.
        Header: X-IMWEB-SIGNATURE
        """
        expected = hmac.new(
            self.api_secret.encode(), payload, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    def parse_webhook_event(self, raw_payload: dict) -> WebhookEvent:
        event_type = raw_payload.get("event", "unknown")
        return WebhookEvent(
            event_id=str(raw_payload.get("hookSeq", "")),
            platform="imweb",
            event_type=event_type,
            payload=raw_payload.get("data", raw_payload),
        )
