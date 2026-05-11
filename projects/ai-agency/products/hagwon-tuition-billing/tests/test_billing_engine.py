"""
Tests for hagwon billing engine (dry-run mode).
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
os.environ.pop("TOSS_SECRET_KEY", None)

from billing_engine import charge_billing_key


def test_dry_run_when_no_key():
    result = charge_billing_key("dummy_key", 300000, "order_001", "김민준")
    assert result["status"] == "dry_run"
    assert result["amount"] == 300000
    assert result["customerName"] == "김민준"
