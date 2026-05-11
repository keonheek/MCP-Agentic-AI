"""
Cafe24 webhook adapter.

Receives webhooks from Cafe24 and normalizes them into a standard event dict
that the orchestrator understands.

Cafe24 webhook docs: https://developers.cafe24.com/app/front/reference/webhook
"""

from __future__ import annotations
import hashlib
import hmac
import logging
import os
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

SUPPORTED_EVENTS = {
    "order_cart_abandoned",
    "order_placed",
    "order_delivered",
    "product_restocked",
}

CAFE24_WEBHOOK_SECRET = os.getenv("CAFE24_WEBHOOK_SECRET", "mock_secret")


def verify_signature(raw_body: bytes, signature_header: str) -> bool:
    """Validate HMAC-SHA256 signature from Cafe24."""
    expected = hmac.new(
        CAFE24_WEBHOOK_SECRET.encode(),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)


def parse_event(payload: dict[str, Any]) -> dict[str, Any] | None:
    """
    Normalize a Cafe24 webhook payload into a standard event.
    Returns None if event type is unsupported or payload is malformed.
    """
    event_type = payload.get("event_type") or payload.get("event")
    if event_type not in SUPPORTED_EVENTS:
        logger.debug("Unsupported Cafe24 event: %s", event_type)
        return None

    try:
        event = {
            "source": "cafe24",
            "event_type": event_type,
            "raw": payload,
        }

        if event_type == "order_cart_abandoned":
            event.update(_parse_cart_abandoned(payload))
        elif event_type in ("order_placed", "order_delivered"):
            event.update(_parse_order(payload, event_type))
        elif event_type == "product_restocked":
            event.update(_parse_restock(payload))

        return event

    except (KeyError, TypeError) as exc:
        logger.error("Failed to parse Cafe24 payload: %s | payload=%s", exc, payload)
        return None


def _parse_cart_abandoned(payload: dict) -> dict:
    customer = payload["buyer"]
    items = payload.get("items", [{}])
    first_item = items[0] if items else {}
    return {
        "customer_id": customer["member_id"],
        "customer_name": customer.get("name", "고객"),
        "customer_phone": customer.get("cellphone", ""),
        "customer_email": customer.get("email", ""),
        "product_id": first_item.get("product_no", ""),
        "product_name": first_item.get("product_name", ""),
        "product_url": first_item.get("detail_page_url", ""),
        "event_at": datetime.utcnow().isoformat(),
    }


def _parse_order(payload: dict, event_type: str) -> dict:
    customer = payload.get("buyer", {})
    items = payload.get("items", [{}])
    first_item = items[0] if items else {}
    return {
        "customer_id": customer.get("member_id", ""),
        "customer_name": customer.get("name", "고객"),
        "customer_phone": customer.get("cellphone", ""),
        "customer_email": customer.get("email", ""),
        "product_id": first_item.get("product_no", ""),
        "product_name": first_item.get("product_name", ""),
        "order_id": payload.get("order_id", ""),
        "event_at": datetime.utcnow().isoformat(),
    }


def _parse_restock(payload: dict) -> dict:
    product = payload.get("product", {})
    return {
        "product_id": product.get("product_no", ""),
        "product_name": product.get("product_name", ""),
        "product_url": product.get("detail_page_url", ""),
        "stock_count": product.get("stock", 0),
        "event_at": datetime.utcnow().isoformat(),
    }
