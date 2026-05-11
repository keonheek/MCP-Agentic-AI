"""
Flow 5: Win-Back Inactive (휴면 고객 복구)

Trigger: Scheduler finds customers with no purchase in 90+ days.
3-touch sequence with progressively larger discounts:
  T+0  (90 days inactive)  -> 5% off  (INFO, no promo language)
  T+7  (97 days inactive)  -> 10% off (AD)
  T+14 (104 days inactive) -> 15% off + free shipping (AD)

Stops immediately on purchase.
"""

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from src.kakao_sender import MessageType, send as kakao_send

logger = logging.getLogger(__name__)

TEMPLATE_TOUCH_1 = (
    "안녕하세요, {{customer_name}}님!\n\n"
    "오랫동안 뵙지 못했네요.\n"
    "{{brand_name}} 신제품이 출시됐는데 한번 확인해보세요.\n\n"
    "{{product_url}}"
)

TEMPLATE_TOUCH_2 = (
    "[광고] 안녕하세요, {{customer_name}}님!\n\n"
    "{{brand_name}}에서 특별히 준비했어요.\n\n"
    "오늘 주문하시면 10% 추가 할인 적용됩니다.\n"
    "코드: {{discount_code}}\n"
    "유효기간: {{expiry_date}}까지\n\n"
    "{{product_url}}"
)

TEMPLATE_TOUCH_3 = (
    "[광고] 안녕하세요, {{customer_name}}님!\n\n"
    "{{brand_name}}이(가) 마지막으로 특별 혜택을 드려요.\n\n"
    "15% 할인 + 무료 배송\n"
    "코드: {{discount_code}}\n"
    "유효기간: {{expiry_date}}까지\n\n"
    "이 코드가 마지막 혜택이에요. 놓치지 마세요!\n"
    "{{product_url}}"
)


@dataclass
class WinbackState:
    customer_id: str
    customer_name: str
    customer_phone: str
    brand_name: str
    product_url: str
    last_purchase_at: datetime
    discount_codes: dict = field(default_factory=lambda: {"touch2": "WINBACK10", "touch3": "WINBACK15"})
    touches_sent: list[str] = field(default_factory=list)
    purchased: bool = False


def _is_done(state: WinbackState) -> bool:
    return state.purchased or len(state.touches_sent) >= 3


def run_touch(state: WinbackState, mock: bool = True) -> WinbackState:
    if _is_done(state):
        return state

    now = datetime.utcnow()
    elapsed = now - state.last_purchase_at

    if "touch1" not in state.touches_sent and elapsed >= timedelta(days=90):
        _send_touch_1(state, mock)
        state.touches_sent.append("touch1")

    elif "touch2" not in state.touches_sent and elapsed >= timedelta(days=97):
        _send_touch_2(state, mock)
        state.touches_sent.append("touch2")

    elif "touch3" not in state.touches_sent and elapsed >= timedelta(days=104):
        _send_touch_3(state, mock)
        state.touches_sent.append("touch3")

    return state


def _send_touch_1(state: WinbackState, mock: bool) -> None:
    kakao_send(
        phone=state.customer_phone,
        template_code="WINBACK_TOUCH1",
        template_body=TEMPLATE_TOUCH_1,
        variables={
            "customer_name": state.customer_name,
            "brand_name": state.brand_name,
            "product_url": state.product_url,
        },
        message_type=MessageType.INFO,
        flow_name="winback_touch1",
        mock=mock,
    )
    logger.info("Winback touch1 sent to %s", state.customer_id)


def _send_touch_2(state: WinbackState, mock: bool) -> None:
    expiry = (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d")
    kakao_send(
        phone=state.customer_phone,
        template_code="WINBACK_TOUCH2",
        template_body=TEMPLATE_TOUCH_2,
        variables={
            "customer_name": state.customer_name,
            "brand_name": state.brand_name,
            "discount_code": state.discount_codes["touch2"],
            "expiry_date": expiry,
            "product_url": state.product_url,
        },
        message_type=MessageType.AD,
        flow_name="winback_touch2",
        mock=mock,
    )
    logger.info("Winback touch2 sent to %s", state.customer_id)


def _send_touch_3(state: WinbackState, mock: bool) -> None:
    expiry = (datetime.utcnow() + timedelta(days=5)).strftime("%Y-%m-%d")
    kakao_send(
        phone=state.customer_phone,
        template_code="WINBACK_TOUCH3",
        template_body=TEMPLATE_TOUCH_3,
        variables={
            "customer_name": state.customer_name,
            "brand_name": state.brand_name,
            "discount_code": state.discount_codes["touch3"],
            "expiry_date": expiry,
            "product_url": state.product_url,
        },
        message_type=MessageType.AD,
        flow_name="winback_touch3",
        mock=mock,
    )
    logger.info("Winback touch3 sent to %s", state.customer_id)


def mark_purchased(state: WinbackState) -> WinbackState:
    state.purchased = True
    return state
