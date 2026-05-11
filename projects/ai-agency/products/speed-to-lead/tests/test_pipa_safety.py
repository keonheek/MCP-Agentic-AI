"""
PIPA (개인정보 보호법) safety tests.

Verifies:
1. User keys are truncated before logging (no full PII stored)
2. Notion log is skipped gracefully when credentials are absent
3. Audit log fields are present for Tier P clients
4. Duplicate message detection prevents re-processing the same inquiry
5. Escalation fires when Kakao send fails (no silent drop)
"""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

_SERVICES_DIR = (
    Path(__file__).resolve().parents[3] / "services" / "automation"
)
if str(_SERVICES_DIR) not in sys.path:
    sys.path.insert(0, str(_SERVICES_DIR))

from speed_to_lead import is_duplicate, log_to_notion, process_inquiry

# Notion logger from the product layer
_PRODUCT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_PRODUCT_SRC) not in sys.path:
    sys.path.insert(0, str(_PRODUCT_SRC))

from notion_logger import log_inquiry as product_log_inquiry

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

BASE_CONFIG = {
    "brand_name": "퓨어스킨",
    "brand_voice": "친근한 톤",
    "kakao_access_token": "fake_token",
    "kakao_channel_id": "fake_channel",
    "notion_token": "ntn_fake_notion_token",
    "notion_db_id": "fake_db_id_12345",
    "product_catalog": [],
    "faq": [],
    "owner_kakao_user_key": "owner_key_abc",
    "owner_phone": None,
    "tier": "pro",
}

TIER_P_CONFIG = {**BASE_CONFIG, "tier": "tier_p"}


def _mock_triage(category: str = "견적", confidence: float = 0.92):
    content = MagicMock()
    content.text = json.dumps({"category": category, "confidence": confidence, "reason": "test"})
    response = MagicMock()
    response.content = [content]
    return response


def _mock_reply(text: str = "안녕하세요! 문의 주셔서 감사합니다."):
    content = MagicMock()
    content.text = text
    response = MagicMock()
    response.content = [content]
    return response


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestUserKeyTruncation(unittest.TestCase):
    """User keys must be truncated (not stored in full) in Notion logs."""

    @patch("speed_to_lead.NotionClient")
    def test_user_key_truncated_in_notion(self, mock_notion_cls):
        mock_notion = MagicMock()
        mock_notion_cls.return_value = mock_notion

        full_user_key = "kakao_user_id_very_long_string_12345678"
        log_to_notion(
            inquiry="세럼 가격 알려주세요",
            user_key=full_user_key,
            category="견적",
            confidence=0.9,
            reply="가격 문의 감사합니다.",
            escalated=False,
            eval_score=9.0,
            config=BASE_CONFIG,
        )

        call_args = mock_notion.pages.create.call_args
        properties = call_args[1]["properties"]
        stored_id = properties["고객ID"]["title"][0]["text"]["content"]

        self.assertNotEqual(stored_id, full_user_key, "Full user key must not be stored")
        self.assertIn("...", stored_id, "Truncated key must end with ...")
        self.assertLessEqual(len(stored_id), 20, "Stored ID should be short")


class TestNotionSkippedWhenNoCreds(unittest.TestCase):
    """Notion log silently skips when token or db_id is absent."""

    @patch("speed_to_lead.NotionClient")
    def test_no_notion_token_skips(self, mock_notion_cls):
        config_no_token = {**BASE_CONFIG, "notion_token": None}
        # Remove env fallback
        with patch("speed_to_lead.os.getenv", return_value=None):
            log_to_notion(
                inquiry="test",
                user_key="u1",
                category="기타",
                confidence=0.5,
                reply="감사합니다",
                escalated=False,
                eval_score=10.0,
                config=config_no_token,
            )
        mock_notion_cls.assert_not_called()

    @patch("speed_to_lead.NotionClient")
    def test_no_db_id_skips(self, mock_notion_cls):
        config_no_db = {**BASE_CONFIG, "notion_db_id": None}
        with patch("speed_to_lead.os.getenv", return_value=None):
            log_to_notion(
                inquiry="test",
                user_key="u1",
                category="기타",
                confidence=0.5,
                reply="감사합니다",
                escalated=False,
                eval_score=10.0,
                config=config_no_db,
            )
        mock_notion_cls.assert_not_called()


class TestTierPAuditFields(unittest.TestCase):
    """Tier P logs must include PII redaction flag and audit memo."""

    @patch("notion_client.Client")
    def test_tier_p_includes_pii_field(self, mock_notion_cls):
        mock_notion = MagicMock()
        mock_notion_cls.return_value = mock_notion

        product_log_inquiry(
            inquiry="세럼 도매가 알려주세요",
            user_key="u_tier_p_test",
            category="견적",
            confidence=0.9,
            reply="도매가 안내 드릴게요",
            escalated=False,
            eval_score=9.5,
            config=TIER_P_CONFIG,
            pii_redacted=True,
            audit_note="국외이전 고지 완료",
        )

        call_args = mock_notion.pages.create.call_args
        properties = call_args[1]["properties"]
        self.assertIn("PII제거여부", properties, "Tier P must log PII redaction field")
        self.assertTrue(properties["PII제거여부"]["checkbox"])
        self.assertIn("감사메모", properties)

    @patch("notion_client.Client")
    def test_pro_tier_excludes_pii_field(self, mock_notion_cls):
        mock_notion = MagicMock()
        mock_notion_cls.return_value = mock_notion

        product_log_inquiry(
            inquiry="세럼 가격 알려주세요",
            user_key="u_pro_test",
            category="견적",
            confidence=0.9,
            reply="가격 문의 감사합니다",
            escalated=False,
            eval_score=9.0,
            config=BASE_CONFIG,  # tier=pro
        )

        call_args = mock_notion.pages.create.call_args
        properties = call_args[1]["properties"]
        self.assertNotIn("PII제거여부", properties, "Pro tier must NOT log PII field")


class TestDuplicatePrevention(unittest.TestCase):
    """Same message processed twice must be idempotent at the webhook layer."""

    def test_duplicate_detection_works(self):
        msg_id = "pipa_test_dedup_unique_xyz_999"
        first = is_duplicate(msg_id)
        second = is_duplicate(msg_id)
        self.assertFalse(first, "First call must not be duplicate")
        self.assertTrue(second, "Second call must be duplicate")


class TestEscalationOnKakaoFailure(unittest.TestCase):
    """If Kakao send fails, owner escalation must fire."""

    @patch("speed_to_lead.log_to_notion")
    @patch("speed_to_lead.escalate_to_owner")
    @patch("speed_to_lead.send_kakao_reply")
    @patch("speed_to_lead._get_anthropic_client")
    def test_kakao_failure_triggers_escalation(
        self, mock_client, mock_send, mock_escalate, mock_log
    ):
        mock_client.return_value.messages.create.side_effect = [
            _mock_triage("견적", 0.95),
            _mock_reply("도매가 안내 드릴게요"),
        ]
        # Kakao send fails
        mock_send.return_value = False

        result = process_inquiry(
            message_id="pipa_kakao_fail_test_unique_001",
            user_key="user_kakao_fail",
            inquiry_text="세럼 도매가 알려주세요",
            config=BASE_CONFIG,
        )

        self.assertTrue(result["escalated"])
        mock_escalate.assert_called_once()
        escalate_args = mock_escalate.call_args[0]
        self.assertIn("API", escalate_args[1])  # reason mentions API failure


if __name__ == "__main__":
    unittest.main(verbosity=2)
