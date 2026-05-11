"""
test_breach_notification_timing.py
------------------------------------
Tests for breach_responder.py: severity, deadlines, notices.
Zero API calls.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import datetime
from src.breach_responder import (
    assess_severity,
    compute_deadlines,
    generate_pipc_notification,
    generate_individual_notice,
    run_breach_timeline,
    BreachEvent,
    Severity,
)


def _make_event(affected: int, data_types: list[str], breach_type: str = "unauthorized_access") -> BreachEvent:
    return BreachEvent(
        discovered_at=datetime.datetime.utcnow().isoformat() + "Z",
        breach_type=breach_type,
        affected_count=affected,
        data_types=data_types,
        systems_affected=["CRM DB"],
        suspected_cause="SQL 인젝션",
        containment_status="contained",
        discovered_by="내부 발견",
    )


# -----------------------------------------------------------------------
# Severity classification
# -----------------------------------------------------------------------

def test_small_breach_general_data_is_low():
    event = _make_event(50, ["이름", "이메일"])
    assert assess_severity(event) == Severity.LOW


def test_medium_breach():
    event = _make_event(500, ["이름", "전화번호"])
    assert assess_severity(event) == Severity.MEDIUM


def test_large_breach_is_high():
    event = _make_event(5_000, ["이름", "주소"])
    assert assess_severity(event) == Severity.HIGH


def test_very_large_breach_is_critical():
    event = _make_event(15_000, ["이름", "이메일"])
    assert assess_severity(event) == Severity.CRITICAL


def test_sensitive_data_small_count_is_high():
    event = _make_event(150, ["이름", "피부상태", "알레르기"])
    assert assess_severity(event) in (Severity.HIGH, Severity.CRITICAL)


def test_rrn_breach_always_high():
    event = _make_event(10, ["주민등록번호"])
    severity = assess_severity(event)
    assert severity in (Severity.HIGH, Severity.CRITICAL)


# -----------------------------------------------------------------------
# 72-hour deadline
# -----------------------------------------------------------------------

def test_pipc_deadline_is_72h_from_discovery():
    now = datetime.datetime.utcnow()
    event_time = now.isoformat() + "Z"
    deadlines = compute_deadlines(event_time)

    pipc_dl = datetime.datetime.fromisoformat(deadlines["pipc_notification_deadline"].rstrip("Z"))
    delta = pipc_dl - now
    # Should be approximately 72 hours
    assert 71 <= delta.total_seconds() / 3600 <= 73


def test_all_deadline_keys_present():
    deadlines = compute_deadlines(datetime.datetime.utcnow().isoformat() + "Z")
    required_keys = [
        "pipc_notification_deadline",
        "individual_notification_deadline",
        "internal_escalation_t0",
        "containment_target_t4h",
        "forensics_report_t7d",
        "post_incident_review_t30d",
    ]
    for key in required_keys:
        assert key in deadlines, f"Missing deadline key: {key}"


def test_forensics_deadline_is_7d():
    now = datetime.datetime.utcnow()
    deadlines = compute_deadlines(now.isoformat() + "Z")
    forensics_dl = datetime.datetime.fromisoformat(deadlines["forensics_report_t7d"].rstrip("Z"))
    delta = forensics_dl - now
    assert 6 <= delta.days <= 8


# -----------------------------------------------------------------------
# PIPC notification document
# -----------------------------------------------------------------------

def test_pipc_notification_contains_required_fields():
    event = _make_event(500, ["이름", "전화번호", "이메일"])
    doc = generate_pipc_notification(event, "테스트 주식회사", "123-45-67890")
    assert "PIPA 제34조" in doc or "Art. 34" in doc
    assert "테스트 주식회사" in doc
    assert "500" in doc
    assert "이름" in doc


def test_large_breach_pipc_notice_includes_public_notice_warning():
    event = _make_event(2_000, ["이름", "이메일"])
    doc = generate_pipc_notification(event, "회사명", "000-00-00000")
    assert "1,000명" in doc or "홈페이지" in doc


# -----------------------------------------------------------------------
# Individual notice
# -----------------------------------------------------------------------

def test_individual_email_notice_contains_key_elements():
    event = _make_event(200, ["이름", "전화번호"])
    notice = generate_individual_notice(event, "스킨케어 브랜드 A")
    assert "이름" in notice
    assert "전화번호" in notice


def test_sms_notice_is_short():
    event = _make_event(50, ["이메일"])
    notice = generate_individual_notice(event, "브랜드B", channel="sms")
    assert len(notice) <= 500  # SMS should be concise


# -----------------------------------------------------------------------
# Timeline
# -----------------------------------------------------------------------

def test_timeline_covers_72h():
    event = _make_event(100, ["이름"])
    timeline = run_breach_timeline(event)
    times = [item["t"] for item in timeline]
    assert "T+72h" in times
    assert "T+0h" in times


def test_large_breach_timeline_includes_public_notice():
    event = _make_event(1_500, ["이름", "이메일"])
    timeline = run_breach_timeline(event)
    actions = [item["action"] for item in timeline]
    assert any("홈페이지" in a or "공지" in a for a in actions)
