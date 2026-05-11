"""
naver_serp_check.py
Checks brand visibility on Naver search via WebSearch (read-only).

Design: This module builds search queries for manual or agent-mediated
Naver checks. It does NOT call Naver APIs directly (requires registration).
Instead, it formats queries suitable for WebSearch MCP or manual testing,
then scores the results based on the response text.

For automated use: pass the Naver search result text to parse_naver_result().
"""

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

NAVER_QUERY_TEMPLATES = [
    "{brand} 후기",
    "{brand} 사용 후기",
    "{brand} 효과",
    "{brand} 추천",
    "{keyword} 추천 {brand}",
]

NAVER_BLOG_SIGNALS = [
    "후기",
    "리뷰",
    "사용해봤어요",
    "써봤어요",
    "추천",
    "효과 있어요",
    "재구매",
]


def build_naver_queries(brand_name: str, keywords: list[str] = None) -> list[str]:
    """Returns Naver search query strings for brand visibility check."""
    queries = []
    for t in NAVER_QUERY_TEMPLATES:
        if "{keyword}" in t:
            if keywords:
                for kw in keywords[:2]:
                    queries.append(t.format(brand=brand_name, keyword=kw))
        else:
            queries.append(t.format(brand=brand_name))
    return queries


def parse_naver_result(brand_name: str, result_text: str) -> dict:
    """
    Parses a Naver search result page text (from WebSearch or manual copy-paste).
    Scores brand presence and blog/review signal quality.

    Returns:
        {
          "brand": str,
          "brand_mentions": int,
          "blog_signals": int,
          "naver_score": int (0-100),
          "has_official_blog": bool,
          "notes": str
        }
    """
    brand_lower = brand_name.lower()
    text_lower = result_text.lower()

    brand_mentions = len(re.findall(re.escape(brand_lower), text_lower))
    blog_signals = sum(1 for s in NAVER_BLOG_SIGNALS if s in result_text)

    has_official_blog = (
        "blog.naver.com" in result_text and brand_lower in text_lower
    )

    # Rough scoring: mentions + signal richness
    raw = min(brand_mentions * 10 + blog_signals * 5, 100)
    naver_score = min(raw + (20 if has_official_blog else 0), 100)

    notes = []
    if brand_mentions == 0:
        notes.append("브랜드 네이버 검색 노출 없음 -- 네이버 블로그 콘텐츠 긴급 필요")
    if not has_official_blog:
        notes.append("공식 네이버 블로그 미확인")
    if blog_signals < 3:
        notes.append("후기/리뷰 콘텐츠 부족")

    return {
        "brand": brand_name,
        "brand_mentions": brand_mentions,
        "blog_signals": blog_signals,
        "naver_score": naver_score,
        "has_official_blog": has_official_blog,
        "notes": " / ".join(notes) if notes else "네이버 노출 양호",
    }


def demo_parse(brand_name: str) -> dict:
    """Returns a zero-score result for brands with no data (for testing)."""
    return parse_naver_result(brand_name, "")


if __name__ == "__main__":
    brand = sys.argv[1] if len(sys.argv) > 1 else "글로우랩"
    queries = build_naver_queries(brand, ["비타민C 세럼", "수분크림"])
    print(f"Naver queries for '{brand}':")
    for q in queries:
        print(f"  - {q}")
