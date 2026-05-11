"""
audit_logger.py
---------------
Immutable, hash-chained audit log.
PIPA Art. 29 (Safety measures), Art. 34 (Breach notification obligations).

Each log entry contains a SHA-256 hash of the previous entry,
creating a tamper-evident chain. Any deletion or modification
breaks the chain and is detectable during audit.

Log entries are append-only JSONL (one JSON object per line).
"""

import json
import hashlib
import datetime
from pathlib import Path
from typing import Optional


AUDIT_LOG_PATH = Path("data/audit.jsonl")
GENESIS_HASH = "0" * 64  # Sentinel for first entry


# -----------------------------------------------------------------------
# Core
# -----------------------------------------------------------------------

def _compute_hash(entry: dict) -> str:
    """SHA-256 of canonical JSON string (sorted keys, no whitespace)."""
    canonical = json.dumps(entry, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _get_last_hash(log_path: Path) -> str:
    """Return hash of the last entry in the log, or GENESIS_HASH if empty."""
    if not log_path.exists() or log_path.stat().st_size == 0:
        return GENESIS_HASH
    last_line = None
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                last_line = line
    if last_line is None:
        return GENESIS_HASH
    entry = json.loads(last_line)
    return entry.get("entry_hash", GENESIS_HASH)


def log_event(
    event_type: str,
    actor: str,
    target: str,
    details: dict,
    log_path: Path = AUDIT_LOG_PATH,
) -> dict:
    """
    Append an immutable audit event.

    event_type: e.g. "consent_recorded", "data_access", "breach_detected",
                     "pii_redacted", "data_deleted", "access_request_fulfilled"
    actor:      user_id, system service name, or "SYSTEM"
    target:     the object being acted on (user_id, file path, table name)
    details:    arbitrary dict of context (PII already redacted before calling)
    """
    prev_hash = _get_last_hash(log_path)

    entry_body = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "actor": actor,
        "target": target,
        "details": details,
        "prev_hash": prev_hash,
    }

    entry_hash = _compute_hash(entry_body)
    entry = {**entry_body, "entry_hash": entry_hash}

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return entry


# -----------------------------------------------------------------------
# Verification
# -----------------------------------------------------------------------

def verify_chain(log_path: Path = AUDIT_LOG_PATH) -> tuple[bool, list[int]]:
    """
    Verify the entire audit log chain.
    Returns (is_valid, list_of_broken_line_numbers).
    An empty broken_lines list means the chain is intact.
    """
    if not log_path.exists():
        return True, []

    broken = []
    prev_hash = GENESIS_HASH

    with log_path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            stored_hash = entry.pop("entry_hash", None)
            claimed_prev = entry.get("prev_hash")

            if claimed_prev != prev_hash:
                broken.append(lineno)

            recomputed = _compute_hash(entry)
            if recomputed != stored_hash:
                broken.append(lineno)

            # Restore for next iteration
            prev_hash = stored_hash if stored_hash else recomputed

    return len(broken) == 0, broken


# -----------------------------------------------------------------------
# Convenience wrappers for common PIPA events
# -----------------------------------------------------------------------

def log_consent(user_id: str, purposes: list[str], version: str) -> dict:
    return log_event(
        event_type="consent_recorded",
        actor=user_id,
        target=user_id,
        details={"purposes": purposes, "consent_version": version},
    )


def log_data_access(actor: str, target_user: str, reason: str) -> dict:
    return log_event(
        event_type="data_access",
        actor=actor,
        target=target_user,
        details={"reason": reason},
    )


def log_breach(severity: str, affected_count: int, data_types: list[str]) -> dict:
    return log_event(
        event_type="breach_detected",
        actor="SYSTEM",
        target="BREACH",
        details={
            "severity": severity,
            "affected_users": affected_count,
            "data_types": data_types,
            "pipc_notification_deadline": _pipc_deadline(),
        },
    )


def log_deletion(user_id: str, actor: str, reason: str) -> dict:
    return log_event(
        event_type="data_deleted",
        actor=actor,
        target=user_id,
        details={"reason": reason},
    )


def log_access_request(user_id: str, request_type: str) -> dict:
    """PIPA Art. 35 - 본인정보 열람청구."""
    return log_event(
        event_type="access_request",
        actor=user_id,
        target=user_id,
        details={"request_type": request_type},
    )


# -----------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------

def _pipc_deadline() -> str:
    """72 hours from now, ISO format. PIPA Art. 34."""
    deadline = datetime.datetime.utcnow() + datetime.timedelta(hours=72)
    return deadline.isoformat() + "Z"
