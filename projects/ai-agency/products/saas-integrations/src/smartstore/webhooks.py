"""
smartstore/webhooks.py
Webhook (notification) event type constants for Naver Smart Store Commerce API.

Naver uses "notificationStatus" terminology instead of event types.
Registered via POST /v1/notification/register.

Key notification statuses:
    PAYMENT_WAITING        - Payment pending
    PAYMENT_DONE           - Payment confirmed
    PRODUCT_PREPARE        - Seller preparing shipment
    DELIVERING             - In transit
    DELIVERED              - Delivered
    PURCHASE_DECIDED       - Purchase confirmed (14-day auto-confirm)
    EXCHANGE_REQUEST       - Exchange requested
    CANCEL_REQUEST         - Cancellation requested
    CANCEL_DONE            - Cancellation complete
    RETURN_REQUEST         - Return requested
    RETURN_DONE            - Return complete
"""

from dataclasses import dataclass
from typing import Callable


# Notification status constants
PAYMENT_WAITING = "PAYMENT_WAITING"
PAYMENT_DONE = "PAYMENT_DONE"
PRODUCT_PREPARE = "PRODUCT_PREPARE"
DELIVERING = "DELIVERING"
DELIVERED = "DELIVERED"
PURCHASE_DECIDED = "PURCHASE_DECIDED"
EXCHANGE_REQUEST = "EXCHANGE_REQUEST"
CANCEL_REQUEST = "CANCEL_REQUEST"
CANCEL_DONE = "CANCEL_DONE"
RETURN_REQUEST = "RETURN_REQUEST"
RETURN_DONE = "RETURN_DONE"

ALL_EVENTS = [
    PAYMENT_WAITING,
    PAYMENT_DONE,
    PRODUCT_PREPARE,
    DELIVERING,
    DELIVERED,
    PURCHASE_DECIDED,
    EXCHANGE_REQUEST,
    CANCEL_REQUEST,
    CANCEL_DONE,
    RETURN_REQUEST,
    RETURN_DONE,
]

# Core automation triggers
AUTOMATION_EVENTS = [PAYMENT_DONE, PURCHASE_DECIDED, CANCEL_DONE]


@dataclass
class SmartStoreWebhookPayload:
    notification_status: str
    notification_id: str
    product_order_id: str
    data: dict


def parse_smartstore_payload(raw: dict) -> SmartStoreWebhookPayload:
    return SmartStoreWebhookPayload(
        notification_status=raw.get("notificationStatus", ""),
        notification_id=str(raw.get("notificationId", "")),
        product_order_id=str(raw.get("productOrderId", "")),
        data=raw.get("data", {}),
    )


class SmartStoreWebhookRouter:
    """Simple event router for Smart Store notifications."""

    def __init__(self):
        self._handlers: dict[str, list[Callable]] = {}

    def on(self, event_type: str, handler: Callable[[SmartStoreWebhookPayload], None]):
        self._handlers.setdefault(event_type, []).append(handler)

    def dispatch(self, raw: dict):
        payload = parse_smartstore_payload(raw)
        for handler in self._handlers.get(payload.notification_status, []):
            handler(payload)
