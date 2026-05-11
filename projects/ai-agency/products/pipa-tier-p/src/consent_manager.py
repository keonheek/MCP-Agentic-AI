"""
consent_manager.py
------------------
Cookie + form consent logic, version-tracked.
PIPA Art. 22 (Consent), Art. 15 (Lawful basis for collection).

2026 amendment: AI-assisted processing requires explicit, separate consent
when the purpose extends beyond the original collection purpose.
"""

import json
import hashlib
import datetime
from dataclasses import dataclass, asdict
from typing import Optional
from pathlib import Path


CONSENT_VERSION = "2026-v1"
CONSENT_STORE_PATH = Path("data/consents.jsonl")


@dataclass
class ConsentRecord:
    user_id: str
    consent_version: str
    timestamp: str
    ip_address: str
    purposes: list[str]  # e.g. ["marketing", "ai_processing", "third_party_transfer"]
    channel: str          # "web_form" | "kakao" | "sms"
    raw_signal: str       # "checkbox_checked" | "button_clicked" | "verbal"
    withdrawn: bool = False
    withdrawn_at: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    def fingerprint(self) -> str:
        payload = f"{self.user_id}:{self.consent_version}:{self.timestamp}:{','.join(self.purposes)}"
        return hashlib.sha256(payload.encode()).hexdigest()


REQUIRED_PURPOSES_TIER_P = [
    "personal_data_collection",       # Art. 15 - 개인정보 수집
    "ai_processing",                   # 2026 amendment - AI 처리 명세
    "third_party_transfer",            # Art. 17 - 제3자 제공 (Anthropic API 등)
    "overseas_transfer",               # Art. 28-2 - 국외 이전 (미국 서버)
    "marketing_communications",        # Art. 22 - 마케팅 수신 동의
    "retention_policy_acknowledgment", # Art. 21 - 보유기간 고지
]


def record_consent(
    user_id: str,
    purposes: list[str],
    channel: str,
    ip_address: str,
    raw_signal: str,
    store_path: Path = CONSENT_STORE_PATH,
) -> ConsentRecord:
    """
    Record a versioned consent event.
    Each consent is append-only (PIPA Art. 22 requires proof of consent).
    """
    record = ConsentRecord(
        user_id=user_id,
        consent_version=CONSENT_VERSION,
        timestamp=datetime.datetime.utcnow().isoformat() + "Z",
        ip_address=ip_address,
        purposes=purposes,
        channel=channel,
        raw_signal=raw_signal,
    )

    store_path.parent.mkdir(parents=True, exist_ok=True)
    with store_path.open("a", encoding="utf-8") as f:
        line = json.dumps(record.to_dict(), ensure_ascii=False)
        f.write(line + "\n")

    return record


def withdraw_consent(
    user_id: str,
    store_path: Path = CONSENT_STORE_PATH,
) -> bool:
    """
    Mark all consent records for user as withdrawn.
    PIPA Art. 37: 동의 철회권. Must be as easy as giving consent.
    Append a withdrawal record (immutable log pattern).
    """
    withdrawal = {
        "user_id": user_id,
        "event": "withdrawal",
        "consent_version": CONSENT_VERSION,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "withdrawn": True,
    }
    store_path.parent.mkdir(parents=True, exist_ok=True)
    with store_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(withdrawal, ensure_ascii=False) + "\n")
    return True


def get_latest_consent(
    user_id: str,
    store_path: Path = CONSENT_STORE_PATH,
) -> Optional[ConsentRecord]:
    """
    Return the most recent active consent for a user, or None if withdrawn/absent.
    Scans append-only log and resolves final state.
    """
    if not store_path.exists():
        return None

    records = []
    withdrawn = False

    with store_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if entry.get("user_id") != user_id:
                continue
            if entry.get("event") == "withdrawal":
                withdrawn = True
            else:
                records.append(entry)

    if withdrawn or not records:
        return None

    latest = records[-1]
    return ConsentRecord(**latest)


def validate_consent_completeness(record: ConsentRecord) -> list[str]:
    """
    Return list of missing required purposes for Tier P compliance.
    Empty list = compliant.
    """
    granted = set(record.purposes)
    required = set(REQUIRED_PURPOSES_TIER_P)
    missing = required - granted
    return sorted(missing)


def consent_is_current(record: ConsentRecord) -> bool:
    """
    Check if consent is for the current PIPA version.
    When PIPA version increments, all users must re-consent.
    """
    return record.consent_version == CONSENT_VERSION
