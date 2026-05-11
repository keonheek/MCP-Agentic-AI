"""
Happy path tests for Speed-to-Lead pipeline.

All LLM calls are mocked -- zero API cost.
Tests the full pipeline logic: triage -> confidence gate -> reply -> log.
"""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add services/automation to path so speed_to_lead is importable
_SERVICES_DIR = (
    Path(__file__).resolve().parents[3] / "services" / "automation"
)
if str(_SERVICES_DIR) not in sys.path:
    sys.path.insert(0, str(_SERVICES_DIR))

from speed_to_lead import (
    CATEGORIES,
    CONFIDENCE_THRESHOLD,
    is_duplicate,
    process_inquiry,
    triage_inquiry,
    generate_reply,
)

# ---------------------------------------------------------------------------
# Shared mock helpers
# ---------------------------------------------------------------------------

MOCK_CONFIG = {
    "brand_name": "테스트 스킨",
    "brand_voice": "친근하고 전문적인 톤",
    "kakao_access_token": "fake_token",
    "kakao_channel_id": "fake_channel",
    "notion_token": None,
    "notion_db_id": None,
    "product_catalog": [
        {"name": "히알루론산 세럼", "description": "수분 공급", "price": "35,000원"},
    ],
    "faq": [
        {"q": "반품은 어떻게 하나요?", "a": "7일 이내 무료 반품 가능합니다."},
    ],
    "owner_kakao_user_key": None,
    "owner_phone": None,
}

def _mock_triage_response(category: str, confidence: float = 0.92) -> MagicMock:
    content = MagicMock()
    content.text = json.dumps({
        "category": category,
        "confidence": confidence,
        "reason": "테스트용 분류",
    })
    response = MagicMock()
    response.content = [content]
    return response


def _mock_reply_response(reply_text: str) -> MagicMock:
    content = MagicMock()
    content.text = reply_text
    response = MagicMock()
    response.content = [content]
    return response


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestTriageCategories(unittest.TestCase):
    """Each category is correctly returned from triage_inquiry."""

    @patch("speed_to_lead._get_anthropic_client")
    def _run_triage(self, utterance: str, expected_category: str, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.messages.create.return_value = _mock_triage_response(expected_category)
        result = triage_inquiry(utterance)
        self.assertEqual(result["category"], expected_category)
        self.assertGreater(result["confidence"], 0.0)

    def test_triage_returns_견적(self):
        self._run_triage("세럼 10개 도매가 가능한가요?", "견적")

    def test_triage_returns_제품문의(self):
        self._run_triage("히알루론산 세럼 성분이 궁금해요", "제품문의")

    def test_triage_returns_재구매(self):
        self._run_triage("저번에 샀던 토너 재주문하고 싶어요", "재구매")

    def test_triage_returns_예약(self):
        self._run_triage("금요일 배송 예약 가능한가요?", "예약")

    def test_triage_returns_기타(self):
        self._run_triage("인스타그램 계정 알려주세요", "기타")


class TestConfidenceGate(unittest.TestCase):
    """Low confidence triggers escalation, not a regular reply."""

    @patch("speed_to_lead.log_to_notion")
    @patch("speed_to_lead.send_kakao_reply")
    @patch("speed_to_lead.escalate_to_owner")
    @patch("speed_to_lead._get_anthropic_client")
    def test_low_confidence_escalates(
        self, mock_client, mock_escalate, mock_send, mock_log
    ):
        mock_client.return_value.messages.create.return_value = _mock_triage_response(
            "기타", confidence=0.30  # Below CONFIDENCE_THRESHOLD
        )
        mock_send.return_value = True

        result = process_inquiry(
            message_id="test_low_conf",
            user_key="user_low_conf",
            inquiry_text="...",
            config=MOCK_CONFIG,
        )

        self.assertTrue(result["escalated"])
        mock_escalate.assert_called_once()

    @patch("speed_to_lead.log_to_notion")
    @patch("speed_to_lead.send_kakao_reply")
    @patch("speed_to_lead._get_anthropic_client")
    def test_high_confidence_does_not_escalate(
        self, mock_client, mock_send, mock_log
    ):
        mock_client.return_value.messages.create.side_effect = [
            _mock_triage_response("견적", confidence=0.95),
            _mock_reply_response("안녕하세요! 도매 문의 주셔서 감사합니다."),
        ]
        mock_send.return_value = True

        result = process_inquiry(
            message_id="test_high_conf",
            user_key="user_high_conf",
            inquiry_text="세럼 도매가 알려주세요",
            config=MOCK_CONFIG,
        )

        self.assertFalse(result["escalated"])
        self.assertEqual(result["category"], "견적")


class TestReplyGeneration(unittest.TestCase):
    """generate_reply returns non-empty Korean text."""

    @patch("speed_to_lead._get_anthropic_client")
    def test_reply_is_non_empty(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.messages.create.return_value = _mock_reply_response(
            "안녕하세요! 세럼 도매가 문의 주셨군요. 담당자가 바로 연락드릴게요."
        )
        reply = generate_reply("세럼 도매가 알려주세요", "견적", MOCK_CONFIG)
        self.assertTrue(len(reply) > 0)

    @patch("speed_to_lead._get_anthropic_client")
    def test_reply_contains_korean(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.messages.create.return_value = _mock_reply_response(
            "안녕하세요! 문의해 주셔서 감사합니다."
        )
        reply = generate_reply("제품 정보 알려주세요", "제품문의", MOCK_CONFIG)
        has_korean = any("가" <= c <= "힣" for c in reply)
        self.assertTrue(has_korean, f"Expected Korean text in reply, got: {reply}")


class TestIdempotency(unittest.TestCase):
    """Same message_id processed twice is deduplicated."""

    def setUp(self):
        # Reset seen messages state for clean test
        from speed_to_lead import SEEN_MESSAGES_FILE
        if SEEN_MESSAGES_FILE.exists():
            import json as _json
            data = _json.loads(SEEN_MESSAGES_FILE.read_text(encoding="utf-8"))
            # Remove our test IDs if present
            data["ids"] = [id_ for id_ in data.get("ids", []) if not id_.startswith("idem_test_")]
            SEEN_MESSAGES_FILE.write_text(
                _json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )

    def test_first_call_not_duplicate(self):
        self.assertFalse(is_duplicate("idem_test_unique_001"))

    def test_second_call_is_duplicate(self):
        is_duplicate("idem_test_unique_002")  # first call
        self.assertTrue(is_duplicate("idem_test_unique_002"))  # second call


class TestFlaskWebhook(unittest.TestCase):
    """Flask routes return correct status codes."""

    def setUp(self):
        if str(_SERVICES_DIR) not in sys.path:
            sys.path.insert(0, str(_SERVICES_DIR))
        from speed_to_lead import app
        self.client = app.test_client()

    def test_health_returns_200(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "ok")

    def test_unknown_client_returns_404(self):
        payload = {"userRequest": {"user": {"id": "u1"}, "utterance": "테스트"}}
        resp = self.client.post(
            "/webhook/nonexistent-client-xyz",
            json=payload,
        )
        self.assertEqual(resp.status_code, 404)

    def test_empty_utterance_returns_400(self):
        payload = {"userRequest": {"user": {"id": "u1"}, "utterance": ""}}
        resp = self.client.post(
            "/webhook/test-client",
            json=payload,
        )
        self.assertEqual(resp.status_code, 400)

    def test_webhook_verify_get(self):
        resp = self.client.get(
            "/webhook/test-client?challenge=abc123",
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["challenge"], "abc123")


if __name__ == "__main__":
    unittest.main(verbosity=2)
