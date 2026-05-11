"""
score_calculator.py
Combines AI visibility score + Naver score into a single GEO score (0-100).
Wraps and extends the scoring logic from projects/geo-agency/.

Weights:
  - AI visibility (ChatGPT/Claude proxy): 60%
  - Naver SERP presence: 40%
"""

import sys

sys.stdout.reconfigure(encoding="utf-8")

AI_WEIGHT = 0.60
NAVER_WEIGHT = 0.40

SCORE_BANDS = [
    (80, 100, "우수", "AI 검색과 네이버 모두 노출 양호. 유지 전략 권장."),
    (55, 79, "보통", "부분적 노출. 블로그 콘텐츠 강화로 상위권 진입 가능."),
    (30, 54, "미흡", "AI 인용 또는 네이버 노출 부족. 즉시 콘텐츠 전략 필요."),
    (0, 29, "위험", "AI 검색에서 브랜드 완전 비노출. 기초부터 GEO 전략 수립 필요."),
]


def calculate_geo_score(ai_score: int, naver_score: int) -> dict:
    """
    Returns combined GEO score and breakdown.

    Args:
        ai_score: 0-100 from ai_visibility_check.parse_responses()
        naver_score: 0-100 from naver_serp_check.parse_naver_result()

    Returns:
        {
          "geo_score": int,
          "ai_score": int,
          "naver_score": int,
          "band": str,
          "recommendation": str,
          "breakdown": dict
        }
    """
    ai_score = max(0, min(100, ai_score))
    naver_score = max(0, min(100, naver_score))

    geo_score = round(ai_score * AI_WEIGHT + naver_score * NAVER_WEIGHT)

    band_label = "위험"
    recommendation = ""
    for lo, hi, label, rec in SCORE_BANDS:
        if lo <= geo_score <= hi:
            band_label = label
            recommendation = rec
            break

    return {
        "geo_score": geo_score,
        "ai_score": ai_score,
        "naver_score": naver_score,
        "band": band_label,
        "recommendation": recommendation,
        "breakdown": {
            "ai_contribution": round(ai_score * AI_WEIGHT),
            "naver_contribution": round(naver_score * NAVER_WEIGHT),
            "ai_weight_pct": int(AI_WEIGHT * 100),
            "naver_weight_pct": int(NAVER_WEIGHT * 100),
        },
    }


def score_from_audit_results(ai_result: dict, naver_result: dict) -> dict:
    """
    Convenience function: accepts raw dicts from ai_visibility_check
    and naver_serp_check and returns final GEO score dict.
    """
    ai_score = ai_result.get("visibility_score", 0)
    naver_score = naver_result.get("naver_score", 0)
    combined = calculate_geo_score(ai_score, naver_score)
    combined["brand"] = ai_result.get("brand", naver_result.get("brand", "Unknown"))
    combined["ai_details"] = {
        "mentions": ai_result.get("mentions", 0),
        "total_responses": ai_result.get("total_responses", 0),
        "mention_rate": ai_result.get("mention_rate", 0.0),
    }
    combined["naver_details"] = {
        "brand_mentions": naver_result.get("brand_mentions", 0),
        "blog_signals": naver_result.get("blog_signals", 0),
        "has_official_blog": naver_result.get("has_official_blog", False),
        "notes": naver_result.get("notes", ""),
    }
    return combined


if __name__ == "__main__":
    # Quick smoke test
    sample = calculate_geo_score(ai_score=40, naver_score=20)
    print(f"GEO Score: {sample['geo_score']}/100 ({sample['band']})")
    print(f"Recommendation: {sample['recommendation']}")
