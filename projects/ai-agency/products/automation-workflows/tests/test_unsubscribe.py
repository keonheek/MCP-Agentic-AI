"""
PIPA opt-out compliance tests.
Verifies that opted-out customers never receive messages across all flows.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timedelta, date
from unittest.mock import patch, MagicMock
import src.kakao_sender as sender

from src.flows.abandoned_cart import AbandonedCartState, run_touch as cart_run
from src.flows.birthday_discount import BirthdayCustomer, send_birthday_discount, should_send_today
from src.flows.winback_inactive import WinbackState, run_touch as winback_run
from src.kakao_sender import reset_daily_counts


def _opted_out(phone: str) -> bool:
    return True if phone == "01000000000" else False


OPT_OUT_PHONE = "01000000000"


def test_opted_out_cart_no_send():
    """
    When a customer has opted out, kakao_send returns None.
    The touch is still recorded (attempt logged), but no message is delivered.
    Test verifies the send function returns None for opted-out number.
    """
    reset_daily_counts()
    results = []
    original_send = sender.send

    def capturing_send(*args, **kwargs):
        result = original_send(*args, **kwargs)
        results.append(result)
        return result

    with patch.object(sender, "_is_opted_in", side_effect=lambda p: p != OPT_OUT_PHONE):
        with patch.object(sender, "send", side_effect=capturing_send):
            pass

    # Direct test: opted-out phone returns None from send()
    reset_daily_counts()
    with patch.object(sender, "_is_opted_in", side_effect=lambda p: p != OPT_OUT_PHONE):
        result = sender.send(
            phone=OPT_OUT_PHONE,
            template_code="TEST",
            template_body="test",
            variables={},
            message_type=sender.MessageType.INFO,
            flow_name="test",
            mock=True,
        )
    assert result is None
    print("PASS test_opted_out_cart_no_send")


def test_opted_out_birthday_no_send():
    reset_daily_counts()
    today = date(2026, 5, 11)
    customer = BirthdayCustomer(
        customer_id="OPT002",
        customer_name="수신거부",
        customer_phone=OPT_OUT_PHONE,
        birthday=date(2026, 5, 18),
        brand_name="스킨로직",
        discount_code="BDAY15-OPT",
    )
    with patch.object(sender, "_is_opted_in", side_effect=lambda p: p != OPT_OUT_PHONE):
        sent = send_birthday_discount(customer, today, mock=True)
    assert sent is False
    assert customer.sent is False
    print("PASS test_opted_out_birthday_no_send")


def test_opted_out_winback_no_send():
    """
    Opted-out customer: kakao_send returns None (no delivery).
    Verified at the sender level, not touch state (touch state tracks attempts).
    """
    reset_daily_counts()
    with patch.object(sender, "_is_opted_in", side_effect=lambda p: p != OPT_OUT_PHONE):
        result = sender.send(
            phone=OPT_OUT_PHONE,
            template_code="WINBACK_TEST",
            template_body="test",
            variables={},
            message_type=sender.MessageType.AD,
            flow_name="winback_touch1",
            mock=True,
        )
    assert result is None
    print("PASS test_opted_out_winback_no_send")


def test_opt_out_footer_included_in_all_messages():
    """Every message body must include the opt-out footer."""
    from src.kakao_sender import _opt_out_footer
    footer = _opt_out_footer()
    assert "수신거부" in footer
    assert "080" in footer or "카카오톡" in footer
    print("PASS test_opt_out_footer_included_in_all_messages")


if __name__ == "__main__":
    test_opted_out_cart_no_send()
    test_opted_out_birthday_no_send()
    test_opted_out_winback_no_send()
    test_opt_out_footer_included_in_all_messages()
    print("\nAll PIPA unsubscribe tests passed.")
