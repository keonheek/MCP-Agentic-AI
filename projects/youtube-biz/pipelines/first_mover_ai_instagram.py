"""
First Mover AI — Instagram 캐러셀 파이프라인
Remote cron 07:00 KST (평일): 5개 캐러셀 텍스트 초안 생성

- Claude 뉴스 2개
- AI 사업 뉴스 2개
- AI 시사/트렌드 1개

출력: channels/first-mover-ai/drafts/instagram/YYYY-MM-DD-carousels.json
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))


def _notify_activepieces(event: str, payload: dict):
    """POST to Activepieces webhook if ACTIVEPIECES_WEBHOOK_INSTAGRAM is set in .env."""
    url = os.environ.get("ACTIVEPIECES_WEBHOOK_INSTAGRAM", "")
    if not url:
        return
    try:
        import urllib.request
        body = json.dumps({"event": event, **payload}).encode()
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass  # Non-blocking — pipeline runs regardless

from core.layer1_ingestion.claude_news import run as ingest_claude
from core.layer1_ingestion.ai_business_news import run as ingest_business
from core.layer1_ingestion.ai_news import run as ingest_ai_trends
from core.layer2_intelligence.ranker import score_candidates
from core.layer2_intelligence.script_generator import run_instagram


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def run():
    date_str = datetime.now().strftime("%Y-%m-%d")
    log("First Mover AI Instagram 파이프라인 시작")

    # Layer 1
    claude_path = ingest_claude(date_str)
    biz_path = ingest_business(date_str)
    trends_path = ingest_ai_trends(date_str)

    with open(claude_path, encoding="utf-8") as f:
        claude_cands = json.load(f)
    with open(biz_path, encoding="utf-8") as f:
        biz_cands = json.load(f)
    with open(trends_path, encoding="utf-8") as f:
        trends_cands = json.load(f)

    log(f"  수집: Claude {len(claude_cands)} / Biz {len(biz_cands)} / Trends {len(trends_cands)}")

    # Layer 2: 각 카테고리 채점 → top N
    top_claude = score_candidates(claude_cands, "first_mover_ai_instagram_claude", top_n=2)
    top_biz = score_candidates(biz_cands, "first_mover_ai_instagram_business", top_n=2)
    top_trends = score_candidates(trends_cands, "first_mover_ai_instagram_trends", top_n=1)

    log(f"  선정: Claude {len(top_claude)} / Biz {len(top_biz)} / Trends {len(top_trends)}")

    # Layer 2: 캐러셀 5개 생성
    output_path = run_instagram(top_claude, top_biz, top_trends, date_str)
    log(f"파이프라인 완료: {output_path}")
    _notify_activepieces("instagram_carousels", {"output_path": str(output_path), "date": date_str})
    return output_path


if __name__ == "__main__":
    run()
