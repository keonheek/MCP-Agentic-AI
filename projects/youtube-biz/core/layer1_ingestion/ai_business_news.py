"""
Layer 1: AI 사업/스타트업/투자 뉴스 수집
- HackerNews AI 사업 키워드
- TechCrunch RSS (AI 카테고리)
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
INBOX_DIR = BASE_DIR / "data" / "inbox"

BUSINESS_KEYWORDS = [
    "funding", "acquisition", "IPO", "valuation", "Series A", "Series B",
    "AI startup", "AI investment", "AI company", "launches"
]


def fetch_hackernews_business() -> list[dict]:
    try:
        import httpx
    except ImportError:
        return []

    candidates = []
    try:
        for kw in BUSINESS_KEYWORDS[:5]:
            resp = httpx.get(
                "https://hn.algolia.com/api/v1/search_by_date",
                params={"query": f"{kw} AI", "tags": "story", "numericFilters": "points>50"},
                timeout=10,
            )
            hits = resp.json().get("hits", [])[:3]
            for hit in hits:
                title = hit.get("title", "")
                if "AI" not in title and "ai" not in title.lower():
                    continue
                candidates.append({
                    "id": str(hit.get("objectID")),
                    "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                    "title": title,
                    "points": hit.get("points", 0),
                    "source_platform": "hackernews",
                    "content_type": "ai_business",
                    "category": "ai_business",
                    "keyword": kw,
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                })
    except Exception as e:
        print(f"[WARN] HN 사업 뉴스 실패: {e}")
    return candidates


def fetch_techcrunch_ai() -> list[dict]:
    try:
        import httpx
    except ImportError:
        return []

    try:
        resp = httpx.get(
            "https://techcrunch.com/category/artificial-intelligence/feed/",
            timeout=15,
        )
        xml = resp.text
        items = re.findall(r'<item>(.*?)</item>', xml, re.DOTALL)
        candidates = []
        for item in items[:15]:
            title_match = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
            link_match = re.search(r'<link>(.*?)</link>', item)
            pubdate_match = re.search(r'<pubDate>(.*?)</pubDate>', item)
            if not (title_match and link_match):
                continue
            candidates.append({
                "id": link_match.group(1).strip(),
                "url": link_match.group(1).strip(),
                "title": title_match.group(1).strip(),
                "pub_date": pubdate_match.group(1).strip() if pubdate_match else "",
                "source_platform": "techcrunch",
                "content_type": "ai_business",
                "category": "ai_business",
                "collected_at": datetime.now(timezone.utc).isoformat(),
            })
        return candidates
    except Exception as e:
        print(f"[WARN] TechCrunch RSS 실패: {e}")
        return []


def run(date_str: str = None) -> str:
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    hn = fetch_hackernews_business()
    tc = fetch_techcrunch_ai()

    seen = set()
    merged = []
    for item in hn + tc:
        key = item.get("url")
        if key and key not in seen:
            seen.add(key)
            merged.append(item)

    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    output_path = INBOX_DIR / f"{date_str}-ai-business.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print(f"[Layer1/Biz] {len(merged)}개 수집 → {output_path}")
    return str(output_path)


if __name__ == "__main__":
    run()
