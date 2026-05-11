"""
test_audit_log_immutability.py
-------------------------------
Tests for audit_logger.py hash-chain integrity.
Zero API calls. Uses tmp_path for file isolation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import pytest
from pathlib import Path
from src.audit_logger import (
    log_event,
    verify_chain,
    log_consent,
    log_breach,
    log_deletion,
    log_access_request,
    GENESIS_HASH,
)


def test_single_entry_chain_valid(tmp_path):
    log_path = tmp_path / "audit.jsonl"
    log_event("test_event", "system", "target_1", {"key": "value"}, log_path=log_path)
    valid, broken = verify_chain(log_path)
    assert valid is True
    assert broken == []


def test_multiple_entries_chain_valid(tmp_path):
    log_path = tmp_path / "audit.jsonl"
    for i in range(5):
        log_event("event", "system", f"target_{i}", {"seq": i}, log_path=log_path)
    valid, broken = verify_chain(log_path)
    assert valid is True
    assert broken == []


def test_tampered_entry_detected(tmp_path):
    log_path = tmp_path / "audit.jsonl"
    for i in range(3):
        log_event("event", "actor", f"target_{i}", {"i": i}, log_path=log_path)

    # Tamper: modify the second line
    lines = log_path.read_text(encoding="utf-8").splitlines()
    entry = json.loads(lines[1])
    entry["details"]["i"] = 999  # Change data without updating hash
    lines[1] = json.dumps(entry)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    valid, broken = verify_chain(log_path)
    assert valid is False
    assert len(broken) > 0


def test_empty_log_returns_valid(tmp_path):
    log_path = tmp_path / "empty.jsonl"
    log_path.touch()
    valid, broken = verify_chain(log_path)
    assert valid is True
    assert broken == []


def test_nonexistent_log_returns_valid(tmp_path):
    log_path = tmp_path / "nonexistent.jsonl"
    valid, broken = verify_chain(log_path)
    assert valid is True
    assert broken == []


def test_first_entry_uses_genesis_hash(tmp_path):
    log_path = tmp_path / "audit.jsonl"
    log_event("first_event", "system", "target", {}, log_path=log_path)
    entry = json.loads(log_path.read_text().strip())
    assert entry["prev_hash"] == GENESIS_HASH


def test_second_entry_links_to_first(tmp_path):
    log_path = tmp_path / "audit.jsonl"
    first = log_event("event_1", "system", "t1", {}, log_path=log_path)
    second = log_event("event_2", "system", "t2", {}, log_path=log_path)
    assert second["prev_hash"] == first["entry_hash"]


def test_consent_wrapper_logs_correctly(tmp_path):
    # Patch the default log_path via monkeypatching the module default
    import src.audit_logger as al
    original = al.AUDIT_LOG_PATH
    al.AUDIT_LOG_PATH = tmp_path / "audit.jsonl"
    try:
        entry = log_consent("user_001", ["personal_data_collection"], "2026-v1")
        assert entry["event_type"] == "consent_recorded"
        assert entry["actor"] == "user_001"
    finally:
        al.AUDIT_LOG_PATH = original


def test_breach_wrapper_includes_deadline(tmp_path):
    import src.audit_logger as al
    al.AUDIT_LOG_PATH = tmp_path / "audit.jsonl"
    entry = log_breach("HIGH", 500, ["이름", "전화번호"])
    assert "pipc_notification_deadline" in entry["details"]
    assert entry["event_type"] == "breach_detected"
    al.AUDIT_LOG_PATH = Path("data/audit.jsonl")


def test_deletion_event_logged(tmp_path):
    import src.audit_logger as al
    al.AUDIT_LOG_PATH = tmp_path / "audit.jsonl"
    entry = log_deletion("user_007", "admin", "열람청구 후 삭제")
    assert entry["event_type"] == "data_deleted"
    al.AUDIT_LOG_PATH = Path("data/audit.jsonl")


def test_access_request_logged(tmp_path):
    import src.audit_logger as al
    al.AUDIT_LOG_PATH = tmp_path / "audit.jsonl"
    entry = log_access_request("user_008", "열람")
    assert entry["event_type"] == "access_request"
    al.AUDIT_LOG_PATH = Path("data/audit.jsonl")
