"""
Integration tests for hagwon webhook handler.
Mocks external calls (OpenAI, Kakao, Notion).
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_webhook_requires_fields():
    """Missing fields should return 400."""
    with patch("webhook_handler.generate_alimtalk", return_value="테스트"), \
         patch("webhook_handler.send_alimtalk", return_value={"status": "dry_run"}), \
         patch("webhook_handler.log_to_notion", return_value=True):
        from webhook_handler import app
        client = app.test_client()
        resp = client.post("/webhook/emr", json={"event_type": "attendance"})
        assert resp.status_code == 400


def test_webhook_success():
    """Valid payload returns 200."""
    with patch("webhook_handler.generate_alimtalk", return_value="테스트 메시지"), \
         patch("webhook_handler.send_alimtalk", return_value={"status": "dry_run"}), \
         patch("webhook_handler.log_to_notion", return_value=True):
        from webhook_handler import app
        client = app.test_client()
        resp = client.post("/webhook/emr", json={
            "event_type": "attendance",
            "student_name": "김민준",
            "parent_phone": "01012345678",
            "details": {"status": "결석"},
        })
        assert resp.status_code == 200


def test_health_check():
    from webhook_handler import app
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
