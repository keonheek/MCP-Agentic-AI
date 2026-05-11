"""
Kakao rate limit and daily cap tests.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import src.kakao_sender as sender
from src.kakao_sender import MessageType, send, reset_daily_counts, KAKAO_DAILY_LIMIT_PER_CUSTOMER


def _basic_send(phone: str) -> dict | None:
    return send(
        phone=phone,
        template_code="TEST",
        template_body="안녕하세요 {{name}}님!",
        variables={"name": "테스트"},
        message_type=MessageType.INFO,
        flow_name="test_flow",
        mock=True,
    )


def test_daily_limit_enforced():
    reset_daily_counts()
    phone = "01011110001"
    results = []
    for _ in range(KAKAO_DAILY_LIMIT_PER_CUSTOMER + 2):
        results.append(_basic_send(phone))
    sent = [r for r in results if r is not None]
    blocked = [r for r in results if r is None]
    assert len(sent) == KAKAO_DAILY_LIMIT_PER_CUSTOMER
    assert len(blocked) == 2
    print(f"PASS test_daily_limit_enforced ({KAKAO_DAILY_LIMIT_PER_CUSTOMER} sent, 2 blocked)")


def test_reset_daily_counts():
    reset_daily_counts()
    phone = "01022220002"
    for _ in range(KAKAO_DAILY_LIMIT_PER_CUSTOMER):
        _basic_send(phone)
    reset_daily_counts()
    result = _basic_send(phone)
    assert result is not None
    print("PASS test_reset_daily_counts")


def test_different_phones_independent_limits():
    reset_daily_counts()
    phones = [f"0101111000{i}" for i in range(5)]
    for phone in phones:
        result = _basic_send(phone)
        assert result is not None, f"First send for {phone} should succeed"
    print("PASS test_different_phones_independent_limits")


def test_opted_out_customer_blocked():
    reset_daily_counts()
    phone = "01033330003"
    with __import__("unittest.mock", fromlist=["patch"]).patch.object(
        sender, "_is_opted_in", return_value=False
    ):
        result = _basic_send(phone)
    assert result is None
    print("PASS test_opted_out_customer_blocked")


if __name__ == "__main__":
    test_daily_limit_enforced()
    test_reset_daily_counts()
    test_different_phones_independent_limits()
    test_opted_out_customer_blocked()
    print("\nAll throttle tests passed.")
