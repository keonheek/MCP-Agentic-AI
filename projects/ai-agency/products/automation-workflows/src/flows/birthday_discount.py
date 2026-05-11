"""
Flow 4: Birthday Discount (생일 쿠폰)

Trigger: Scheduler runs daily, finds customers whose birthday is 7 days away.
Message: KakaoTalk AD type (contains discount code).
Code expiry: Day after birthday (2-day window total).

AD template rules: must include "[광고]" prefix per Kakao guidelines.
"""

from __future__ import annotations
import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from src.kakao_sender import MessageType, send as kakao_send

logger = logging.getLogger(__name__)

TEMPLATE_BIRTHDAY = (
    "[광고] 안녕하세요, {{customer_name}}님!\n\n"
    "{{brand_name}}에서 생일을 진심으로 축하드려요.\n\n"
    "특별한 날을 위한 선물을 준비했어요.\n\n"
    "생일 축하 15% 할인 코드: {{discount_code}}\n"
    "사용 기간: {{start_date}} ~ {{expiry_date}}\n\n"
    "오늘도 좋은 하루 보내세요 :)"
)


@dataclass
class BirthdayCustomer:
    customer_id: str
    customer_name: str
    customer_phone: str
    birthday: date
    brand_name: str
    discount_code: str
    sent: bool = False


def should_send_today(customer: BirthdayCustomer, today: date = None) -> bool:
    """Returns True if today is 7 days before the customer's birthday."""
    if today is None:
        today = date.today()
    this_year_birthday = customer.birthday.replace(year=today.year)
    if this_year_birthday < today:
        this_year_birthday = this_year_birthday.replace(year=today.year + 1)
    return (this_year_birthday - today).days == 7


def send_birthday_discount(customer: BirthdayCustomer, today: date = None, mock: bool = True) -> bool:
    """Send birthday discount Kakao. Returns True if sent."""
    if customer.sent:
        logger.info("Birthday Kakao already sent to %s this year", customer.customer_id)
        return False

    if today is None:
        today = date.today()

    this_year_birthday = customer.birthday.replace(year=today.year)
    if this_year_birthday < today:
        this_year_birthday = this_year_birthday.replace(year=today.year + 1)

    expiry = this_year_birthday + timedelta(days=1)

    result = kakao_send(
        phone=customer.customer_phone,
        template_code="BIRTHDAY_DISCOUNT",
        template_body=TEMPLATE_BIRTHDAY,
        variables={
            "customer_name": customer.customer_name,
            "brand_name": customer.brand_name,
            "discount_code": customer.discount_code,
            "start_date": this_year_birthday.strftime("%m월 %d일"),
            "expiry_date": expiry.strftime("%m월 %d일"),
        },
        message_type=MessageType.AD,
        flow_name="birthday_discount",
        mock=mock,
    )
    if result:
        customer.sent = True
        logger.info("Birthday discount sent to %s", customer.customer_id)
        return True
    return False


def run_daily_batch(customers: list[BirthdayCustomer], today: date = None, mock: bool = True) -> int:
    """
    Called once per day by scheduler.
    Sends birthday messages to all eligible customers.
    Returns count sent.
    """
    if today is None:
        today = date.today()
    sent_count = 0
    for customer in customers:
        if should_send_today(customer, today):
            if send_birthday_discount(customer, today, mock):
                sent_count += 1
    logger.info("Birthday batch: %d messages sent on %s", sent_count, today)
    return sent_count
