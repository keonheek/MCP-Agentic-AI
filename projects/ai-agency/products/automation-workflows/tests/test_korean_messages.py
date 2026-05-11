"""
Korean copy tests: verify templates render correctly and contain required Korean text.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kakao_sender import _render_template, _opt_out_footer
from src.flows.abandoned_cart import TEMPLATE_30MIN, TEMPLATE_72HR_DISCOUNT
from src.flows.review_request import TEMPLATE_REVIEW_REQUEST, TEMPLATE_IG_REPOST
from src.flows.restock_alert import TEMPLATE_RESTOCK
from src.flows.birthday_discount import TEMPLATE_BIRTHDAY
from src.flows.winback_inactive import TEMPLATE_TOUCH_1, TEMPLATE_TOUCH_2, TEMPLATE_TOUCH_3


def test_cart_30min_renders_korean():
    rendered = _render_template(TEMPLATE_30MIN, {
        "customer_name": "김민지",
        "product_name": "수분 토너",
    })
    assert "김민지" in rendered
    assert "수분 토너" in rendered
    assert "{{" not in rendered
    print("PASS test_cart_30min_renders_korean")


def test_cart_72hr_is_ad_type():
    assert "[광고]" in TEMPLATE_72HR_DISCOUNT
    print("PASS test_cart_72hr_is_ad_type")


def test_review_request_no_ad_label():
    assert "[광고]" not in TEMPLATE_REVIEW_REQUEST
    print("PASS test_review_request_no_ad_label")


def test_ig_repost_renders():
    rendered = _render_template(TEMPLATE_IG_REPOST, {
        "customer_name": "박지은",
        "brand_ig": "skinlogic_kr",
    })
    assert "@skinlogic_kr" in rendered
    assert "{{" not in rendered
    print("PASS test_ig_repost_renders")


def test_restock_renders_korean():
    rendered = _render_template(TEMPLATE_RESTOCK, {
        "customer_name": "정하은",
        "product_name": "수분 토너",
        "product_url": "https://brand.com/toner",
    })
    assert "재입고" in rendered
    assert "정하은" in rendered
    print("PASS test_restock_renders_korean")


def test_birthday_is_ad_type():
    assert "[광고]" in TEMPLATE_BIRTHDAY
    print("PASS test_birthday_is_ad_type")


def test_birthday_renders_korean():
    rendered = _render_template(TEMPLATE_BIRTHDAY, {
        "customer_name": "윤지호",
        "brand_name": "스킨로직",
        "discount_code": "BDAY15-XYZ",
        "start_date": "05월 18일",
        "expiry_date": "05월 19일",
    })
    assert "생일" in rendered
    assert "윤지호" in rendered
    assert "{{" not in rendered
    print("PASS test_birthday_renders_korean")


def test_winback_touch1_no_ad_label():
    assert "[광고]" not in TEMPLATE_TOUCH_1
    print("PASS test_winback_touch1_no_ad_label")


def test_winback_touch2_is_ad_type():
    assert "[광고]" in TEMPLATE_TOUCH_2
    print("PASS test_winback_touch2_is_ad_type")


def test_winback_touch3_is_ad_type():
    assert "[광고]" in TEMPLATE_TOUCH_3
    print("PASS test_winback_touch3_is_ad_type")


def test_opt_out_footer_present():
    footer = _opt_out_footer()
    assert "수신거부" in footer
    print("PASS test_opt_out_footer_present")


if __name__ == "__main__":
    test_cart_30min_renders_korean()
    test_cart_72hr_is_ad_type()
    test_review_request_no_ad_label()
    test_ig_repost_renders()
    test_restock_renders_korean()
    test_birthday_is_ad_type()
    test_birthday_renders_korean()
    test_winback_touch1_no_ad_label()
    test_winback_touch2_is_ad_type()
    test_winback_touch3_is_ad_type()
    test_opt_out_footer_present()
    print("\nAll Korean message tests passed.")
