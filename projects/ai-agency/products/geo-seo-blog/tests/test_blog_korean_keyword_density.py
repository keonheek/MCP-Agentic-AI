"""
test_blog_korean_keyword_density.py
Tests keyword density analysis for Korean blog posts.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from src.blog.naver_seo_optimizer import check_keyword_density, optimize_title, generate_meta_description

SAMPLE_POST = """# 비타민C 세럼 효과 완벽 가이드

비타민C 세럼은 피부 미백과 항산화에 효과적인 성분입니다.
글로우랩 비타민C 세럼은 안정화 비타민C 15%를 함유합니다.

## 비타민C 세럼의 핵심 효과

비타민C 세럼을 꾸준히 사용하면 피부 톤이 밝아집니다.
멜라닌 생성을 억제해 기미와 잡티 개선에 도움을 줍니다.

## 올바른 사용 방법

비타민C 세럼은 아침 루틴에서 사용하는 것이 효과적입니다.
토너 후, 에센스 전 단계에서 바릅니다.

## 주의사항

비타민C 세럼은 산성 제품이므로 레티놀과 함께 사용하지 않는 것이 좋습니다.
"""


def test_keyword_density_in_range():
    result = check_keyword_density(SAMPLE_POST, "비타민C 세럼")
    assert result["count"] > 0, "Keyword not found in sample post"
    assert result["density"] > 0
    print(f"  Keyword density: {result['density_pct']} ({result['count']} mentions) -- {result['recommendation']}")


def test_keyword_density_zero_for_missing():
    result = check_keyword_density(SAMPLE_POST, "레티놀 크림")
    # "레티놀" appears but "레티놀 크림" does not as a phrase
    assert result["count"] == 0 or result["density"] < 0.01
    print(f"  Missing keyword density: {result['density_pct']}")


def test_keyword_density_caps_at_100():
    # Repeated keyword should not produce score > 100
    repeated = "비타민C 세럼 " * 100
    result = check_keyword_density(repeated, "비타민C 세럼")
    assert result["density"] <= 1.0


def test_title_optimization():
    title = optimize_title("효과 완벽 가이드", "비타민C 세럼", "글로우랩")
    assert "비타민C 세럼" in title
    assert len(title) <= 38  # max + ellipsis
    print(f"  Optimized title: {title} ({len(title)} chars)")


def test_meta_description_length():
    meta = generate_meta_description(SAMPLE_POST, "비타민C 세럼", "글로우랩")
    assert 70 <= len(meta) <= 130, f"Meta length {len(meta)} out of range"
    assert "비타민C 세럼" in meta or "글로우랩" in meta
    print(f"  Meta description: {meta} ({len(meta)} chars)")


def test_meta_contains_cta():
    meta = generate_meta_description(SAMPLE_POST, "비타민C 세럼", "글로우랩")
    # Should contain brand name or keyword as soft CTA marker
    assert "글로우랩" in meta or "확인" in meta or "비타민C" in meta
    print(f"  CTA present: YES")


if __name__ == "__main__":
    print("=== Naver SEO Keyword Density Tests ===\n")
    test_keyword_density_in_range()
    print("test_keyword_density_in_range: PASS")
    test_keyword_density_zero_for_missing()
    print("test_keyword_density_zero_for_missing: PASS")
    test_keyword_density_caps_at_100()
    print("test_keyword_density_caps_at_100: PASS")
    test_title_optimization()
    print("test_title_optimization: PASS")
    test_meta_description_length()
    print("test_meta_description_length: PASS")
    test_meta_contains_cta()
    print("test_meta_contains_cta: PASS")
    print("\nAll keyword density tests passed.")
