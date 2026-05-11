"""
Unit tests for Kakao Alimtalk sender (dry-run mode).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import os
os.environ.pop("KAKAO_ALIMTALK_API_KEY", None)
os.environ.pop("MAKE_KAKAO_WEBHOOK_URL", None)

from kakao_sender import send_alimtalk


def test_dry_run_when_no_keys(capsys):
    result = send_alimtalk("01012345678", "테스트 메시지입니다.")
    assert result["status"] == "dry_run"
    captured = capsys.readouterr()
    assert "DRY RUN" in captured.out
