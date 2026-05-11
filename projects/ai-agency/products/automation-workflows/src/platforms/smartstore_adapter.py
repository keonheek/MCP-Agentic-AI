"""
Naver Smartstore adapter.

Smartstore does not natively support webhooks. Events are polled via
Naver Commerce API (NCP API). This adapter wraps the poll response
into the same standard event dict used by Cafe24/Imweb adapters.

Production: schedule poll_orders() every 5 minutes via n8n cron node.
Docs: https://apicenter.commerce.naver.com/ko/basic/commerce-api
"""

from __future__ import annotations
import logging
import os
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

SMARTSTORE_API_BASE = "https://api.commerce.naver.com/external"
SMARTSTORE_CLIENT_ID = os.getenv("SMARTSTORE_CLIENT_ID", "mock_client_id")
SMARTSTORE_CLIENT_SECRET = os.getenv("SMARTSTORE_CLIENT_SECRET", "mock_secret")

DELIVERY_STATUS_DELIVERED = "DELIVERED"


def poll_orders(last_checked_at: datetime) -> list[dict[str, Any]]:
    """
    Poll Smartstore for new order events since last_checked_at.
    Returns list of normalized event dicts.
    Production: make authenticated GET to /v1/pay-order/seller/orders/query-list
    """
    logger.info("Polling Smartstore orders since %s (mock)", last_checked_at.isoformat())
    return []


def parse_order_event(order: dict[str, Any]) -> dict[str, Any] | None:
    """
    Normalize a Smartstore order object into a standard event dict.
    """
    try:
        status = order.get("productOrderStatus", "")
        event_type = _map_status_to_event(status)
        if not event_type:
            return None

        product = order.get("productSnapshot", {})
        orderer = order.get("orderer", {})

        return {
            "source": "smartstore",
            "event_type": event_type,
            "customer_id": orderer.get("memberId", ""),
            "customer_name": orderer.get("name", "고객"),
            "customer_phone": orderer.get("tel", ""),
            "customer_email": orderer.get("email", ""),
            "product_id": product.get("originalProductNo", ""),
            "product_name": product.get("productName", ""),
            "order_id": order.get("productOrderId", ""),
            "event_at": datetime.utcnow().isoformat(),
            "raw": order,
        }
    except (KeyError, TypeError) as exc:
        logger.error("Failed to parse Smartstore order: %s", exc)
        return None


def _map_status_to_event(status: str) -> str | None:
    mapping = {
        "DELIVERED": "order_delivered",
        "PURCHASE_DECIDED": "order_placed",
    }
    return mapping.get(status)
