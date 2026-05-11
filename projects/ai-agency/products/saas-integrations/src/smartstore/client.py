"""
smartstore/client.py
Naver Smart Store Commerce API client.

Auth: Application ID + Secret -> Bearer token (OAuth 2.0 client credentials)
Token endpoint: https://api.commerce.naver.com/v1/oauth2/token
Token expiry: 30 minutes

Docs: https://apicenter.commerce.naver.com/ko/basic/commerce-API-guide
"""

import json
import time
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


class SmartStoreClient(PlatformAdapter):
    """
    Naver Smart Store Commerce API client.

    Required:
        application_id     - Commerce API application ID
        application_secret - Commerce API application secret
    """

    platform_name = "smartstore"
    BASE_URL = "https://api.commerce.naver.com/v1"

    def __init__(
        self,
        application_id: str,
        application_secret: str,
        access_token: str = "",
        _mock_transport=None,
    ):
        self.application_id = application_id
        self.application_secret = application_secret
        self.access_token = access_token
        self._token_expires_at: float = 0
        self._mock_transport = _mock_transport

    # ------------------------------------------------------------------ #
    # Internal HTTP
    # ------------------------------------------------------------------ #

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
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

    def _generate_signature(self, timestamp: int) -> str:
        """
        Naver Commerce API signature:
        HMAC-SHA256( application_id + "_" + timestamp, application_secret )
        Returns Base64-encoded result.
        """
        message = f"{self.application_id}_{timestamp}".encode()
        sig = hmac.new(
            self.application_secret.encode(), message, hashlib.sha256
        ).digest()
        return base64.b64encode(sig).decode()

    def authenticate(self) -> bool:
        """Get Bearer token via client credentials."""
        timestamp = int(time.time() * 1000)
        signature = self._generate_signature(timestamp)

        token_url = f"{self.BASE_URL}/oauth2/token"
        body = {
            "client_id": self.application_id,
            "timestamp": timestamp,
            "client_secret_sign": signature,
            "grant_type": "client_credentials",
            "type": "SELF",
        }

        if self._mock_transport:
            resp = self._mock_transport("POST", token_url, body)
        else:
            data = urlencode(body).encode()
            req = urllib.request.Request(
                token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )
            with urllib.request.urlopen(req) as r:
                resp = json.loads(r.read())

        if "access_token" in resp:
            self.access_token = resp["access_token"]
            self._token_expires_at = time.time() + int(resp.get("expires_in", 1800))
            return True
        return bool(self.access_token)

    def refresh_token(self) -> bool:
        """Smart Store tokens expire in 30 min. Re-authenticate."""
        if time.time() < self._token_expires_at - 60:
            return False
        return self.authenticate()

    def _ensure_token(self):
        if not self.access_token or time.time() >= self._token_expires_at - 60:
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
        # Smart Store uses productOrderStatuses + lastChangedFrom/To
        body = {
            "pageNum": (offset // limit) + 1,
            "pageSize": limit,
        }
        if start_date:
            body["placedFromDate"] = start_date
        if end_date:
            body["placedToDate"] = end_date
        if status:
            body["productOrderStatuses"] = [status]

        resp = self._post("/pay-order/seller/product-orders/query", body)
        return [self._normalize_order(o) for o in resp.get("data", {}).get("contents", [])]

    def get_order(self, order_id: str) -> Order:
        self._ensure_token()
        resp = self._get(f"/pay-order/seller/product-orders/{order_id}")
        return self._normalize_order(resp.get("data", resp))

    def _normalize_order(self, raw: dict) -> Order:
        order_info = raw.get("order", raw)
        orderer = order_info.get("ordererName", "")
        return Order(
            order_id=str(raw.get("productOrderId", "")),
            platform="smartstore",
            customer_id=str(order_info.get("ordererId", "")),
            customer_name=orderer,
            customer_email=order_info.get("ordererEmail", ""),
            customer_phone=order_info.get("ordererTel", ""),
            status=raw.get("productOrderStatus", ""),
            total_price=int(raw.get("totalPaymentAmount", 0)),
            items=[{
                "product_id": raw.get("productId", ""),
                "product_name": raw.get("productName", ""),
                "quantity": raw.get("quantity", 1),
                "unit_price": raw.get("unitPrice", 0),
            }],
            created_at=raw.get("paymentDate", raw.get("orderDate", "")),
            raw=raw,
        )

    # ------------------------------------------------------------------ #
    # Customers
    # ------------------------------------------------------------------ #

    def list_customers(self, limit: int = 50, offset: int = 0) -> list[Customer]:
        """
        Smart Store does not have a standalone customer list endpoint.
        Returns customer info extracted from recent orders.
        """
        self._ensure_token()
        orders = self.list_orders(limit=limit, offset=offset)
        seen = set()
        customers = []
        for order in orders:
            if order.customer_id not in seen:
                seen.add(order.customer_id)
                customers.append(Customer(
                    customer_id=order.customer_id,
                    platform="smartstore",
                    name=order.customer_name,
                    email=order.customer_email,
                    phone=order.customer_phone,
                    joined_at="",
                    total_orders=1,
                    total_spent=order.total_price,
                    raw=order.raw,
                ))
        return customers

    # ------------------------------------------------------------------ #
    # Webhooks
    # ------------------------------------------------------------------ #

    def subscribe_webhook(self, event_type: str, callback_url: str) -> dict:
        """
        Smart Store calls this "notification" registration.
        event_type examples: ORDER_PAYMENT_WAITING, PURCHASE_DECIDED
        """
        body = {
            "notificationUrl": callback_url,
            "notificationStatus": [event_type],
        }
        return self._post("/notification/register", body)

    def list_webhook_subscriptions(self) -> list[dict]:
        resp = self._get("/notification/list")
        return resp.get("data", [])

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Naver Commerce API signs with HMAC-SHA256 using application_secret.
        Header: X-Naver-Signature
        """
        expected = hmac.new(
            self.application_secret.encode(), payload, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    def parse_webhook_event(self, raw_payload: dict) -> WebhookEvent:
        event_type = raw_payload.get("notificationStatus", "unknown")
        return WebhookEvent(
            event_id=str(raw_payload.get("notificationId", "")),
            platform="smartstore",
            event_type=event_type,
            payload=raw_payload.get("data", raw_payload),
        )
