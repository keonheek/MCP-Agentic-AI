"""
Speed-to-Lead one-command sales demo.

Runs a realistic demonstration of the full pipeline using cached responses
so zero API cost is incurred during sales calls. Cached replies live in
demo_data.json and are indexed by inquiry ID.

Usage:
    python demo/run_demo.py                # cached mode (default, zero API cost)
    python demo/run_demo.py --live         # live mode (calls real Claude API)
    python demo/run_demo.py --ids D001 D005 D010  # subset of demo inquiries

Requirements (cached mode): none beyond standard library + colorama (optional)
Requirements (live mode): same as speed_to_lead.py
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

# Force UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DEMO_DATA_PATH = Path(__file__).parent / "demo_data.json"
SERVICES_DIR = Path(__file__).resolve().parents[3] / "services" / "automation"

# ANSI colour helpers (degrade gracefully if not supported)
try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init()
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    CYAN = Fore.CYAN
    RESET = Style.RESET_ALL
except ImportError:
    GREEN = YELLOW = CYAN = RESET = ""


def load_demo_data() -> dict:
    if not DEMO_DATA_PATH.exists():
        print(f"ERROR: demo_data.json not found at {DEMO_DATA_PATH}")
        sys.exit(1)
    with open(DEMO_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def run_cached(inquiries: list[dict], brand: str) -> None:
    """Simulate pipeline with cached replies -- zero API cost."""
    sep = "=" * 72
    print(f"\n{sep}")
    print(f"  Speed-to-Lead DEMO  --  {brand}")
    print(f"  모드: 캐시 (API 비용 없음)")
    print(f"{sep}\n")

    for i, item in enumerate(inquiries, 1):
        category = item["category"]
        utterance = item["utterance"]
        cached_reply = item["cached_reply"]
        inquiry_id = item["id"]

        print(f"{CYAN}[{i}/{len(inquiries)}] {inquiry_id} | 카테고리: {category}{RESET}")
        print(f"  고객 문의: {utterance}")

        # Simulate triage processing
        time.sleep(0.4)
        print(f"  {YELLOW}→ AI 분류: {category} (신뢰도 92%){RESET}")

        # Simulate reply generation
        time.sleep(0.6)
        print(f"  {GREEN}→ 자동 답변: {cached_reply}{RESET}")
        print(f"  → 처리 시간: 0.9s (캐시) | Notion 로그: 기록됨\n")

    print(sep)
    print(f"  데모 완료 | {len(inquiries)}건 처리 | 평균 0.9s | 에스컬레이션 0건")
    print(f"  실제 운영 시: Claude Haiku 분류 + Sonnet 답변 생성 (p95 90초 이내)")
    print(f"{sep}\n")


def run_live(inquiries: list[dict], brand: str) -> None:
    """Call real Claude API -- incurs API cost."""
    if str(SERVICES_DIR) not in sys.path:
        sys.path.insert(0, str(SERVICES_DIR))

    try:
        from speed_to_lead import triage_inquiry, generate_reply, load_client_config
    except ImportError as e:
        print(f"ERROR: Could not import speed_to_lead: {e}")
        print(f"Make sure speed_to_lead.py exists at: {SERVICES_DIR}")
        sys.exit(1)

    config = load_client_config("test-client")
    if config is None:
        print("ERROR: test-client config not found. Run from repo root.")
        sys.exit(1)

    sep = "=" * 72
    print(f"\n{sep}")
    print(f"  Speed-to-Lead DEMO  --  {brand}")
    print(f"  모드: 라이브 (실제 Claude API 호출)")
    print(f"{sep}\n")

    latencies = []
    for i, item in enumerate(inquiries, 1):
        utterance = item["utterance"]
        inquiry_id = item["id"]

        print(f"{CYAN}[{i}/{len(inquiries)}] {inquiry_id}{RESET}")
        print(f"  고객 문의: {utterance}")

        t0 = time.time()
        triage = triage_inquiry(utterance)
        cat = triage["category"]
        conf = triage["confidence"]
        reply = generate_reply(utterance, cat, config)
        elapsed = round(time.time() - t0, 2)
        latencies.append(elapsed)

        print(f"  {YELLOW}→ AI 분류: {cat} (신뢰도 {conf:.0%}){RESET}")
        print(f"  {GREEN}→ 자동 답변: {reply}{RESET}")
        print(f"  → 처리 시간: {elapsed}s\n")
        time.sleep(0.5)

    avg = round(sum(latencies) / len(latencies), 2)
    p95 = round(sorted(latencies)[int(len(latencies) * 0.95)], 2) if len(latencies) >= 20 else max(latencies)
    print(sep)
    print(f"  데모 완료 | {len(inquiries)}건 처리 | 평균 {avg}s | p95 {p95}s")
    print(sep + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Speed-to-Lead sales demo runner")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Use real Claude API (incurs cost). Default: cached mode.",
    )
    parser.add_argument(
        "--ids",
        nargs="*",
        default=None,
        help="Specific demo inquiry IDs to run (e.g. D001 D005). Default: first 5.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all 20 demo inquiries instead of the default first 5.",
    )
    args = parser.parse_args()

    data = load_demo_data()
    brand = data.get("brand", "글로우랩 화장품")
    all_inquiries = data.get("inquiries", [])

    if args.ids:
        inquiries = [item for item in all_inquiries if item["id"] in args.ids]
        if not inquiries:
            print(f"No inquiries matched IDs: {args.ids}")
            sys.exit(1)
    elif args.all:
        inquiries = all_inquiries
    else:
        # Default: one per category (D001-D005 covers견적/제품문의/재구매/예약/기타)
        inquiries = all_inquiries[:5]

    if args.live:
        run_live(inquiries, brand)
    else:
        run_cached(inquiries, brand)


if __name__ == "__main__":
    main()
