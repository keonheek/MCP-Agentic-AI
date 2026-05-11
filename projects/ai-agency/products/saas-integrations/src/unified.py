"""
unified.py
Common interface (PlatformAdapter ABC) for all e-commerce platform integrations.
All platform clients inherit from this base class.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
import hashlib
import hmac
import time


@dataclass
class Order:
    order_id: str
    platform: str
    customer_id: str
    customer_name: str
    customer_email: str
    customer_phone: str
    status: str
    total_price: int  # KRW, integer (no decimals)
    items: list[dict]
    created_at: str
    raw: dict = field(default_factory=dict)


@dataclass
class Customer:
    customer_id: str
    platform: str
    name: str
    email: str
    phone: str
    joined_at: str
    total_orders: int
    total_spent: int  # KRW
    raw: dict = field(default_factory=dict)


@dataclass
class WebhookEvent:
    event_id: str
    platform: str
    event_type: str   # order.created, order.paid, customer.created, inventory.low
    payload: dict
    received_at: float = field(default_factory=time.time)


class PlatformAdapter(ABC):
    """
    Abstract base for all platform integrations.
    Each adapter normalizes platform-specific data into common Order/Customer shapes.
    """

    platform_name: str = ""

    # --- Auth ---

    @abstractmethod
    def authenticate(self) -> bool:
        """Establish auth (OAuth token exchange, API key validation, etc.)."""
        ...

    @abstractmethod
    def refresh_token(self) -> bool:
        """Refresh access token if applicable. Return True if refreshed."""
        ...

    # --- Orders ---

    @abstractmethod
    def list_orders(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Order]:
        """Return normalized Order list."""
        ...

    @abstractmethod
    def get_order(self, order_id: str) -> Order:
        """Return single normalized Order."""
        ...

    # --- Customers ---

    @abstractmethod
    def list_customers(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Customer]:
        """Return normalized Customer list."""
        ...

    # --- Webhooks ---

    @abstractmethod
    def subscribe_webhook(self, event_type: str, callback_url: str) -> dict:
        """Register a webhook subscription for the given event_type."""
        ...

    @abstractmethod
    def list_webhook_subscriptions(self) -> list[dict]:
        """Return current webhook subscriptions."""
        ...

    @abstractmethod
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify incoming webhook payload signature."""
        ...

    @abstractmethod
    def parse_webhook_event(self, raw_payload: dict) -> WebhookEvent:
        """Parse raw webhook payload into normalized WebhookEvent."""
        ...

    # --- Utilities (shared) ---

    @staticmethod
    def _hmac_sha256(secret: str, payload: bytes) -> str:
        return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

    def health_check(self) -> dict:
        """Ping the platform API and return status dict."""
        try:
            ok = self.authenticate()
            return {"platform": self.platform_name, "status": "ok" if ok else "auth_failed"}
        except Exception as e:
            return {"platform": self.platform_name, "status": "error", "detail": str(e)}
