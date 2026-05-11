"""
Flow 1: Abandoned Cart Recovery (장바구니 이탈 복구)

Trigger: Cafe24/Imweb webhook fires when a cart is abandoned.
Sequence:
  T+30min  -> KakaoTalk: "잊으셨나요?" (no discount)
  T+24hr   -> Email: product image + soft nudge
  T+72hr   -> KakaoTalk: 10% discount code (AD type)

State machine persisted per customer. Stops if:
  - Purchase detected
  - Customer opts out
  - All 3 touches sent
"""

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from src.kakao_sender import MessageType, send as kakao_send

logger = logging.getLogger(__name__)

TEMPLATE_30MIN = (
    "안녕하세요, {{customer_name}}님!\n\n"
    "{{product_name}} 담아두신 거 혹시 못 보셨나요?\n"
    "지금 재고가 얼마 남지 않아 안내드려요.\n"
    "천천히 확인해 보세요 :)"
)

TEMPLATE_24HR_EMAIL_SUBJECT = "[{{brand_name}}] {{product_name}} 아직 기다리고 있어요"

TEMPLATE_24HR_EMAIL_BODY = (
    "안녕하세요 {{customer_name}}님,\n\n"
    "장바구니에 담아두신 {{product_name}}이(가) 아직 기다리고 있어요.\n\n"
    "{{product_url}}\n\n"
    "{{brand_name}} 드림"
)

TEMPLATE_72HR_DISCOUNT = (
    "[광고] 안녕하세요, {{customer_name}}님!\n\n"
    "{{product_name}} 장바구니에 담아두셨는데,\n"
    "특별히 10% 할인 코드 드릴게요.\n\n"
    "코드: {{discount_code}}\n"
    "유효기간: {{expiry_date}}까지\n\n"
    "{{product_url}}"
)


@dataclass
class AbandonedCartState:
    customer_id: str
    customer_name: str
    customer_phone: str
    customer_email: str
    product_name: str
    product_url: str
    brand_name: str
    cart_abandoned_at: datetime
    discount_code: str
    touches_sent: list[str] = field(default_factory=list)
    purchased: bool = False
    opted_out: bool = False


def _is_done(state: AbandonedCartState) -> bool:
    return state.purchased or state.opted_out or len(state.touches_sent) >= 3


def run_touch(state: AbandonedCartState, email_sender=None, mock: bool = True) -> AbandonedCartState:
    """
    Call this on a scheduler. Evaluates which touch is due and sends it.
    Returns updated state.
    """
    if _is_done(state):
        return state

    now = datetime.utcnow()
    elapsed = now - state.cart_abandoned_at

    if "30min" not in state.touches_sent and elapsed >= timedelta(minutes=30):
        _send_30min(state, mock)
        state.touches_sent.append("30min")

    elif "24hr" not in state.touches_sent and elapsed >= timedelta(hours=24):
        _send_24hr_email(state, email_sender)
        state.touches_sent.append("24hr")

    elif "72hr" not in state.touches_sent and elapsed >= timedelta(hours=72):
        _send_72hr_discount(state, mock)
        state.touches_sent.append("72hr")

    return state


def _send_30min(state: AbandonedCartState, mock: bool) -> None:
    kakao_send(
        phone=state.customer_phone,
        template_code="CART_30MIN",
        template_body=TEMPLATE_30MIN,
        variables={
            "customer_name": state.customer_name,
            "product_name": state.product_name,
        },
        message_type=MessageType.INFO,
        flow_name="abandoned_cart_30min",
        mock=mock,
    )
    logger.info("Abandoned cart 30min touch sent to %s", state.customer_id)


def _send_24hr_email(state: AbandonedCartState, email_sender) -> None:
    if email_sender is None:
        logger.info(
            "[MOCK EMAIL] to=%s | subject=%s",
            state.customer_email,
            TEMPLATE_24HR_EMAIL_SUBJECT.replace("{{brand_name}}", state.brand_name)
            .replace("{{product_name}}", state.product_name),
        )
        return
    subject = (
        TEMPLATE_24HR_EMAIL_SUBJECT
        .replace("{{brand_name}}", state.brand_name)
        .replace("{{product_name}}", state.product_name)
    )
    body = (
        TEMPLATE_24HR_EMAIL_BODY
        .replace("{{customer_name}}", state.customer_name)
        .replace("{{product_name}}", state.product_name)
        .replace("{{product_url}}", state.product_url)
        .replace("{{brand_name}}", state.brand_name)
    )
    email_sender(to=state.customer_email, subject=subject, body=body)


def _send_72hr_discount(state: AbandonedCartState, mock: bool) -> None:
    expiry = (state.cart_abandoned_at + timedelta(days=4)).strftime("%Y-%m-%d")
    kakao_send(
        phone=state.customer_phone,
        template_code="CART_72HR_DISCOUNT",
        template_body=TEMPLATE_72HR_DISCOUNT,
        variables={
            "customer_name": state.customer_name,
            "product_name": state.product_name,
            "discount_code": state.discount_code,
            "expiry_date": expiry,
            "product_url": state.product_url,
        },
        message_type=MessageType.AD,
        flow_name="abandoned_cart_72hr",
        mock=mock,
    )
    logger.info("Abandoned cart 72hr discount sent to %s", state.customer_id)


def mark_purchased(state: AbandonedCartState) -> AbandonedCartState:
    state.purchased = True
    return state
