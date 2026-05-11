"""
Flow 3: Restock Alert (재입고 알림)

Trigger: Product inventory transitions from 0 to >0 (webhook from Cafe24/Imweb).
Action: Notify all customers who registered for "재입고 알림" via Kakao (INFO type).

Registry: In-memory dict for demo. Production: query CRM/DB.
"""

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from datetime import datetime

from src.kakao_sender import MessageType, send as kakao_send

logger = logging.getLogger(__name__)

TEMPLATE_RESTOCK = (
    "안녕하세요, {{customer_name}}님!\n\n"
    "기다리시던 {{product_name}}이(가) 재입고됐어요.\n\n"
    "재고가 한정되어 있으니 서두르세요!\n"
    "{{product_url}}"
)

# In-memory registry. Production: replace with DB query.
# Structure: { product_id: [{"customer_id": str, "name": str, "phone": str}] }
_restock_registry: dict[str, list[dict]] = {}


def register_alert(product_id: str, customer_id: str, customer_name: str, phone: str) -> None:
    """Customer clicks '재입고 알림' on product page."""
    if product_id not in _restock_registry:
        _restock_registry[product_id] = []
    existing_ids = [c["customer_id"] for c in _restock_registry[product_id]]
    if customer_id not in existing_ids:
        _restock_registry[product_id].append(
            {"customer_id": customer_id, "name": customer_name, "phone": phone}
        )
        logger.info("Registered restock alert: customer=%s product=%s", customer_id, product_id)


def trigger_restock(product_id: str, product_name: str, product_url: str, mock: bool = True) -> int:
    """
    Called when product restocks. Sends Kakao to all registered customers.
    Returns count of messages sent.
    """
    subscribers = _restock_registry.get(product_id, [])
    if not subscribers:
        logger.info("No restock subscribers for product %s", product_id)
        return 0

    sent_count = 0
    for customer in subscribers:
        result = kakao_send(
            phone=customer["phone"],
            template_code="RESTOCK_ALERT",
            template_body=TEMPLATE_RESTOCK,
            variables={
                "customer_name": customer["name"],
                "product_name": product_name,
                "product_url": product_url,
            },
            message_type=MessageType.INFO,
            flow_name="restock_alert",
            mock=mock,
        )
        if result:
            sent_count += 1

    # Clear registry after sending so customer does not get duplicate alerts.
    _restock_registry[product_id] = []
    logger.info("Restock alert sent to %d customers for product %s", sent_count, product_id)
    return sent_count


def get_subscribers(product_id: str) -> list[dict]:
    return _restock_registry.get(product_id, [])
