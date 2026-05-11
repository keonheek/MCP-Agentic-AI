"""
Korean language edge case tests.

Covers: 욕설, 오타, 띄어쓰기 오류, 사투리, 초성만 입력, 영문 혼용, 아주 짧은 입력.
All LLM calls are mocked -- zero API cost.
"""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

_SERVICES_DIR = (
    Path(__file__).resolve().parents[3] / "services" / "automation"
)
if str(_SERVICES_DIR) not in sys.path:
    sys.path.insert(0, str(_SERVICES_DIR))

from speed_to_lead import triage_inquiry, CATEGORIES

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_client_with_response(category: str, confidence: float = 0.85):
    content = MagicMock()
    content.text = json.dumps({
        "category": category,
        "confidence": confidence,
        "reason": "edge case test",
    })
    response = MagicMock()
    response.content = [content]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = response
    return mock_client


EDGE_CASES = [
    # (label, utterance, expected_category, confidence_min)
    # 오타 (typos)
    ("오타_가격", "가결이 어떻게 되나요", "견적", 0.6),
    ("오타_배송", "배숑 언제 오나요", "예약", 0.6),
    ("오타_재구매", "전에샀던거 다시사고시퍼요", "재구매", 0.5),
    # 띄어쓰기 오류
    ("띄어쓰기_세럼가격", "세럼가격알려주세요", "견적", 0.7),
    ("띄어쓰기_재구매", "저번에샀던토너재주문하고싶어요", "재구매", 0.6),
    # 사투리
    ("사투리_경상", "이거 얼마씩이고?", "견적", 0.5),
    ("사투리_전라", "이거 갑이 얼마당가요?", "견적", 0.4),
    # 초성 / 매우 짧은 입력
    ("초성_ㅇ", "ㅇ", "기타", 0.0),
    ("단어_하나", "가격", "견적", 0.6),
    ("빈 문자 유사", "   ", "기타", 0.0),
    # 욕설 (should still categorize, not crash)
    ("욕설_포함", "씨발 세럼 왜 이렇게 비싸요?", "견적", 0.4),
    ("욕설_강도높음", "존나 배송 언제 와요?", "예약", 0.4),
    # 영문 혼용
    ("영문혼용_가격", "세럼 price 어떻게 되나요?", "견적", 0.7),
    ("영문혼용_order", "order 하고 싶은데 어떻게 하나요?", "재구매", 0.5),
    # 특수문자
    ("특수문자", "가격???? 얼마에요!!!!!", "견적", 0.7),
    # 아주 긴 문의
    ("긴문의", "안녕하세요 저는 화장품 소매상인데요 세럼이랑 토너 앰플 크림 아이크림 립밤 선크림 다 합쳐서 대량으로 구매하면 어떤 할인이 있나요 그리고 배송은 어떻게 되고 견본품도 받을 수 있나요 정기배송도 신청하고 싶은데 어떻게 하면 되나요", "견적", 0.6),
    # 자기소개만
    ("자기소개만", "저는 강남에서 뷰티샵 운영하고 있어요", "기타", 0.4),
    # 불만
    ("불만", "지난번에 산 제품 피부에 트러블 났어요 어떻게 할 건가요", "기타", 0.5),
    # 감사 인사
    ("감사인사", "감사해요 잘 쓸게요", "기타", 0.7),
    # 숫자만
    ("숫자만", "010-1234-5678", "기타", 0.3),
]


class TestKoreanEdgeCases(unittest.TestCase):
    """
    For each edge case, triage_inquiry must:
    1. Not raise an exception
    2. Return a dict with 'category' in CATEGORIES
    3. Return 'confidence' as a float in [0.0, 1.0]
    """

    def _assert_valid_triage(self, label: str, utterance: str, expected_category: str, confidence_min: float):
        with patch("speed_to_lead._get_anthropic_client") as mock_get_client:
            mock_get_client.return_value = _mock_client_with_response(
                expected_category, max(confidence_min, 0.01)
            )
            result = triage_inquiry(utterance)

        self.assertIn(
            result["category"], CATEGORIES,
            msg=f"[{label}] Category '{result['category']}' not in valid categories",
        )
        self.assertIsInstance(result["confidence"], float, msg=f"[{label}] confidence must be float")
        self.assertGreaterEqual(result["confidence"], 0.0, msg=f"[{label}] confidence < 0")
        self.assertLessEqual(result["confidence"], 1.0, msg=f"[{label}] confidence > 1")


# Dynamically create one test method per edge case
def _make_test(label, utterance, expected_category, confidence_min):
    def test_method(self):
        self._assert_valid_triage(label, utterance, expected_category, confidence_min)
    test_method.__name__ = f"test_{label}"
    return test_method


for _label, _utterance, _expected, _conf_min in EDGE_CASES:
    _test_fn = _make_test(_label, _utterance, _expected, _conf_min)
    setattr(TestKoreanEdgeCases, _test_fn.__name__, _test_fn)


class TestJsonParseRobustness(unittest.TestCase):
    """triage_inquiry must not crash even when LLM returns malformed JSON."""

    @patch("speed_to_lead._get_anthropic_client")
    def test_malformed_json_returns_기타(self, mock_get_client):
        content = MagicMock()
        content.text = "I cannot classify this."
        response = MagicMock()
        response.content = [content]
        mock_get_client.return_value.messages.create.return_value = response

        result = triage_inquiry("아무말이나 해볼게요")
        self.assertIn(result["category"], CATEGORIES)
        self.assertEqual(result["confidence"], 0.0)

    @patch("speed_to_lead._get_anthropic_client")
    def test_markdown_fenced_json(self, mock_get_client):
        content = MagicMock()
        content.text = '```json\n{"category": "견적", "confidence": 0.88, "reason": "price query"}\n```'
        response = MagicMock()
        response.content = [content]
        mock_get_client.return_value.messages.create.return_value = response

        result = triage_inquiry("가격 알려주세요")
        self.assertEqual(result["category"], "견적")
        self.assertAlmostEqual(result["confidence"], 0.88)


if __name__ == "__main__":
    unittest.main(verbosity=2)
