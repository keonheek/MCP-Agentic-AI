"""
Latency tests -- p95 must be under 90 seconds.

Tests run against the Flask test client with mocked LLM calls.
Real latency is validated in integration testing (live API).
Here we verify the pipeline overhead (routing, idempotency check, logging)
adds minimal time on top of the (mocked) LLM call.

Pass criteria:
    - p50 pipeline overhead < 0.5s
    - p95 pipeline overhead < 1.0s (excluding mocked LLM time)
    - llm_router.get_models returns correct models within < 1ms
"""

import json
import statistics
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

_SERVICES_DIR = (
    Path(__file__).resolve().parents[3] / "services" / "automation"
)
if str(_SERVICES_DIR) not in sys.path:
    sys.path.insert(0, str(_SERVICES_DIR))

_PRODUCT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_PRODUCT_SRC) not in sys.path:
    sys.path.insert(0, str(_PRODUCT_SRC))

from speed_to_lead import app
from llm_router import get_models, requires_pipa_audit

# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------

def _fast_triage_mock():
    content = MagicMock()
    content.text = json.dumps({"category": "견적", "confidence": 0.9, "reason": "latency test"})
    resp = MagicMock()
    resp.content = [content]
    return resp


def _fast_reply_mock():
    content = MagicMock()
    content.text = "안녕하세요! 문의 주셔서 감사합니다."
    resp = MagicMock()
    resp.content = [content]
    return resp


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPipelineOverheadLatency(unittest.TestCase):
    """
    Measure pipeline overhead with instant-return LLM mocks.
    Each request exercises: idempotency check, triage, reply, Kakao send, Notion log.
    """

    N_REQUESTS = 30
    P95_OVERHEAD_LIMIT_S = 1.0  # pipeline code only, no real LLM
    P50_OVERHEAD_LIMIT_S = 0.5

    @patch("speed_to_lead.log_to_notion")
    @patch("speed_to_lead.send_kakao_reply")
    @patch("speed_to_lead._get_anthropic_client")
    def test_pipeline_overhead_p95(self, mock_get_client, mock_send, mock_log):
        mock_send.return_value = True
        mock_get_client.return_value.messages.create.side_effect = [
            item
            for _ in range(self.N_REQUESTS)
            for item in (_fast_triage_mock(), _fast_reply_mock())
        ]

        flask_client = app.test_client()
        latencies = []

        for i in range(self.N_REQUESTS):
            payload = {
                "userRequest": {
                    "user": {"id": f"latency_user_{i:04d}"},
                    "utterance": f"세럼 {i}개 구매 가격 알려주세요",
                },
                "bot": {"id": "bot_latency"},
            }
            t0 = time.perf_counter()
            resp = flask_client.post("/webhook/test-client", json=payload)
            elapsed = time.perf_counter() - t0
            latencies.append(elapsed)
            self.assertIn(resp.status_code, [200, 409], f"Unexpected status {resp.status_code} on request {i}")

        latencies.sort()
        p50 = latencies[int(len(latencies) * 0.50)]
        p95_idx = min(int(len(latencies) * 0.95), len(latencies) - 1)
        p95 = latencies[p95_idx]
        avg = statistics.mean(latencies)

        print(
            f"\nLatency profile (N={self.N_REQUESTS}, mocked LLM):\n"
            f"  avg={avg*1000:.1f}ms | p50={p50*1000:.1f}ms | p95={p95*1000:.1f}ms"
        )

        self.assertLess(
            p50, self.P50_OVERHEAD_LIMIT_S,
            f"p50 overhead {p50*1000:.1f}ms exceeds {self.P50_OVERHEAD_LIMIT_S*1000:.0f}ms limit",
        )
        self.assertLess(
            p95, self.P95_OVERHEAD_LIMIT_S,
            f"p95 overhead {p95*1000:.1f}ms exceeds {self.P95_OVERHEAD_LIMIT_S*1000:.0f}ms limit",
        )


class TestLLMRouterLatency(unittest.TestCase):
    """get_models must resolve in under 1ms (pure dict lookup)."""

    LIMIT_MS = 1.0
    N = 10000

    def test_get_models_is_fast(self):
        t0 = time.perf_counter()
        for _ in range(self.N):
            get_models("pro")
            get_models("lite")
            get_models("tier_p")
            get_models(None)
            get_models("unknown")
        elapsed_ms = (time.perf_counter() - t0) * 1000
        per_call_ms = elapsed_ms / (self.N * 5)
        print(f"\nllm_router.get_models: {per_call_ms:.4f}ms per call ({self.N*5} calls)")
        self.assertLess(per_call_ms, self.LIMIT_MS)


class TestLLMRouterCorrectness(unittest.TestCase):
    """get_models returns expected model IDs per tier."""

    def test_pro_reply_model(self):
        models = get_models("pro")
        self.assertEqual(models["reply"], "claude-sonnet-4-5")

    def test_lite_uses_haiku_for_reply(self):
        models = get_models("lite")
        self.assertEqual(models["reply"], "claude-haiku-4-5")

    def test_tier_p_uses_opus_for_reply(self):
        models = get_models("tier_p")
        self.assertEqual(models["reply"], "claude-opus-4-5")

    def test_all_tiers_use_haiku_for_triage(self):
        for tier in ["lite", "pro", "tier_p"]:
            with self.subTest(tier=tier):
                self.assertEqual(get_models(tier)["triage"], "claude-haiku-4-5")

    def test_unknown_tier_defaults_to_pro(self):
        models = get_models("enterprise")
        self.assertEqual(models, get_models("pro"))

    def test_none_tier_defaults_to_pro(self):
        models = get_models(None)
        self.assertEqual(models, get_models("pro"))

    def test_pipa_audit_flag(self):
        self.assertTrue(requires_pipa_audit("tier_p"))
        self.assertFalse(requires_pipa_audit("pro"))
        self.assertFalse(requires_pipa_audit("lite"))
        self.assertFalse(requires_pipa_audit(None))


if __name__ == "__main__":
    unittest.main(verbosity=2)
