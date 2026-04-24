"""
Layer 1: Claude/Anthropic 뉴스 수집
- Anthropic 공식 블로그 (RSS/페이지 파싱)
- HackerNews Claude/Anthropic/MCP 키워드
- Product Hunt Claude 관련 툴
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
INBOX_DIR = BASE_DIR / "data" / "inbox"


def fetch_anthropic_news() -> list[dict]:
    try:
        import httpx
    except ImportError:
        return []

    candidates = []
    urls = [
        "https://www.anthropic.com/news",
        "https://www.anthropic.com/research",
    ]

    for url in urls:
        try:
            resp = httpx.get(url, timeout=15, follow_redirects=True)
            html = resp.text
            # article-card 링크 추출
            article_urls = set(re.findall(r'href="(/news/[^"]+)"', html) +
                               re.findall(r'href="(/research/[^"]+)"', html))
            for path in list(article_urls)[:10]:
                full_url = f"https://www.anthropic.com{path}"
                title_match = re.search(rf'href="{re.escape(path)}"[^>]*>([^<]+)<', html)
                title = title_match.group(1).strip() if title_match else path
                candidates.append({
                    "id": full_url,
                    "url": full_url,
                    "title": title,
                    "source_platform": "anthropic_official",
                    "content_type": "claude_news",
                    "category": "claude_news",
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                })
        except Exception as e:
            print(f"[WARN] Anthropic {url} 수집 실패: {e}")

    return candidates


def fetch_hackernews_claude() -> list[dict]:
    try:
        import httpx
    except ImportError:
        return []

    try:
        # Algolia HN 검색 (공식 API)
        resp = httpx.get(
            "https://hn.algolia.com/api/v1/search_by_date",
            params={
                "query": "Claude OR Anthropic OR MCP",
                "tags": "story",
                "numericFilters": "points>30",
            },
            timeout=15,
        )
        hits = resp.json().get("hits", [])
        candidates = []
        for hit in hits[:15]:
            title = hit.get("title", "")
            if not any(kw in title.lower() for kw in ["claude", "anthropic", "mcp"]):
                continue
            candidates.append({
                "id": str(hit.get("objectID")),
                "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                "title": title,
                "points": hit.get("points", 0),
                "source_platform": "hackernews",
                "content_type": "claude_news",
                "category": "claude_news",
                "collected_at": datetime.now(timezone.utc).isoformat(),
            })
        return candidates
    except Exception as e:
        print(f"[WARN] HN Claude 검색 실패: {e}")
        return []


def run(date_str: str = None) -> str:
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    anthropic = fetch_anthropic_news()
    hn = fetch_hackernews_claude()

    seen = set()
    merged = []
    for item in anthropic + hn:
        key = item.get("url")
        if key and key not in seen:
            seen.add(key)
            merged.append(item)

    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    output_path = INBOX_DIR / f"{date_str}-claude-news.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print(f"[Layer1/Claude] {len(merged)}개 수집 → {output_path}")
    return str(output_path)


if __name__ == "__main__":
    run()
