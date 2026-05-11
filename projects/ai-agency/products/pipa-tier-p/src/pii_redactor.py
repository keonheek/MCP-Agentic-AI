"""
pii_redactor.py
---------------
Redacts Korean PII patterns from logs, strings, and dicts.
PIPA Art. 24 (Unique identifiers), Art. 23 (Sensitive information).

Patterns covered:
- 주민등록번호 (RRN): 6-digit birth date + 7-digit suffix
- 전화번호: 010-XXXX-XXXX, 02-XXX-XXXX, 031-XXX-XXXX
- 이메일 주소
- 도로명/지번 주소 (시/도/구/동 pattern)
- 신용카드번호 (16-digit)
- 외국인등록번호 (similar to RRN)
- 계좌번호 (bank account)
- 생년월일 (standalone 6-digit YYMMDD)
"""

import re
from typing import Any


# -----------------------------------------------------------------------
# Compiled patterns
# -----------------------------------------------------------------------

_PATTERNS = {
    "rrn": re.compile(
        r"\b(\d{6})"          # 생년월일 6자리
        r"[-\s]?"
        r"(\d{7})\b"          # 뒤 7자리
    ),
    "phone_mobile": re.compile(
        r"\b(010|011|016|017|018|019)"
        r"[-\s]?"
        r"(\d{3,4})"
        r"[-\s]?"
        r"(\d{4})\b"
    ),
    "phone_landline": re.compile(
        r"\b(02|0[3-9]\d)"    # 서울 02 or 지역번호 03x~09x
        r"[-\s]?"
        r"(\d{3,4})"
        r"[-\s]?"
        r"(\d{4})\b"
    ),
    "email": re.compile(
        r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    ),
    "address": re.compile(
        r"(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)"
        r"[가-힣\s\d\-]+"
        r"(시|구|군|동|읍|면|리|로|길|번길)"
        r"[\s\d\-]*"
        r"(\d+동|\d+호|\d+층)?"
    ),
    "card_number": re.compile(
        r"\b(\d{4})"
        r"[-\s]?"
        r"(\d{4})"
        r"[-\s]?"
        r"(\d{4})"
        r"[-\s]?"
        r"(\d{4})\b"
    ),
    "bank_account": re.compile(
        r"\b\d{3,6}"           # 앞 3~6자리
        r"[-\s]?"
        r"\d{2,6}"
        r"[-\s]?"
        r"\d{2,6}\b"
    ),
    "birth_date_standalone": re.compile(
        r"\b(19|20)\d{2}"      # YYYY
        r"(0[1-9]|1[0-2])"    # MM
        r"(0[1-9]|[12]\d|3[01])\b"  # DD
    ),
}

_REPLACEMENTS = {
    "rrn":                    "[RRN-REDACTED]",
    "phone_mobile":           "[PHONE-REDACTED]",
    "phone_landline":         "[PHONE-REDACTED]",
    "email":                  "[EMAIL-REDACTED]",
    "address":                "[ADDRESS-REDACTED]",
    "card_number":            "[CARD-REDACTED]",
    "bank_account":           "[ACCOUNT-REDACTED]",
    "birth_date_standalone":  "[DOB-REDACTED]",
}

# Order matters: redact RRN before birth_date_standalone to avoid double-match
_ORDERED_KEYS = [
    "rrn",
    "phone_mobile",
    "phone_landline",
    "email",
    "address",
    "card_number",
    "bank_account",
    "birth_date_standalone",
]


# -----------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------

def redact_string(text: str, skip: list[str] | None = None) -> str:
    """
    Redact all Korean PII from a string.
    skip: list of pattern keys to skip (e.g. ["bank_account"]).
    """
    skip = skip or []
    for key in _ORDERED_KEYS:
        if key in skip:
            continue
        text = _PATTERNS[key].sub(_REPLACEMENTS[key], text)
    return text


def redact_dict(data: dict, skip: list[str] | None = None) -> dict:
    """
    Recursively redact PII from all string values in a dict.
    Non-string values are passed through unchanged.
    """
    result = {}
    for k, v in data.items():
        if isinstance(v, str):
            result[k] = redact_string(v, skip=skip)
        elif isinstance(v, dict):
            result[k] = redact_dict(v, skip=skip)
        elif isinstance(v, list):
            result[k] = redact_list(v, skip=skip)
        else:
            result[k] = v
    return result


def redact_list(items: list, skip: list[str] | None = None) -> list:
    """Recursively redact PII from a list."""
    result = []
    for item in items:
        if isinstance(item, str):
            result.append(redact_string(item, skip=skip))
        elif isinstance(item, dict):
            result.append(redact_dict(item, skip=skip))
        elif isinstance(item, list):
            result.append(redact_list(item, skip=skip))
        else:
            result.append(item)
    return result


def redact_log_line(line: str) -> str:
    """
    Safe wrapper for log-line redaction.
    Returns original line on any error (never raises in production).
    """
    try:
        return redact_string(line)
    except Exception:
        return "[LOG-REDACTION-ERROR]"


def contains_pii(text: str) -> bool:
    """Return True if text contains any detectable PII pattern."""
    for key in _ORDERED_KEYS:
        if _PATTERNS[key].search(text):
            return True
    return False


def scan_pii_types(text: str) -> list[str]:
    """Return list of PII types found in text (for audit logging)."""
    found = []
    for key in _ORDERED_KEYS:
        if _PATTERNS[key].search(text):
            found.append(key)
    return found
