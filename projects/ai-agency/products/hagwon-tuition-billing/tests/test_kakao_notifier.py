"""
Tests for Kakao notifier (dry-run).
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
os.environ.pop("KAKAO_ALIMTALK_API_KEY", None)
os.environ.pop("MAKE_KAKAO_WEBHOOK_URL", None)

from kakao_notifier import send_billing_result, send_dunning_alimtalk


def test_success_notification_dry_run(capsys):
    result = send_billing_result("01012345678", "김민준", 300000, "success")
    assert result["status"] == "dry_run"
    captured = capsys.readouterr()
    assert "정상 결제" in captured.out


def test_dunning_d3_dry_run(capsys):
    result = send_dunning_alimtalk("01012345678", "박서연", 250000, "D3")
    assert result["status"] == "dry_run"
    captured = capsys.readouterr()
    assert "3일" in captured.out
