"""
Imweb webhook adapter.

Imweb is common among Korean skincare D2C brands on their own domains.
Normalizes Imweb webhook payloads into the same standard event dict as Cafe24 adapter.
"""

from __future__ import annotations
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

SUPPORTED_EVENTS = {
    "cart_abandon",
    "order_complete",
    "delivery_complete",
    "product_restock",
}


def parse_event(payload: dict[str, Any]) -> dict[str, Any] | None:
    """
    Normalize an Imweb webhook payload into a standard event.
    Returns None if unsupported or malformed.
    """
    event_type = payload.get("type") or payload.get("eventType")
    if event_type not in SUPPORTED_EVENTS:
        logger.debug("Unsupported Imweb event: %s", event_type)
        return None

    try:
        event = {
            "source": "imweb",
            "event_type": _normalize_event_type(event_type),
            "raw": payload,
        }

        if event_type == "cart_abandon":
            event.update(_parse_cart(payload))
        elif event_type in ("order_complete", "delivery_complete"):
            event.update(_parse_order(payload, event_type))
        elif event_type == "product_restock":
            event.update(_parse_restock(payload))

        return event

    except (KeyError, TypeError) as exc:
        logger.error("Failed to parse Imweb payload: %s | payload=%s", exc, payload)
        return None


def _normalize_event_type(imweb_type: str) -> str:
    mapping = {
        "cart_abandon": "order_cart_abandoned",
        "order_complete": "order_placed",
        "delivery_complete": "order_delivered",
        "product_restock": "product_restocked",
    }
    return mapping.get(imweb_type, imweb_type)


def _parse_cart(payload: dict) -> dict:
    member = payload.get("member", {})
    item = payload.get("cartItem", {})
    return {
        "customer_id": member.get("code", ""),
        "customer_name": member.get("name", "고객"),
        "customer_phone": member.get("phone", ""),
        "customer_email": member.get("email", ""),
        "product_id": item.get("productCode", ""),
        "product_name": item.get("productName", ""),
        "product_url": item.get("productUrl", ""),
        "event_at": datetime.utcnow().isoformat(),
    }


def _parse_order(payload: dict, event_type: str) -> dict:
    member = payload.get("member", {})
    item = payload.get("orderItem", {})
    return {
        "customer_id": member.get("code", ""),
        "customer_name": member.get("name", "고객"),
        "customer_phone": member.get("phone", ""),
        "customer_email": member.get("email", ""),
        "product_id": item.get("productCode", ""),
        "product_name": item.get("productName", ""),
        "order_id": payload.get("orderCode", ""),
        "event_at": datetime.utcnow().isoformat(),
    }


def _parse_restock(payload: dict) -> dict:
    product = payload.get("product", {})
    return {
        "product_id": product.get("code", ""),
        "product_name": product.get("name", ""),
        "product_url": product.get("url", ""),
        "stock_count": product.get("stock", 0),
        "event_at": datetime.utcnow().isoformat(),
    }
