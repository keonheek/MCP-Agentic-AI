"""
Tests for dunning scheduler.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_dunning_d3_fires():
    due_date = datetime.now() - timedelta(days=3)
    unpaid_student = {
        "name": "박서연",
        "parent_phone": "01087654321",
        "tuition_amount": 250000,
        "due_date": due_date.isoformat(),
    }
    with patch("dunning_scheduler.get_unpaid_students", return_value=[unpaid_student]), \
         patch("dunning_scheduler.send_dunning_alimtalk", return_value={"status": "dry_run"}) as mock_send:
        from dunning_scheduler import run_dunning_check
        actions = run_dunning_check(datetime.now())
        assert any(a["action"] == "D3_dunning" for a in actions)
        mock_send.assert_called_once()


def test_dunning_no_action_for_current():
    due_date = datetime.now()
    unpaid_student = {
        "name": "이지훈",
        "parent_phone": "01099999999",
        "tuition_amount": 200000,
        "due_date": due_date.isoformat(),
    }
    with patch("dunning_scheduler.get_unpaid_students", return_value=[unpaid_student]), \
         patch("dunning_scheduler.send_dunning_alimtalk", return_value={"status": "dry_run"}):
        from dunning_scheduler import run_dunning_check
        actions = run_dunning_check(datetime.now())
        assert len(actions) == 0
