"""
naver_seo_optimizer.py
Applies Naver Blog SEO rules to a blog post draft.

Naver SEO rules (2025-2026):
  - Title: 25-35 characters, primary keyword in first 15 chars
  - First 200 chars: must contain primary keyword (Naver uses this for snippet)
  - Keyword density: 1-3% for primary kw, natural usage
  - Headers: use H2/H3 (## / ###) -- Naver indexes these
  - Internal links: 2-3 minimum per post
  - Images: alt text in Korean with keyword
  - Meta description: 80-120 characters, include keyword + CTA
"""

import re
import sys
from typing import Optional

sys.stdout.reconfigure(encoding="utf-8")

NAVER_TITLE_MIN = 25
NAVER_TITLE_MAX = 35
NAVER_META_MIN = 80
NAVER_META_MAX = 120
KEYWORD_DENSITY_MIN = 0.01
KEYWORD_DENSITY_MAX = 0.03


def optimize_title(raw_title: str, primary_keyword: str, brand_name: str) -> str:
    """
    Returns a Naver-optimized title.
    Ensures: primary keyword in first 15 chars, total 25-35 chars.
    """
    # If keyword is already in title, check position
    title = raw_title.strip()
    kw = primary_keyword.strip()

    if kw.lower() not in title.lower():
        title = f"{kw} {title}"

    # Check keyword position -- should be in first 15 chars
    kw_pos = title.lower().find(kw.lower())
    if kw_pos > 15:
        # Move keyword to front
        title = f"{kw} -- {title}"

    # Trim to max length
    if len(title) > NAVER_TITLE_MAX:
        title = title[:NAVER_TITLE_MAX - 3] + "..."

    # Pad if too short (add brand)
    if len(title) < NAVER_TITLE_MIN and brand_name not in title:
        title = f"{title} | {brand_name}"

    return title


def generate_meta_description(draft: str, primary_keyword: str, brand_name: str) -> str:
    """
    Generates Naver-optimized meta description.
    80-120 chars, includes keyword + soft CTA.
    """
    # Extract first meaningful sentence
    clean = re.sub(r'^#{1,6}\s+', '', draft, flags=re.MULTILINE)
    clean = re.sub(r'\*{1,2}', '', clean)
    sentences = [s.strip() for s in re.split(r'[.!?。]', clean) if len(s.strip()) > 20]

    base = sentences[0] if sentences else f"{primary_keyword}에 대한 완벽 가이드"

    # Include keyword if missing
    if primary_keyword.lower() not in base.lower():
        base = f"{primary_keyword} - {base}"

    # Add CTA
    meta = f"{base}. {brand_name}에서 확인하세요."

    # Trim to range
    if len(meta) > NAVER_META_MAX:
        meta = meta[:NAVER_META_MAX - 1] + "."
    elif len(meta) < NAVER_META_MIN:
        meta = meta + f" {primary_keyword} 관련 정보를 확인하세요."
        meta = meta[:NAVER_META_MAX]

    return meta


def check_keyword_density(text: str, keyword: str) -> dict:
    """
    Checks keyword density in text.
    Returns density info and whether it is within Naver's recommended range.
    """
    words = text.split()
    total_words = len(words) if words else 1
    kw_count = len(re.findall(re.escape(keyword), text, re.IGNORECASE))
    density = kw_count / total_words

    return {
        "keyword": keyword,
        "count": kw_count,
        "total_words": total_words,
        "density": round(density, 4),
        "density_pct": f"{round(density * 100, 2)}%",
        "in_range": KEYWORD_DENSITY_MIN <= density <= KEYWORD_DENSITY_MAX,
        "recommendation": (
            "적정 범위" if KEYWORD_DENSITY_MIN <= density <= KEYWORD_DENSITY_MAX
            else ("키워드 추가 필요" if density < KEYWORD_DENSITY_MIN else "키워드 과다 -- 줄이기 권장")
        ),
    }


def add_image_alt_hints(draft: str, primary_keyword: str, brand_name: str) -> str:
    """
    Appends image alt text suggestions at the bottom of the post.
    (Naver Blog does not support automatic alt text injection via paste,
    so we provide a checklist for the client.)
    """
    hints = (
        f"\n\n---\n"
        f"**[이미지 업로드 시 alt 텍스트 권장]**\n"
        f"- 제품 사진: \"{brand_name} {primary_keyword} 제품\"\n"
        f"- 사용 전후 사진: \"{primary_keyword} 사용 전후 비교\"\n"
        f"- 성분 설명 이미지: \"{primary_keyword} 성분 설명\"\n"
    )
    return draft + hints


def run_naver_seo_pass(
    draft: str,
    raw_title: str,
    primary_keyword: str,
    brand_name: str,
) -> dict:
    """
    Full Naver SEO pass on a blog post.

    Returns:
        {
          "optimized_title": str,
          "meta_description": str,
          "keyword_density": dict,
          "optimized_draft": str,
          "seo_issues": list[str]
        }
    """
    title = optimize_title(raw_title, primary_keyword, brand_name)
    meta = generate_meta_description(draft, primary_keyword, brand_name)
    density = check_keyword_density(draft, primary_keyword)
    draft_with_alts = add_image_alt_hints(draft, primary_keyword, brand_name)

    issues = []
    if not density["in_range"]:
        issues.append(f"키워드 밀도 {density['density_pct']} -- {density['recommendation']}")
    if primary_keyword.lower() not in draft[:200].lower():
        issues.append("본문 첫 200자 내 주요 키워드 미포함")
    if draft.count("##") < 2:
        issues.append("H2 헤더 2개 미만 -- 네이버 인덱싱에 불리")

    return {
        "optimized_title": title,
        "meta_description": meta,
        "keyword_density": density,
        "optimized_draft": draft_with_alts,
        "seo_issues": issues,
    }


if __name__ == "__main__":
    sample = """# 세럼 사용법

비타민C 세럼은 아침 루틴에서 사용하는 것이 효과적입니다.
글로우랩 비타민C 세럼은 안정화 성분을 사용합니다.

## 사용 순서
토너 후, 에센스 전에 바릅니다.
"""
    result = run_naver_seo_pass(sample, "세럼 사용법", "비타민C 세럼", "글로우랩")
    print(f"Title: {result['optimized_title']}")
    print(f"Meta: {result['meta_description']}")
    print(f"Density: {result['keyword_density']}")
    if result["seo_issues"]:
        print(f"Issues: {result['seo_issues']}")
