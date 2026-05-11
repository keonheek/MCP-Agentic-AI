"""
Flow orchestrator — routes incoming events to the correct flow.

In production this logic lives inside n8n (Service A delivery mechanism).
This module is the local Python equivalent for demo and testing purposes.

Usage:
    from src.orchestrator import handle_event
    handle_event(event_dict, customer_db, flow_states)
"""

from __future__ import annotations
import logging
import uuid
from datetime import datetime, date
from typing import Any

from src.flows.abandoned_cart import AbandonedCartState, run_touch as cart_touch, mark_purchased as cart_purchased
from src.flows.review_request import ReviewState, run_touch as review_touch
from src.flows.restock_alert import trigger_restock, register_alert
from src.flows.birthday_discount import BirthdayCustomer, run_daily_batch
from src.flows.winback_inactive import WinbackState, run_touch as winback_touch, mark_purchased as winback_purchased

logger = logging.getLogger(__name__)


def handle_event(
    event: dict[str, Any],
    flow_states: dict,
    mock: bool = True,
) -> dict:
    """
    Route a normalized event dict to the correct flow.
    flow_states is a simple in-memory dict keyed by customer_id.
    Returns updated flow_states.
    """
    event_type = event.get("event_type")
    customer_id = event.get("customer_id", "unknown")

    logger.info("Orchestrator received event: %s for customer %s", event_type, customer_id)

    if event_type == "order_cart_abandoned":
        _handle_cart_abandoned(event, flow_states, mock)

    elif event_type == "order_delivered":
        _handle_order_delivered(event, flow_states, mock)
        _stop_cart_flow_on_purchase(customer_id, flow_states)
        _stop_winback_on_purchase(customer_id, flow_states)

    elif event_type == "product_restocked":
        trigger_restock(
            product_id=event["product_id"],
            product_name=event["product_name"],
            product_url=event["product_url"],
            mock=mock,
        )

    else:
        logger.debug("No flow handler for event type: %s", event_type)

    return flow_states


def _handle_cart_abandoned(event: dict, flow_states: dict, mock: bool) -> None:
    customer_id = event["customer_id"]
    if f"cart_{customer_id}" in flow_states:
        return
    state = AbandonedCartState(
        customer_id=customer_id,
        customer_name=event.get("customer_name", "고객"),
        customer_phone=event.get("customer_phone", ""),
        customer_email=event.get("customer_email", ""),
        product_name=event.get("product_name", "상품"),
        product_url=event.get("product_url", ""),
        brand_name=event.get("brand_name", "브랜드"),
        cart_abandoned_at=datetime.utcnow(),
        discount_code=f"CART10-{uuid.uuid4().hex[:6].upper()}",
    )
    flow_states[f"cart_{customer_id}"] = state
    cart_touch(state, mock=mock)


def _handle_order_delivered(event: dict, flow_states: dict, mock: bool) -> None:
    customer_id = event["customer_id"]
    key = f"review_{customer_id}"
    if key not in flow_states:
        state = ReviewState(
            customer_id=customer_id,
            customer_name=event.get("customer_name", "고객"),
            customer_phone=event.get("customer_phone", ""),
            product_name=event.get("product_name", "상품"),
            review_url=event.get("review_url", "https://brand.com/review"),
            brand_ig=event.get("brand_ig", "brand"),
            founder_phone=event.get("founder_phone", ""),
            delivered_at=datetime.utcnow(),
        )
        flow_states[key] = state
    review_touch(flow_states[key], mock=mock)


def _stop_cart_flow_on_purchase(customer_id: str, flow_states: dict) -> None:
    key = f"cart_{customer_id}"
    if key in flow_states:
        cart_purchased(flow_states[key])


def _stop_winback_on_purchase(customer_id: str, flow_states: dict) -> None:
    key = f"winback_{customer_id}"
    if key in flow_states:
        winback_purchased(flow_states[key])


def run_scheduled_flows(flow_states: dict, birthday_customers: list, mock: bool = True) -> None:
    """
    Called by scheduler (e.g., daily cron via n8n). Runs time-based flows.
    """
    for key, state in list(flow_states.items()):
        if key.startswith("cart_") and isinstance(state, AbandonedCartState):
            cart_touch(state, mock=mock)
        elif key.startswith("review_") and isinstance(state, ReviewState):
            review_touch(state, mock=mock)
        elif key.startswith("winback_") and isinstance(state, WinbackState):
            winback_touch(state, mock=mock)

    run_daily_batch(birthday_customers, today=date.today(), mock=mock)
