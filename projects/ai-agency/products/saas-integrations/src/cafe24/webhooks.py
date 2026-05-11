"""
cafe24/webhooks.py
Webhook event type constants and payload parsers for Cafe24.

Cafe24 webhook event types (as of API version 2026-03-01):
    order_created          - New order placed
    order_paid             - Payment confirmed
    order_shipped          - Shipment dispatched
    order_cancelled        - Order cancelled
    order_refunded         - Refund completed
    member_join            - New member registration
    member_withdrawal      - Member account deleted
    product_stock_below    - Inventory below threshold

Cafe24 sends POST to your endpoint_url with:
    Content-Type: application/json
    X-Cafe24-Signature: <hmac-sha256 hex>
    X-Cafe24-Timestamp: <unix timestamp>
"""

from dataclasses import dataclass
from typing import Callable


# Event type constants
ORDER_CREATED = "order_created"
ORDER_PAID = "order_paid"
ORDER_SHIPPED = "order_shipped"
ORDER_CANCELLED = "order_cancelled"
ORDER_REFUNDED = "order_refunded"
MEMBER_JOIN = "member_join"
MEMBER_WITHDRAWAL = "member_withdrawal"
PRODUCT_STOCK_BELOW = "product_stock_below"

ALL_EVENTS = [
    ORDER_CREATED,
    ORDER_PAID,
    ORDER_SHIPPED,
    ORDER_CANCELLED,
    ORDER_REFUNDED,
    MEMBER_JOIN,
    MEMBER_WITHDRAWAL,
    PRODUCT_STOCK_BELOW,
]

# Automation flow triggers (subset used for Service A)
AUTOMATION_EVENTS = [ORDER_PAID, MEMBER_JOIN, PRODUCT_STOCK_BELOW]


@dataclass
class Cafe24WebhookPayload:
    event_type: str
    event_no: str
    resource_id: str
    mall_id: str
    resource: dict


def parse_cafe24_payload(raw: dict) -> Cafe24WebhookPayload:
    """Parse raw Cafe24 webhook JSON into structured payload."""
    return Cafe24WebhookPayload(
        event_type=raw.get("event_type", ""),
        event_no=str(raw.get("event_no", "")),
        resource_id=str(raw.get("resource_id", "")),
        mall_id=raw.get("mall_id", ""),
        resource=raw.get("resource", {}),
    )


class Cafe24WebhookRouter:
    """
    Simple event router for Cafe24 webhooks.

    Usage:
        router = Cafe24WebhookRouter()
        router.on(ORDER_PAID, handle_paid_order)
        router.dispatch(raw_payload_dict)
    """

    def __init__(self):
        self._handlers: dict[str, list[Callable]] = {}

    def on(self, event_type: str, handler: Callable[[Cafe24WebhookPayload], None]):
        self._handlers.setdefault(event_type, []).append(handler)

    def dispatch(self, raw: dict):
        payload = parse_cafe24_payload(raw)
        for handler in self._handlers.get(payload.event_type, []):
            handler(payload)
