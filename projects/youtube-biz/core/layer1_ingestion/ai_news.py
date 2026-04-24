"""
Layer 1: AI 채널 소스 수집
ProductHunt AI, HackerNews, 경쟁 채널 transcript 수집
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parents[3]
CONFIG_PATH = BASE_DIR / "config" / "sources.yaml"
INBOX_DIR = BASE_DIR / "data" / "inbox"


def load_sources() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)["sources"]["ai"]


def fetch_producthunt(config: dict) -> list[dict]:
    """ProductHunt AI 카테고리 신규 툴 수집"""
    try:
        import httpx
    except ImportError:
        print("[WARN] httpx 미설치. pip install httpx 필요.")
        return []

    query = """
    query {
      posts(order: VOTES, topic: "artificial-intelligence", first: 10) {
        edges {
          node {
            id name tagline url votesCount createdAt
            thumbnail { url }
          }
        }
      }
    }
    """
    try:
        resp = httpx.post(
            "https://api.producthunt.com/v2/api/graphql",
            json={"query": query},
            headers={"Authorization": f"Bearer {os.getenv('PRODUCTHUNT_TOKEN', '')}"},
            timeout=10,
        )
        data = resp.json()
        posts = data.get("data", {}).get("posts", {}).get("edges", [])
        candidates = []
        for edge in posts:
            node = edge.get("node", {})
            if node.get("votesCount", 0) < config.get("min_upvotes", 100):
                continue
            candidates.append({
                "id": node.get("id"),
                "url": node.get("url"),
                "title": node.get("name"),
                "description": node.get("tagline"),
                "votes": node.get("votesCount"),
                "source_platform": "producthunt",
                "content_type": "ai_tool",
                "collected_at": datetime.now(timezone.utc).isoformat(),
            })
        return candidates
    except Exception as e:
        print(f"[WARN] ProductHunt 수집 실패: {e}")
        return []


def fetch_hackernews(config: dict) -> list[dict]:
    """HackerNews AI 관련 상위 스토리 수집"""
    try:
        import httpx
    except ImportError:
        return []

    keywords = config.get("keywords", [])
    min_points = config.get("min_points", 50)

    try:
        resp = httpx.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        story_ids = resp.json()[:50]

        candidates = []
        for sid in story_ids:
            story_resp = httpx.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5)
            story = story_resp.json()
            if not story or story.get("type") != "story":
                continue
            title = story.get("title", "")
            if not any(kw.lower() in title.lower() for kw in keywords):
                continue
            if story.get("score", 0) < min_points:
                continue
            candidates.append({
                "id": str(sid),
                "url": story.get("url") or f"https://news.ycombinator.com/item?id={sid}",
                "title": title,
                "points": story.get("score"),
                "source_platform": "hackernews",
                "content_type": "ai_news",
                "collected_at": datetime.now(timezone.utc).isoformat(),
            })
            if len(candidates) >= 5:
                break
        return candidates
    except Exception as e:
        print(f"[WARN] HackerNews 수집 실패: {e}")
        return []


def run(date_str: str = None) -> str:
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    sources = load_sources()

    ph_candidates = fetch_producthunt(sources.get("producthunt", {}))
    hn_candidates = fetch_hackernews(sources.get("hacker_news", {}))

    all_candidates = ph_candidates + hn_candidates

    output_path = INBOX_DIR / f"{date_str}-ai-candidates.json"
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_candidates, f, ensure_ascii=False, indent=2)

    print(f"[Layer1] AI 후보 {len(all_candidates)}개 저장: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    run()
