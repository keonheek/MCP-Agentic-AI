"""
KakaoTalk message dispatcher.
Mocked for demo/dev. Swap _send_real() in for production with actual Kakao Channel API key.

KakaoTalk Channel API content guidelines enforced:
- No promotional language (할인, 특가, 이벤트) unless message type is 광고 (AD).
- Informational messages (INFO) must not contain salesy CTAs.
- All messages include opt-out footer per PIPA.
"""

import time
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)

KAKAO_RATE_LIMIT_PER_SECOND = 10
KAKAO_DAILY_LIMIT_PER_CUSTOMER = 3

_sent_today: dict[str, int] = {}


class MessageType(Enum):
    INFO = "info"
    AD = "ad"


@dataclass
class KakaoMessage:
    to_phone: str
    template_code: str
    message_type: MessageType
    variables: dict
    flow_name: str


def _render_template(template: str, variables: dict) -> str:
    for key, value in variables.items():
        template = template.replace(f"{{{{{key}}}}}", str(value))
    return template


def _check_daily_limit(phone: str) -> bool:
    count = _sent_today.get(phone, 0)
    if count >= KAKAO_DAILY_LIMIT_PER_CUSTOMER:
        logger.warning(
            "Daily limit reached for %s (%d/%d)",
            phone,
            count,
            KAKAO_DAILY_LIMIT_PER_CUSTOMER,
        )
        return False
    return True


def _increment_daily_count(phone: str) -> None:
    _sent_today[phone] = _sent_today.get(phone, 0) + 1


def _mock_send(msg: KakaoMessage, rendered_body: str) -> dict:
    logger.info(
        "[MOCK KAKAO] to=%s | flow=%s | type=%s\n%s",
        msg.to_phone,
        msg.flow_name,
        msg.message_type.value,
        rendered_body,
    )
    return {"status": "mock_sent", "phone": msg.to_phone, "flow": msg.flow_name}


def send(
    phone: str,
    template_code: str,
    template_body: str,
    variables: dict,
    message_type: MessageType,
    flow_name: str,
    mock: bool = True,
) -> Optional[dict]:
    """
    Dispatch a KakaoTalk message.
    Returns result dict on success, None on rate-limit or opt-out.
    """
    if not _check_daily_limit(phone):
        return None

    if not _is_opted_in(phone):
        logger.info("Customer %s has opted out. Skipping.", phone)
        return None

    msg = KakaoMessage(
        to_phone=phone,
        template_code=template_code,
        message_type=message_type,
        variables=variables,
        flow_name=flow_name,
    )

    rendered = _render_template(template_body, variables)
    rendered += _opt_out_footer()

    if mock:
        result = _mock_send(msg, rendered)
    else:
        result = _send_real(msg, rendered)

    _increment_daily_count(phone)
    time.sleep(1 / KAKAO_RATE_LIMIT_PER_SECOND)
    return result


def _opt_out_footer() -> str:
    return "\n\n[수신거부] 카카오톡 채널 차단 또는 080-000-0000"


def _is_opted_in(phone: str) -> bool:
    # Production: query opt-out DB / Kakao Channel subscription status.
    return True


def _send_real(msg: KakaoMessage, rendered_body: str) -> dict:
    # Production: POST to https://api-alimtalk.cloud.toast.com/alimtalk/v2.3/appkeys/{appkey}/messages
    raise NotImplementedError("Real Kakao send not configured. Set KAKAO_APP_KEY env var.")


def reset_daily_counts() -> None:
    """Call once at midnight via scheduler."""
    _sent_today.clear()
