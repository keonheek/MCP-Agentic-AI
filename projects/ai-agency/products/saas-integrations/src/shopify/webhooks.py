"""
shopify/webhooks.py
Webhook topic constants and payload parsers for Shopify.

Shopify sends topic in the X-Shopify-Topic header, not the body.
Your endpoint handler must pass topic as raw_payload["_topic"] to parse_webhook_event().

Key topics:
    orders/create          - New order
    orders/paid            - Payment captured
    orders/fulfilled       - Shipment dispatched
    orders/cancelled       - Order cancelled
    orders/refunded        - Refund issued
    customers/create       - New customer
    customers/delete       - Customer deleted
    inventory_levels/update - Inventory updated
    products/update        - Product info changed

Full list: https://shopify.dev/docs/api/admin-rest/2025-04/resources/webhook
"""

from dataclasses import dataclass
from typing import Callable


# Topic constants
ORDERS_CREATE = "orders/create"
ORDERS_PAID = "orders/paid"
ORDERS_FULFILLED = "orders/fulfilled"
ORDERS_CANCELLED = "orders/cancelled"
ORDERS_REFUNDED = "orders/refunded"
CUSTOMERS_CREATE = "customers/create"
CUSTOMERS_DELETE = "customers/delete"
INVENTORY_UPDATE = "inventory_levels/update"
PRODUCTS_UPDATE = "products/update"

ALL_EVENTS = [
    ORDERS_CREATE,
    ORDERS_PAID,
    ORDERS_FULFILLED,
    ORDERS_CANCELLED,
    ORDERS_REFUNDED,
    CUSTOMERS_CREATE,
    CUSTOMERS_DELETE,
    INVENTORY_UPDATE,
    PRODUCTS_UPDATE,
]

AUTOMATION_EVENTS = [ORDERS_PAID, CUSTOMERS_CREATE, INVENTORY_UPDATE]


@dataclass
class ShopifyWebhookPayload:
    topic: str
    shop_domain: str
    data: dict


def parse_shopify_payload(raw: dict, topic: str = "", shop_domain: str = "") -> ShopifyWebhookPayload:
    """
    raw: parsed JSON body
    topic: value from X-Shopify-Topic header
    shop_domain: value from X-Shopify-Shop-Domain header
    """
    return ShopifyWebhookPayload(
        topic=topic or raw.pop("_topic", "unknown"),
        shop_domain=shop_domain,
        data=raw,
    )


class ShopifyWebhookRouter:
    """Simple event router for Shopify webhooks."""

    def __init__(self):
        self._handlers: dict[str, list[Callable]] = {}

    def on(self, topic: str, handler: Callable[[ShopifyWebhookPayload], None]):
        self._handlers.setdefault(topic, []).append(handler)

    def dispatch(self, raw: dict, topic: str, shop_domain: str = ""):
        payload = parse_shopify_payload(raw, topic, shop_domain)
        for handler in self._handlers.get(payload.topic, []):
            handler(payload)
