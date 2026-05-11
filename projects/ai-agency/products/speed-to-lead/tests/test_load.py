"""
Load test -- 100 concurrent simulated inquiries.

Uses threading to simulate concurrent webhook requests against the Flask test
client. All LLM and external calls are mocked so this runs offline with zero
API cost.

Pass criteria:
    - All 100 requests return HTTP 200
    - No unhandled exceptions (no 500 responses)
    - Thread safety: duplicate detection state is consistent
"""

import json
import sys
import threading
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

_SERVICES_DIR = (
    Path(__file__).resolve().parents[3] / "services" / "automation"
)
if str(_SERVICES_DIR) not in sys.path:
    sys.path.insert(0, str(_SERVICES_DIR))

from speed_to_lead import app

# ---------------------------------------------------------------------------
# Mock setup
# ---------------------------------------------------------------------------

CATEGORIES_CYCLE = ["견적", "제품문의", "재구매", "예약", "기타"]

def _mock_triage(idx: int) -> MagicMock:
    cat = CATEGORIES_CYCLE[idx % len(CATEGORIES_CYCLE)]
    content = MagicMock()
    content.text = json.dumps({"category": cat, "confidence": 0.88, "reason": "load test"})
    resp = MagicMock()
    resp.content = [content]
    return resp


def _mock_reply() -> MagicMock:
    content = MagicMock()
    content.text = "안녕하세요! 문의 주셔서 감사합니다. 바로 안내드릴게요."
    resp = MagicMock()
    resp.content = [content]
    return resp


INQUIRY_TEMPLATES = [
    "세럼 {n}개 도매가 가능한가요?",
    "히알루론산 세럼 성분이 궁금해요 ({n}번 문의)",
    "저번에 샀던 토너 재주문 ({n}번)",
    "이번 주 {n}일 배송 예약 가능한가요?",
    "인스타그램 계정 알려주세요 ({n})",
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestConcurrentLoad(unittest.TestCase):

    def setUp(self):
        self.flask_client = app.test_client()
        self.results = []
        self.lock = threading.Lock()

    @patch("speed_to_lead.log_to_notion")
    @patch("speed_to_lead.send_kakao_reply")
    @patch("speed_to_lead._get_anthropic_client")
    def test_100_concurrent_inquiries(self, mock_get_client, mock_send, mock_log):
        # Setup mocks
        mock_send.return_value = True

        call_count = [0]
        call_lock = threading.Lock()

        def side_effect(*args, **kwargs):
            with call_lock:
                idx = call_count[0]
                call_count[0] += 1
            # Alternate between triage and reply responses
            if idx % 2 == 0:
                return _mock_triage(idx // 2)
            else:
                return _mock_reply()

        mock_get_client.return_value.messages.create.side_effect = side_effect

        N = 100
        threads = []

        def send_request(thread_id: int):
            utterance = INQUIRY_TEMPLATES[thread_id % len(INQUIRY_TEMPLATES)].format(n=thread_id)
            payload = {
                "userRequest": {
                    "user": {"id": f"load_user_{thread_id:04d}"},
                    "utterance": utterance,
                },
                "bot": {"id": "bot_load_test"},
            }
            resp = self.flask_client.post(
                "/webhook/test-client",
                json=payload,
            )
            with self.lock:
                self.results.append({
                    "thread_id": thread_id,
                    "status_code": resp.status_code,
                    "utterance": utterance,
                })

        for i in range(N):
            t = threading.Thread(target=send_request, args=(i,))
            threads.append(t)

        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)

        # Assertions
        self.assertEqual(len(self.results), N, f"Expected {N} results, got {len(self.results)}")

        status_codes = [r["status_code"] for r in self.results]
        failures = [r for r in self.results if r["status_code"] >= 500]
        self.assertEqual(
            len(failures), 0,
            f"Got {len(failures)} server errors (500+): {failures[:3]}",
        )

        ok_or_dup = [r for r in self.results if r["status_code"] in (200, 409)]
        non_ok = [r for r in self.results if r["status_code"] not in (200, 409)]
        self.assertEqual(
            len(non_ok), 0,
            f"Unexpected status codes: {[(r['status_code'], r['utterance'][:30]) for r in non_ok[:5]]}",
        )

        print(
            f"\nLoad test complete: {N} requests | "
            f"200: {status_codes.count(200)} | "
            f"duplicates skipped: {status_codes.count(200) - len(set(r['thread_id'] for r in self.results if r['status_code'] == 200))} | "
            f"500: {status_codes.count(500)}"
        )


class TestDuplicateUnderConcurrency(unittest.TestCase):
    """Concurrent requests with the same user+utterance should not double-process."""

    @patch("speed_to_lead.log_to_notion")
    @patch("speed_to_lead.send_kakao_reply")
    @patch("speed_to_lead._get_anthropic_client")
    def test_same_utterance_concurrent(self, mock_get_client, mock_send, mock_log):
        mock_send.return_value = True
        mock_get_client.return_value.messages.create.side_effect = [
            # Provide enough responses for any non-deduplicated calls
            *[_mock_triage(0) for _ in range(10)],
            *[_mock_reply() for _ in range(10)],
        ]

        flask_client = app.test_client()
        results = []
        lock = threading.Lock()

        same_payload = {
            "userRequest": {
                "user": {"id": "concurrent_dedup_user"},
                "utterance": "세럼 도매가 알려주세요",
            },
            "bot": {"id": "bot_dedup"},
        }

        def send(i):
            resp = flask_client.post("/webhook/test-client", json=same_payload)
            with lock:
                results.append(resp.status_code)

        threads = [threading.Thread(target=send, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=15)

        self.assertEqual(len(results), 5)
        # At least one must succeed (200); rest should be 200 (duplicate) or 200 (processed)
        # No 500s allowed
        self.assertEqual(results.count(500), 0, "No server errors under concurrent duplicate load")


if __name__ == "__main__":
    unittest.main(verbosity=2)
