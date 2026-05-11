"""
Happy-path test: one test per flow.
All Kakao sends are mocked. Zero API calls.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timedelta, date
from unittest.mock import patch, MagicMock

from src.flows.abandoned_cart import AbandonedCartState, run_touch as cart_run, mark_purchased
from src.flows.review_request import ReviewState, run_touch as review_run, submit_review
from src.flows.restock_alert import register_alert, trigger_restock, get_subscribers, _restock_registry
from src.flows.birthday_discount import BirthdayCustomer, send_birthday_discount, should_send_today
from src.flows.winback_inactive import WinbackState, run_touch as winback_run


def _mock_kakao(phone, template_code, template_body, variables, message_type, flow_name, mock=True):
    return {"status": "mock_sent", "phone": phone, "flow": flow_name}


# Flow 1: Abandoned Cart
def test_abandoned_cart_30min_touch():
    state = AbandonedCartState(
        customer_id="C001",
        customer_name="김민지",
        customer_phone="01012345678",
        customer_email="minji@test.com",
        product_name="수분 토너",
        product_url="https://brand.com/toner",
        brand_name="스킨로직",
        cart_abandoned_at=datetime.utcnow() - timedelta(minutes=35),
        discount_code="CART10-ABCDEF",
    )
    with patch("src.flows.abandoned_cart.kakao_send", side_effect=_mock_kakao):
        state = cart_run(state, mock=True)
    assert "30min" in state.touches_sent
    assert state.purchased is False
    print("PASS test_abandoned_cart_30min_touch")


def test_abandoned_cart_stops_on_purchase():
    state = AbandonedCartState(
        customer_id="C002",
        customer_name="이수진",
        customer_phone="01099998888",
        customer_email="sujin@test.com",
        product_name="레티놀 세럼",
        product_url="https://brand.com/serum",
        brand_name="스킨로직",
        cart_abandoned_at=datetime.utcnow() - timedelta(hours=75),
        discount_code="CART10-ZZZZZ",
    )
    state = mark_purchased(state)
    with patch("src.flows.abandoned_cart.kakao_send", side_effect=_mock_kakao) as mock_send:
        state = cart_run(state, mock=True)
    assert state.purchased is True
    print("PASS test_abandoned_cart_stops_on_purchase")


# Flow 2: Review Request
def test_review_request_positive_path():
    state = ReviewState(
        customer_id="C003",
        customer_name="박지은",
        customer_phone="01055556666",
        product_name="진정 앰플",
        review_url="https://brand.com/review",
        brand_ig="skinlogic_kr",
        founder_phone="01011112222",
        delivered_at=datetime.utcnow() - timedelta(days=8),
    )
    with patch("src.flows.review_request.kakao_send", side_effect=_mock_kakao):
        state = review_run(state, mock=True)
    assert state.review_requested is True
    print("PASS test_review_request_positive_path")


def test_review_negative_escalates():
    state = ReviewState(
        customer_id="C004",
        customer_name="최수민",
        customer_phone="01033334444",
        product_name="진정 앰플",
        review_url="https://brand.com/review",
        brand_ig="skinlogic_kr",
        founder_phone="01011112222",
        delivered_at=datetime.utcnow() - timedelta(days=10),
    )
    state.review_requested = True
    state = submit_review(state, "별로예요. 환불하고 싶어요.")
    with patch("src.flows.review_request.kakao_send", side_effect=_mock_kakao):
        state = review_run(state, mock=True)
    assert state.escalated is True
    assert state.sentiment == "negative"
    print("PASS test_review_negative_escalates")


# Flow 3: Restock Alert
def test_restock_alert_notifies_subscribers():
    _restock_registry.clear()
    register_alert("PROD001", "C005", "정하은", "01077778888")
    register_alert("PROD001", "C006", "강민서", "01011119999")
    assert len(get_subscribers("PROD001")) == 2
    with patch("src.flows.restock_alert.kakao_send", side_effect=_mock_kakao):
        count = trigger_restock("PROD001", "수분 토너", "https://brand.com/toner", mock=True)
    assert count == 2
    assert len(get_subscribers("PROD001")) == 0
    print("PASS test_restock_alert_notifies_subscribers")


# Flow 4: Birthday Discount
def test_birthday_discount_sent_7_days_before():
    today = date(2026, 5, 11)
    birthday_this_year = date(2026, 5, 18)
    customer = BirthdayCustomer(
        customer_id="C007",
        customer_name="윤지호",
        customer_phone="01022223333",
        birthday=birthday_this_year,
        brand_name="스킨로직",
        discount_code="BDAY15-XYZ",
    )
    assert should_send_today(customer, today) is True
    with patch("src.flows.birthday_discount.kakao_send", side_effect=_mock_kakao):
        sent = send_birthday_discount(customer, today, mock=True)
    assert sent is True
    assert customer.sent is True
    print("PASS test_birthday_discount_sent_7_days_before")


def test_birthday_discount_not_sent_wrong_day():
    today = date(2026, 5, 11)
    birthday = date(2026, 5, 20)
    customer = BirthdayCustomer(
        customer_id="C008",
        customer_name="임채원",
        customer_phone="01044445555",
        birthday=birthday,
        brand_name="스킨로직",
        discount_code="BDAY15-ABC",
    )
    assert should_send_today(customer, today) is False
    print("PASS test_birthday_discount_not_sent_wrong_day")


# Flow 5: Win-Back
def test_winback_touch1_at_90_days():
    state = WinbackState(
        customer_id="C009",
        customer_name="한소희",
        customer_phone="01066667777",
        brand_name="스킨로직",
        product_url="https://brand.com/new",
        last_purchase_at=datetime.utcnow() - timedelta(days=91),
    )
    with patch("src.flows.winback_inactive.kakao_send", side_effect=_mock_kakao):
        state = winback_run(state, mock=True)
    assert "touch1" in state.touches_sent
    print("PASS test_winback_touch1_at_90_days")


def test_winback_full_sequence():
    state = WinbackState(
        customer_id="C010",
        customer_name="신예은",
        customer_phone="01088889999",
        brand_name="스킨로직",
        product_url="https://brand.com/new",
        last_purchase_at=datetime.utcnow() - timedelta(days=110),
    )
    with patch("src.flows.winback_inactive.kakao_send", side_effect=_mock_kakao):
        for _ in range(3):
            state = winback_run(state, mock=True)
    assert "touch1" in state.touches_sent
    assert "touch2" in state.touches_sent
    assert "touch3" in state.touches_sent
    print("PASS test_winback_full_sequence")


if __name__ == "__main__":
    test_abandoned_cart_30min_touch()
    test_abandoned_cart_stops_on_purchase()
    test_review_request_positive_path()
    test_review_negative_escalates()
    test_restock_alert_notifies_subscribers()
    test_birthday_discount_sent_7_days_before()
    test_birthday_discount_not_sent_wrong_day()
    test_winback_touch1_at_90_days()
    test_winback_full_sequence()
    print("\nAll flow tests passed.")
