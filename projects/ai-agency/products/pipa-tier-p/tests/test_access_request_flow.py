"""
test_access_request_flow.py
----------------------------
Tests for access_request.py (PIPA Art. 35, 36, 37, 37-2).
Zero API calls.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import datetime
import pytest
from pathlib import Path
from src.access_request import (
    receive_request,
    fulfill_access_request,
    generate_erasure_confirmation,
    generate_ai_explanation,
    get_overdue_requests,
    RequestType,
    RequestStatus,
    RESPONSE_DEADLINE_BUSINESS_DAYS,
)


def test_receive_request_creates_record(tmp_path):
    store = tmp_path / "requests.jsonl"
    req = receive_request(
        user_id="user_001",
        request_type=RequestType.ACCESS,
        details={"channel": "email", "message": "내 정보를 보고 싶습니다."},
        store_path=store,
    )
    assert store.exists()
    assert req.user_id == "user_001"
    assert req.request_type == RequestType.ACCESS
    assert req.request_id.startswith("REQ-")


def test_unverified_identity_sets_pending_status(tmp_path):
    store = tmp_path / "requests.jsonl"
    req = receive_request(
        user_id="user_002",
        request_type=RequestType.ERASURE,
        details={},
        identity_verified=False,
        store_path=store,
    )
    assert req.status == RequestStatus.PENDING_VERIFICATION


def test_verified_identity_sets_in_progress(tmp_path):
    store = tmp_path / "requests.jsonl"
    req = receive_request(
        user_id="user_003",
        request_type=RequestType.ACCESS,
        details={},
        identity_verified=True,
        store_path=store,
    )
    assert req.status == RequestStatus.IN_PROGRESS


def test_deadline_is_after_received_at(tmp_path):
    store = tmp_path / "requests.jsonl"
    req = receive_request(
        user_id="user_004",
        request_type=RequestType.RECTIFICATION,
        details={},
        store_path=store,
    )
    received = datetime.datetime.fromisoformat(req.received_at.rstrip("Z"))
    deadline = datetime.datetime.fromisoformat(req.deadline.rstrip("Z"))
    assert deadline > received


def test_deadline_approximately_10_business_days(tmp_path):
    store = tmp_path / "requests.jsonl"
    req = receive_request(
        user_id="user_005",
        request_type=RequestType.ACCESS,
        details={},
        store_path=store,
    )
    received = datetime.datetime.fromisoformat(req.received_at.rstrip("Z"))
    deadline = datetime.datetime.fromisoformat(req.deadline.rstrip("Z"))
    delta_days = (deadline - received).days
    # Should be approximately 10 business days (14+ calendar days)
    assert delta_days >= 10


def test_access_fulfillment_contains_user_data():
    user_data = {"이름": "김건희", "전화번호": "[PHONE-REDACTED]", "이메일": "[EMAIL-REDACTED]"}
    response = fulfill_access_request("REQ-ABCDEF123456", user_data)
    assert "김건희" in response
    assert "PIPA" in response or "제35조" in response


def test_erasure_confirmation_lists_fields():
    text = generate_erasure_confirmation(
        user_id="user_006",
        deleted_fields=["이름", "전화번호", "피부상태"],
    )
    assert "이름" in text
    assert "전화번호" in text
    assert "피부상태" in text


def test_ai_explanation_contains_decision_info():
    text = generate_ai_explanation(
        user_id="user_007",
        decision="마케팅 우선순위 High 분류",
        features_used=["문의 횟수", "구매 이력", "피부 타입"],
        score=0.87,
    )
    assert "0.87" in text
    assert "마케팅 우선순위 High" in text
    assert "37" in text  # Art. 37-2 reference


def test_overdue_requests_detected(tmp_path):
    store = tmp_path / "requests.jsonl"
    # Manually write an overdue request
    overdue_entry = {
        "request_id": "REQ-OVERDUE001",
        "user_id": "user_overdue",
        "request_type": "열람",
        "received_at": "2026-01-01T00:00:00Z",
        "deadline": "2026-01-15T00:00:00Z",  # Past
        "identity_verified": True,
        "status": "처리중",  # Not completed
        "details": {},
        "response": None,
        "responded_at": None,
    }
    with store.open("w", encoding="utf-8") as f:
        f.write(json.dumps(overdue_entry, ensure_ascii=False) + "\n")

    overdue = get_overdue_requests(store_path=store)
    assert len(overdue) == 1
    assert overdue[0]["request_id"] == "REQ-OVERDUE001"


def test_completed_request_not_in_overdue(tmp_path):
    store = tmp_path / "requests.jsonl"
    completed_entry = {
        "request_id": "REQ-DONE001",
        "user_id": "user_done",
        "request_type": "열람",
        "received_at": "2026-01-01T00:00:00Z",
        "deadline": "2026-01-15T00:00:00Z",
        "identity_verified": True,
        "status": "완료",
        "details": {},
        "response": "처리 완료",
        "responded_at": "2026-01-10T00:00:00Z",
    }
    with store.open("w", encoding="utf-8") as f:
        f.write(json.dumps(completed_entry, ensure_ascii=False) + "\n")

    overdue = get_overdue_requests(store_path=store)
    assert len(overdue) == 0


def test_all_request_types_supported():
    for rt in RequestType:
        assert rt.value is not None  # All enum members are valid


def test_request_persisted_to_file(tmp_path):
    store = tmp_path / "requests.jsonl"
    receive_request("user_persist", RequestType.DATA_PORTABILITY, {}, store_path=store)
    lines = store.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["request_type"] == "이전"
