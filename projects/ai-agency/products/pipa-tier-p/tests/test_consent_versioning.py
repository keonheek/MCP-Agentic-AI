"""
test_consent_versioning.py
--------------------------
Tests for consent_manager.py.
Zero API calls. Uses tmp_path for file isolation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pathlib import Path
from src.consent_manager import (
    record_consent,
    withdraw_consent,
    get_latest_consent,
    validate_consent_completeness,
    consent_is_current,
    REQUIRED_PURPOSES_TIER_P,
    CONSENT_VERSION,
)


def test_record_consent_creates_file(tmp_path):
    store = tmp_path / "consents.jsonl"
    record = record_consent(
        user_id="user_001",
        purposes=["personal_data_collection", "marketing_communications"],
        channel="web_form",
        ip_address="127.0.0.1",
        raw_signal="checkbox_checked",
        store_path=store,
    )
    assert store.exists()
    assert record.user_id == "user_001"
    assert record.consent_version == CONSENT_VERSION


def test_consent_is_retrievable(tmp_path):
    store = tmp_path / "consents.jsonl"
    record_consent(
        user_id="user_002",
        purposes=["personal_data_collection"],
        channel="kakao",
        ip_address="192.168.1.1",
        raw_signal="button_clicked",
        store_path=store,
    )
    retrieved = get_latest_consent("user_002", store_path=store)
    assert retrieved is not None
    assert retrieved.user_id == "user_002"
    assert retrieved.channel == "kakao"


def test_withdrawal_nullifies_consent(tmp_path):
    store = tmp_path / "consents.jsonl"
    record_consent(
        user_id="user_003",
        purposes=["personal_data_collection"],
        channel="web_form",
        ip_address="10.0.0.1",
        raw_signal="checkbox_checked",
        store_path=store,
    )
    withdraw_consent("user_003", store_path=store)
    retrieved = get_latest_consent("user_003", store_path=store)
    assert retrieved is None


def test_missing_purposes_detected():
    from src.consent_manager import ConsentRecord
    import datetime
    record = ConsentRecord(
        user_id="user_004",
        consent_version=CONSENT_VERSION,
        timestamp=datetime.datetime.utcnow().isoformat() + "Z",
        ip_address="127.0.0.1",
        purposes=["personal_data_collection", "marketing_communications"],
        channel="web_form",
        raw_signal="checkbox_checked",
    )
    missing = validate_consent_completeness(record)
    assert "ai_processing" in missing
    assert "overseas_transfer" in missing
    assert "personal_data_collection" not in missing


def test_full_tier_p_consent_passes():
    from src.consent_manager import ConsentRecord
    import datetime
    record = ConsentRecord(
        user_id="user_005",
        consent_version=CONSENT_VERSION,
        timestamp=datetime.datetime.utcnow().isoformat() + "Z",
        ip_address="127.0.0.1",
        purposes=REQUIRED_PURPOSES_TIER_P,
        channel="web_form",
        raw_signal="checkbox_checked",
    )
    missing = validate_consent_completeness(record)
    assert missing == []


def test_consent_version_check():
    from src.consent_manager import ConsentRecord
    import datetime
    stale_record = ConsentRecord(
        user_id="user_006",
        consent_version="2024-v1",  # old version
        timestamp=datetime.datetime.utcnow().isoformat() + "Z",
        ip_address="127.0.0.1",
        purposes=REQUIRED_PURPOSES_TIER_P,
        channel="web_form",
        raw_signal="checkbox_checked",
    )
    assert not consent_is_current(stale_record)


def test_missing_user_returns_none(tmp_path):
    store = tmp_path / "consents.jsonl"
    result = get_latest_consent("nonexistent_user", store_path=store)
    assert result is None


def test_fingerprint_is_deterministic():
    from src.consent_manager import ConsentRecord
    record = ConsentRecord(
        user_id="user_007",
        consent_version=CONSENT_VERSION,
        timestamp="2026-01-01T00:00:00Z",
        ip_address="127.0.0.1",
        purposes=["personal_data_collection"],
        channel="web_form",
        raw_signal="checkbox_checked",
    )
    assert record.fingerprint() == record.fingerprint()


def test_multiple_users_isolated(tmp_path):
    store = tmp_path / "consents.jsonl"
    record_consent("alice", ["personal_data_collection"], "web_form", "1.1.1.1", "click", store_path=store)
    record_consent("bob", ["marketing_communications"], "kakao", "2.2.2.2", "click", store_path=store)
    withdraw_consent("alice", store_path=store)

    assert get_latest_consent("alice", store_path=store) is None
    bob = get_latest_consent("bob", store_path=store)
    assert bob is not None
    assert bob.user_id == "bob"
