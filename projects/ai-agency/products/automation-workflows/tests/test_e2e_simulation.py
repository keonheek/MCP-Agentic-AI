"""
30-day customer journey simulation.
Simulates 3 customer archetypes through the full flow sequence.
Zero real API calls.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timedelta, date
from unittest.mock import patch
import src.kakao_sender as sender
from src.kakao_sender import reset_daily_counts

from src.flows.abandoned_cart import AbandonedCartState, run_touch as cart_run, mark_purchased
from src.flows.review_request import ReviewState, run_touch as review_run, submit_review
from src.flows.winback_inactive import WinbackState, run_touch as winback_run
from src.flows.birthday_discount import BirthdayCustomer, run_daily_batch


def mock_kakao(phone, template_code, template_body, variables, message_type, flow_name, mock=True):
    return {"status": "mock_sent", "phone": phone, "flow": flow_name}


# Archetype 1: Cart abandoner who converts on 72hr discount
def test_journey_cart_abandoner_converts():
    reset_daily_counts()
    base_time = datetime.utcnow()

    state = AbandonedCartState(
        customer_id="J001",
        customer_name="이현아",
        customer_phone="01010101010",
        customer_email="hyuna@test.com",
        product_name="수분 에센스",
        product_url="https://brand.com/essence",
        brand_name="스킨로직",
        cart_abandoned_at=base_time - timedelta(minutes=35),
        discount_code="CART10-CONV",
    )

    with patch.object(sender, "send", side_effect=mock_kakao):
        # T+30min touch
        state = cart_run(state, mock=True)
        assert "30min" in state.touches_sent

        # Simulate 24hr passing
        state.cart_abandoned_at = base_time - timedelta(hours=25)
        state = cart_run(state, mock=True)
        assert "24hr" in state.touches_sent

        # Simulate 72hr passing
        state.cart_abandoned_at = base_time - timedelta(hours=73)
        state = cart_run(state, mock=True)
        assert "72hr" in state.touches_sent

        # Customer converts
        state = mark_purchased(state)
        state = cart_run(state, mock=True)

    assert state.purchased is True
    assert len(state.touches_sent) == 3
    print("PASS test_journey_cart_abandoner_converts")


# Archetype 2: Loyal buyer leaves positive review, gets IG request
def test_journey_loyal_reviewer():
    reset_daily_counts()

    state = ReviewState(
        customer_id="J002",
        customer_name="김소연",
        customer_phone="01020202020",
        product_name="진정 마스크팩",
        review_url="https://brand.com/review",
        brand_ig="skinlogic_kr",
        founder_phone="01099990000",
        delivered_at=datetime.utcnow() - timedelta(days=8),
    )

    with patch.object(sender, "send", side_effect=mock_kakao):
        state = review_run(state, mock=True)
        assert state.review_requested is True

        state = submit_review(state, "완전 좋아요! 재구매 확정이에요. 별5점!")
        state = review_run(state, mock=True)

    assert state.sentiment == "positive"
    assert state.ig_requested is True
    assert state.escalated is False
    print("PASS test_journey_loyal_reviewer")


# Archetype 3: Inactive customer full 3-touch winback
def test_journey_inactive_winback():
    reset_daily_counts()
    base = datetime.utcnow()

    state = WinbackState(
        customer_id="J003",
        customer_name="정민준",
        customer_phone="01030303030",
        brand_name="스킨로직",
        product_url="https://brand.com/new",
        last_purchase_at=base - timedelta(days=105),
    )

    with patch.object(sender, "send", side_effect=mock_kakao):
        state = winback_run(state, mock=True)
        state = winback_run(state, mock=True)
        state = winback_run(state, mock=True)

    assert len(state.touches_sent) == 3
    assert state.purchased is False
    print("PASS test_journey_inactive_winback")


# Birthday batch simulation
def test_journey_birthday_batch():
    reset_daily_counts()
    today = date(2026, 5, 11)
    customers = [
        BirthdayCustomer("J004", "오예린", "01040404040", date(2026, 5, 18), "스킨로직", "BDAY-J004"),
        BirthdayCustomer("J005", "배승현", "01050505050", date(2026, 5, 25), "스킨로직", "BDAY-J005"),
        BirthdayCustomer("J006", "조하린", "01060606060", date(2026, 5, 12), "스킨로직", "BDAY-J006"),
    ]

    with patch.object(sender, "send", side_effect=mock_kakao):
        sent_count = run_daily_batch(customers, today=today, mock=True)

    assert sent_count == 1
    assert customers[0].sent is True
    assert customers[1].sent is False
    assert customers[2].sent is False
    print("PASS test_journey_birthday_batch (1/3 due today)")


if __name__ == "__main__":
    test_journey_cart_abandoner_converts()
    test_journey_loyal_reviewer()
    test_journey_inactive_winback()
    test_journey_birthday_batch()
    print("\nAll E2E simulation tests passed.")
