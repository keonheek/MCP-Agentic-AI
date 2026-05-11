"""
topic_discoverer.py
Discovers blog topics for Korean skincare brands.

Sources (read-only, no API calls in this module):
  1. Client keyword list (from client_config)
  2. Static seed topics by sub-category
  3. Competitor blog title patterns (passed in as text, scraped externally)

This module generates a prioritized topic queue suitable for
post_drafter.py. No WebSearch API calls here -- topic research
is done via the /1stmover skill or manual competitor scrape passed in.
"""

import sys
import json
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SKINCARE_SEED_TOPICS = {
    "ingredient_guides": [
        "비타민C 세럼 효과 제대로 보는 방법",
        "레티놀 처음 쓸 때 꼭 알아야 할 것들",
        "나이아신아마이드 피부 미백에 정말 효과 있을까",
        "히알루론산 vs 글리세린 수분 공급 차이",
        "판테놀 피부 진정 성분 완벽 정리",
    ],
    "routine_guides": [
        "민감성 피부를 위한 아침 스킨케어 루틴",
        "여름 피지 관리 스킨케어 순서",
        "겨울 건성 피부 수분 루틴 단계별 가이드",
        "30대 안티에이징 스킨케어 시작하는 법",
        "스킨케어 레이어링 순서 완전 정리",
    ],
    "product_comparisons": [
        "앰플 vs 세럼 차이 정리",
        "토너패드 vs 일반 토너 어떤 게 나을까",
        "선크림 PA+++ vs SPF50 어떻게 고를까",
        "화학적 자외선차단제 vs 물리적 자외선차단제",
        "수분크림 젤 타입 vs 크림 타입 피부별 선택법",
    ],
    "faq": [
        "화장품 유통기한 개봉 후 얼마나 쓸 수 있을까",
        "스킨케어 제품 냉장 보관해도 될까",
        "여드름 피부에 보습이 중요한 이유",
        "자외선차단제 실내에서도 발라야 할까",
        "각질 제거 얼마나 자주 해야 할까",
    ],
}


def get_topic_queue(
    client_config: dict,
    competitor_titles: list[str] = None,
    posts_needed: int = 4,
) -> list[dict]:
    """
    Returns a prioritized topic queue for the client.

    Args:
        client_config: Dict from client_config.load_client_config()
        competitor_titles: Optional list of competitor blog titles (scraped externally)
        posts_needed: How many topics to return

    Returns:
        List of dicts: [{"title": str, "category": str, "priority": int, "source": str}]
    """
    keywords = client_config.get("target_keywords", [])
    brand = client_config.get("brand_name", "브랜드")

    queue = []

    # Priority 1: keyword-anchored topics
    for kw in keywords:
        queue.append({
            "title": f"{kw} 완벽 가이드 -- {brand} 추천",
            "category": "keyword_anchor",
            "priority": 1,
            "source": "client_keywords",
        })

    # Priority 2: competitor gap topics (from external scrape)
    if competitor_titles:
        for title in competitor_titles[:posts_needed]:
            # Slightly reframe competitor titles
            queue.append({
                "title": f"{title} (더 깊은 분석)",
                "category": "competitor_gap",
                "priority": 2,
                "source": "competitor_scrape",
            })

    # Priority 3: seed topics padded to fill quota
    flat_seeds = []
    for cat, topics in SKINCARE_SEED_TOPICS.items():
        for t in topics:
            flat_seeds.append({"title": t, "category": cat, "priority": 3, "source": "seed"})

    queue.extend(flat_seeds)

    # Deduplicate by title (case-insensitive)
    seen = set()
    unique_queue = []
    for item in queue:
        key = item["title"].lower()
        if key not in seen:
            seen.add(key)
            unique_queue.append(item)

    # Sort by priority, return top N
    unique_queue.sort(key=lambda x: x["priority"])
    return unique_queue[:posts_needed]


def format_topic_queue_for_prompt(topic_queue: list[dict]) -> str:
    """Formats topic queue as a numbered list for LLM prompt injection."""
    lines = ["다음 달 블로그 포스트 주제 목록:"]
    for i, item in enumerate(topic_queue, 1):
        lines.append(f"{i}. {item['title']} [{item['category']}]")
    return "\n".join(lines)


if __name__ == "__main__":
    demo_config = {
        "brand_name": "글로우랩",
        "target_keywords": ["비타민C 세럼", "수분크림 추천"],
    }
    queue = get_topic_queue(demo_config, posts_needed=4)
    print(format_topic_queue_for_prompt(queue))
