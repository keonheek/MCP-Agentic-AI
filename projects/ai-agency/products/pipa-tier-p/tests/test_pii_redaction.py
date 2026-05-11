"""
test_pii_redaction.py
---------------------
Tests for pii_redactor.py using Korean PII patterns.
Zero API calls.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.pii_redactor import (
    redact_string,
    redact_dict,
    redact_list,
    contains_pii,
    scan_pii_types,
    redact_log_line,
)


# -----------------------------------------------------------------------
# 주민등록번호
# -----------------------------------------------------------------------

def test_redacts_rrn_with_dash():
    text = "고객 주민번호: 901215-1234567"
    result = redact_string(text)
    assert "901215" not in result
    assert "1234567" not in result
    assert "[RRN-REDACTED]" in result


def test_redacts_rrn_without_dash():
    text = "RRN: 8503251234567"
    result = redact_string(text)
    assert "8503251234567" not in result


# -----------------------------------------------------------------------
# 전화번호
# -----------------------------------------------------------------------

def test_redacts_mobile_phone_dash():
    text = "연락처: 010-1234-5678"
    result = redact_string(text)
    assert "010-1234-5678" not in result
    assert "[PHONE-REDACTED]" in result


def test_redacts_mobile_phone_no_dash():
    text = "전화: 01012345678"
    result = redact_string(text)
    assert "01012345678" not in result


def test_redacts_landline():
    text = "사무실: 02-555-1234"
    result = redact_string(text)
    assert "02-555-1234" not in result
    assert "[PHONE-REDACTED]" in result


# -----------------------------------------------------------------------
# 이메일
# -----------------------------------------------------------------------

def test_redacts_email():
    text = "이메일: user@example.com 로 연락주세요"
    result = redact_string(text)
    assert "user@example.com" not in result
    assert "[EMAIL-REDACTED]" in result


def test_redacts_korean_domain_email():
    text = "담당자: kim.keonhee@naver.com"
    result = redact_string(text)
    assert "kim.keonhee@naver.com" not in result


# -----------------------------------------------------------------------
# 주소
# -----------------------------------------------------------------------

def test_redacts_seoul_address():
    text = "주소: 서울특별시 강남구 테헤란로 123"
    result = redact_string(text)
    assert "[ADDRESS-REDACTED]" in result


def test_redacts_gyeonggi_address():
    text = "거주지: 경기도 성남시 분당구 판교로 456"
    result = redact_string(text)
    assert "[ADDRESS-REDACTED]" in result


# -----------------------------------------------------------------------
# 카드번호
# -----------------------------------------------------------------------

def test_redacts_card_number():
    text = "카드: 1234-5678-9012-3456"
    result = redact_string(text)
    assert "[CARD-REDACTED]" in result


def test_redacts_card_number_no_dash():
    text = "결제카드 1234567890123456 등록"
    result = redact_string(text)
    assert "1234567890123456" not in result


# -----------------------------------------------------------------------
# Dict / List redaction
# -----------------------------------------------------------------------

def test_redact_dict_recursive():
    data = {
        "name": "김건희",
        "phone": "010-9876-5432",
        "nested": {"email": "test@test.com"},
    }
    result = redact_dict(data)
    assert result["phone"] == "[PHONE-REDACTED]"
    assert result["nested"]["email"] == "[EMAIL-REDACTED]"
    assert result["name"] == "김건희"  # Name alone is not a PII pattern


def test_redact_list():
    items = ["연락처: 010-1111-2222", "이름: 박지성", "이메일: park@test.com"]
    result = redact_list(items)
    assert "[PHONE-REDACTED]" in result[0]
    assert "[EMAIL-REDACTED]" in result[2]


# -----------------------------------------------------------------------
# contains_pii / scan_pii_types
# -----------------------------------------------------------------------

def test_contains_pii_true():
    assert contains_pii("고객 전화: 010-1234-5678") is True


def test_contains_pii_false():
    assert contains_pii("안녕하세요, 주문 내역을 확인해주세요.") is False


def test_scan_pii_types_multiple():
    text = "전화: 010-1234-5678, 이메일: a@b.com"
    types = scan_pii_types(text)
    assert "phone_mobile" in types
    assert "email" in types


# -----------------------------------------------------------------------
# Edge cases
# -----------------------------------------------------------------------

def test_empty_string():
    assert redact_string("") == ""


def test_non_pii_string_unchanged():
    # Pure Korean text with no numeric patterns that could trigger PII regexes
    text = "배송이 완료되었습니다. 감사합니다."
    result = redact_string(text)
    assert result == text


def test_redact_log_line_never_raises():
    # Even malformed input should not raise
    result = redact_log_line("010-1234-5678 user@test.com 901215-1234567")
    assert "010-1234-5678" not in result
    assert "user@test.com" not in result
