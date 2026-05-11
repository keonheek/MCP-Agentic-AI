"""
Flow 2: Post-Purchase Review Request (구매 후 리뷰 요청)

Trigger: Delivery confirmed (webhook from Cafe24/Imweb/Smartstore).
Sequence:
  T+7days  -> KakaoTalk: ask for review (INFO)
  If positive sentiment -> ask for IG repost (INFO)
  If negative sentiment -> escalate to founder (internal Kakao/email)

Sentiment gate: simple keyword check. Swap for GPT-4o call in production.
"""

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from src.kakao_sender import MessageType, send as kakao_send

logger = logging.getLogger(__name__)

TEMPLATE_REVIEW_REQUEST = (
    "안녕하세요, {{customer_name}}님!\n\n"
    "{{product_name}} 잘 받으셨나요? :)\n\n"
    "사용해보시고 솔직한 후기를 남겨주시면\n"
    "저희가 더 좋은 제품을 만드는 데 큰 도움이 돼요.\n\n"
    "리뷰 작성: {{review_url}}"
)

TEMPLATE_IG_REPOST = (
    "안녕하세요, {{customer_name}}님!\n\n"
    "후기 남겨주셔서 정말 감사해요.\n\n"
    "혹시 인스타그램에도 공유해주실 수 있으시면\n"
    "@{{brand_ig}}를 태그해주세요!\n"
    "리포스트되신 분들께는 다음 구매시 특별 혜택 드리고 있어요 :)"
)

NEGATIVE_KEYWORDS = ["별로", "실망", "환불", "불만", "최악", "후회", "반품", "안좋", "별1", "별2"]
POSITIVE_KEYWORDS = ["좋아요", "만족", "최고", "재구매", "추천", "별5", "완벽", "대박", "굿"]


@dataclass
class ReviewState:
    customer_id: str
    customer_name: str
    customer_phone: str
    product_name: str
    review_url: str
    brand_ig: str
    founder_phone: str
    delivered_at: datetime
    review_requested: bool = False
    review_text: Optional[str] = None
    sentiment: Optional[str] = None
    ig_requested: bool = False
    escalated: bool = False


def classify_sentiment(review_text: str) -> str:
    lower = review_text.lower()
    neg_score = sum(1 for kw in NEGATIVE_KEYWORDS if kw in lower)
    pos_score = sum(1 for kw in POSITIVE_KEYWORDS if kw in lower)
    if neg_score > pos_score:
        return "negative"
    if pos_score > 0:
        return "positive"
    return "neutral"


def run_touch(state: ReviewState, mock: bool = True) -> ReviewState:
    now = datetime.utcnow()
    elapsed = now - state.delivered_at

    if not state.review_requested and elapsed >= timedelta(days=7):
        _send_review_request(state, mock)
        state.review_requested = True
        return state

    if state.review_requested and state.review_text and not state.ig_requested and not state.escalated:
        state.sentiment = classify_sentiment(state.review_text)
        if state.sentiment == "positive":
            _send_ig_request(state, mock)
            state.ig_requested = True
        elif state.sentiment == "negative":
            _escalate_to_founder(state, mock)
            state.escalated = True

    return state


def submit_review(state: ReviewState, review_text: str) -> ReviewState:
    """Called when customer submits a review (webhook from review platform)."""
    state.review_text = review_text
    return state


def _send_review_request(state: ReviewState, mock: bool) -> None:
    kakao_send(
        phone=state.customer_phone,
        template_code="REVIEW_REQUEST",
        template_body=TEMPLATE_REVIEW_REQUEST,
        variables={
            "customer_name": state.customer_name,
            "product_name": state.product_name,
            "review_url": state.review_url,
        },
        message_type=MessageType.INFO,
        flow_name="review_request",
        mock=mock,
    )
    logger.info("Review request sent to %s", state.customer_id)


def _send_ig_request(state: ReviewState, mock: bool) -> None:
    kakao_send(
        phone=state.customer_phone,
        template_code="REVIEW_IG_REPOST",
        template_body=TEMPLATE_IG_REPOST,
        variables={
            "customer_name": state.customer_name,
            "brand_ig": state.brand_ig,
        },
        message_type=MessageType.INFO,
        flow_name="review_ig_repost",
        mock=mock,
    )
    logger.info("IG repost request sent to %s", state.customer_id)


def _escalate_to_founder(state: ReviewState, mock: bool) -> None:
    escalation_msg = (
        "[내부 알림] 부정 후기 접수\n\n"
        f"고객: {state.customer_name}\n"
        f"제품: {state.product_name}\n"
        f"후기: {state.review_text}\n\n"
        "빠른 확인 후 고객 응대 부탁드립니다."
    )
    if mock:
        logger.warning("[MOCK ESCALATION] founder=%s | msg=%s", state.founder_phone, escalation_msg)
    else:
        kakao_send(
            phone=state.founder_phone,
            template_code="REVIEW_ESCALATION",
            template_body=escalation_msg,
            variables={},
            message_type=MessageType.INFO,
            flow_name="review_escalation",
            mock=False,
        )
    logger.info("Negative review escalated for %s", state.customer_id)
