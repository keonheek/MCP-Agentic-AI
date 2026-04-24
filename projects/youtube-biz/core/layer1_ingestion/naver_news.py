"""
Layer 1: 정치 채널 네이버 뉴스 수집
mcp__naver-search__search_news 를 직접 호출하는 대신,
Claude Code 환경 밖(크론)에서 실행할 수 있도록 Naver Search API HTTP 래퍼 제공
"""
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
INBOX_DIR = BASE_DIR / "data" / "inbox"

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")


def fetch_naver_news(query: str, display: int = 20) -> list[dict]:
    if not NAVER_CLIENT_ID:
        print("[WARN] NAVER_CLIENT_ID 미설정. .env 확인 필요.")
        return []

    encoded_query = urllib.parse.quote(query)
    url = f"https://openapi.naver.com/v1/search/news.json?query={encoded_query}&display={display}&sort=date"

    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", NAVER_CLIENT_ID)
    req.add_header("X-Naver-Client-Secret", NAVER_CLIENT_SECRET)

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            items = data.get("items", [])
            candidates = []
            for item in items:
                candidates.append({
                    "id": item.get("link"),
                    "url": item.get("link"),
                    "title": item.get("title", "").replace("<b>", "").replace("</b>", ""),
                    "description": item.get("description", "").replace("<b>", "").replace("</b>", ""),
                    "pub_date": item.get("pubDate"),
                    "source_platform": "naver_news",
                    "content_type": "politics_news",
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                })
            return candidates
    except Exception as e:
        print(f"[WARN] 네이버 뉴스 수집 실패: {e}")
        return []


def run(date_str: str = None) -> str:
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    queries = ["정치 오늘", "국회 최신", "대통령 뉴스", "여야 합의"]
    all_candidates = []
    seen_urls = set()

    for q in queries:
        items = fetch_naver_news(q, display=10)
        for item in items:
            if item["url"] not in seen_urls:
                seen_urls.add(item["url"])
                all_candidates.append(item)

    output_path = INBOX_DIR / f"{date_str}-politics-candidates.json"
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_candidates[:20], f, ensure_ascii=False, indent=2)

    print(f"[Layer1] 정치 뉴스 후보 {len(all_candidates[:20])}개 저장: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    run()
