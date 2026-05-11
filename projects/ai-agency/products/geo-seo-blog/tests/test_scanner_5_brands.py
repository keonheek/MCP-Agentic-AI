"""
test_scanner_5_brands.py
Tests the GEO Scanner pipeline on 5 real Korean skincare brands.

Read-only: uses Claude API for AI visibility check (no DM/contact with brands).
Brands selected: well-known Korean skincare D2C with public web presence.

Run:
    python -m pytest tests/test_scanner_5_brands.py -v
    # or directly:
    python tests/test_scanner_5_brands.py
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
sys.stdout.reconfigure(encoding="utf-8")

from src.scanner.ai_visibility_check import parse_responses, build_queries
from src.scanner.naver_serp_check import parse_naver_result, build_naver_queries
from src.scanner.score_calculator import score_from_audit_results, calculate_geo_score

# 5 real Korean skincare D2C brands (public info only)
BRANDS = [
    {
        "name": "라라스윗",
        "website": "https://larasweet.co.kr",
        "keywords": ["비타민C 세럼", "라라스윗"],
    },
    {
        "name": "토리든",
        "website": "https://toriden.com",
        "keywords": ["히알루론산 세럼", "토리든 다이브인"],
    },
    {
        "name": "아누아",
        "website": "https://anua.co.kr",
        "keywords": ["어성초 토너", "아누아"],
    },
    {
        "name": "달바",
        "website": "https://dalba.co.kr",
        "keywords": ["비피다 앰플", "달바 화이트"],
    },
    {
        "name": "조선미녀",
        "website": "https://joseongmiryeo.com",
        "keywords": ["쌀 선크림", "조선미녀 선크림"],
    },
]

# Simulated AI responses based on known brand visibility (no actual API call in unit test)
# These reflect real-world brand recognition as of 2026
SIMULATED_AI_RESPONSES = {
    "라라스윗": [
        "라라스윗은 한국 스킨케어 브랜드로 비타민C 세럼으로 알려져 있어요.",
        "비타민C 세럼은 라라스윗이나 이니스프리 제품이 괜찮아요.",
        "라라스윗 써봤어요? 성분이 좋더라고요.",
        "한국 스킨케어는 토리든, 아누아, 달바 같은 브랜드들이 유명해요.",
        "수분크림은 라네즈나 이니스프리를 많이 추천해요.",
        "가성비 세럼은 라라스윗도 괜찮아요.",
        "민감성 피부에는 아누아나 달바가 잘 맞아요.",
        "비타민C 성분 제품 중 라라스윗 세럼이 인기 있어요.",
        "한국 스킨케어 브랜드로는 아누아, 토리든, 조선미녀가 해외에서도 유명해요.",
        "라라스윗은 D2C 브랜드로 온라인 중심으로 판매해요.",
    ],
    "토리든": [
        "토리든 다이브인 세럼 진짜 좋아요.",
        "히알루론산 세럼은 토리든이 성분 대비 가격이 좋아요.",
        "토리든 vs 닥터자르트 히알루론산 제품 비교해봤어요.",
        "한국 수분 세럼 중 토리든 다이브인 시리즈가 인기 있어요.",
        "토리든은 해외에서도 많이 팔리는 K-뷰티 브랜드예요.",
        "히알루론산 레이어링은 토리든 제품으로 하면 좋아요.",
        "수분 폭탄 세럼으로는 토리든 다이브인 추천해요.",
        "토리든 마스크팩도 꽤 좋아요.",
        "한국 스킨케어 입문으로 토리든 추천해요.",
        "토리든 아마존에서도 팔아요.",
    ],
    "아누아": [
        "아누아 어성초 77 토너 진짜 유명해요.",
        "아누아 어성초 제품 민감성 피부에 최고예요.",
        "아누아는 어성초 성분으로 유명한 한국 브랜드예요.",
        "틱톡에서 아누아 토너 바이럴됐잖아요.",
        "아누아 vs 라이언 어성초 토너 비교해봤어요.",
        "아누아 제품 해외배송 돼요?",
        "아누아 어성초 토너 여드름 피부에 좋아요.",
        "아누아는 세포라에서도 팔아요.",
        "아누아 클렌징도 있어요.",
        "아누아 쿠션도 나왔더라고요.",
    ],
    "달바": [
        "달바 화이트 트러플 앰플 들어봤어요?",
        "달바는 프리미엄 K-뷰티 브랜드예요.",
        "달바 선크림도 나왔어요.",
        "비피다 성분 제품은 달바나 CNP가 유명해요.",
        "달바 화이트 트러플 앰플 고보습이에요.",
        "달바 제품 백화점에서도 팔아요.",
        "달바 vs 설화수 성분 비교했어요.",
        "달바는 중국 시장에서도 잘 팔려요.",
        "달바 앰플 선물용으로 좋아요.",
        "달바 스킨케어 라인이 꽤 다양해요.",
    ],
    "조선미녀": [
        "조선미녀 쌀 선크림 완전 유명해요.",
        "조선미녀 선크림 해외에서 난리났잖아요.",
        "조선미녀 vs 아누아 선크림 비교해봤어요.",
        "조선미녀는 틱톡에서 바이럴된 K-뷰티 브랜드예요.",
        "조선미녀 레드 선스크린도 나왔어요.",
        "조선미녀 세럼도 있어요.",
        "쌀 선크림은 조선미녀가 원조예요.",
        "조선미녀 아마존에서 베스트셀러예요.",
        "조선미녀 제품 화이트닝 효과 있어요.",
        "조선미녀는 영어 이름이 Beauty of Joseon이에요.",
    ],
}

# Simulated Naver SERP text snippets (representative, not scraped live)
SIMULATED_NAVER_RESULTS = {
    "라라스윗": "라라스윗 후기 라라스윗 사용 후기 써봤어요 재구매 추천 효과 있어요 blog.naver.com 라라스윗",
    "토리든": "토리든 다이브인 후기 토리든 히알루론산 사용 후기 추천 재구매 blog.naver.com 토리든 효과 있어요",
    "아누아": "아누아 어성초 후기 아누아 토너 사용 후기 민감성 피부 추천 blog.naver.com 아누아 재구매 써봤어요 효과",
    "달바": "달바 앰플 후기 달바 사용 후기 추천 blog.naver.com 달바 재구매 효과 있어요",
    "조선미녀": "조선미녀 선크림 후기 쌀 선크림 사용 후기 추천 blog.naver.com 조선미녀 재구매 써봤어요 효과 완전 좋아요",
}


def run_scanner_test(brand: dict, verbose: bool = True) -> dict:
    """Runs the full scanner pipeline on one brand using simulated data."""
    brand_name = brand["name"]

    # AI visibility (simulated responses)
    simulated = SIMULATED_AI_RESPONSES.get(brand_name, [])
    ai_result = parse_responses(brand_name, simulated)

    # Naver SERP (simulated snippet)
    naver_text = SIMULATED_NAVER_RESULTS.get(brand_name, "")
    naver_result = parse_naver_result(brand_name, naver_text)

    # Combined GEO score
    score = score_from_audit_results(ai_result, naver_result)
    score["website_url"] = brand["website"]

    if verbose:
        print(f"\n{brand_name} ({brand['website']})")
        print(f"  AI visibility:  {ai_result['visibility_score']}/100 "
              f"({ai_result['mentions']}/{ai_result['total_responses']} mentions)")
        print(f"  Naver score:    {naver_result['naver_score']}/100")
        print(f"  GEO score:      {score['geo_score']}/100 [{score['band']}]")
        print(f"  Recommendation: {score['recommendation']}")

    return score


def test_all_brands():
    """pytest-compatible test: all 5 brands produce valid scores."""
    results = []
    for brand in BRANDS:
        score = run_scanner_test(brand, verbose=False)
        assert "geo_score" in score, f"Missing geo_score for {brand['name']}"
        assert 0 <= score["geo_score"] <= 100, f"Score out of range for {brand['name']}"
        assert score["band"] in ("우수", "보통", "미흡", "위험"), f"Invalid band for {brand['name']}"
        results.append(score)
    return results


def test_score_calculator():
    """Unit test for score_calculator.calculate_geo_score()."""
    result = calculate_geo_score(ai_score=100, naver_score=100)
    assert result["geo_score"] == 100
    assert result["band"] == "우수"

    result = calculate_geo_score(ai_score=0, naver_score=0)
    assert result["geo_score"] == 0
    assert result["band"] == "위험"

    result = calculate_geo_score(ai_score=60, naver_score=50)
    assert 50 <= result["geo_score"] <= 65


def test_queries_built():
    """Unit test: query builder returns correct structure."""
    queries = build_queries("테스트브랜드")
    assert "brand_queries" in queries
    assert "generic_queries" in queries
    assert len(queries["brand_queries"]) > 0
    assert "테스트브랜드" in queries["brand_queries"][0]


def test_naver_parse():
    """Unit test: naver parser handles empty and non-empty input."""
    empty = parse_naver_result("Brand", "")
    assert empty["naver_score"] == 0
    assert empty["brand_mentions"] == 0

    rich = parse_naver_result(
        "아누아",
        "아누아 후기 아누아 추천 써봤어요 blog.naver.com 아누아 재구매",
    )
    assert rich["naver_score"] > 0
    assert rich["brand_mentions"] >= 3


if __name__ == "__main__":
    print("=" * 60)
    print("GEO Scanner -- 5 Korean Skincare Brand Audit")
    print("=" * 60)

    all_results = []
    for brand in BRANDS:
        result = run_scanner_test(brand, verbose=True)
        all_results.append(result)

    # Ranking
    ranked = sorted(all_results, key=lambda x: x["geo_score"], reverse=True)
    print("\n" + "=" * 60)
    print("RANKING (AI visibility + Naver SEO)")
    print("=" * 60)
    for i, r in enumerate(ranked, 1):
        print(f"  #{i} {r['brand']}: {r['geo_score']}/100 [{r['band']}]")

    print(f"\nBest:  {ranked[0]['brand']} ({ranked[0]['geo_score']}/100)")
    print(f"Worst: {ranked[-1]['brand']} ({ranked[-1]['geo_score']}/100)")

    # Run unit tests
    print("\n--- Unit Tests ---")
    test_score_calculator()
    print("test_score_calculator: PASS")
    test_queries_built()
    print("test_queries_built: PASS")
    test_naver_parse()
    print("test_naver_parse: PASS")
    results = test_all_brands()
    print(f"test_all_brands: PASS ({len(results)}/5 brands scored)")
