"""
test_kakao_format.py
Tests KakaoTalk delivery package formatting.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from src.blog.kakao_packager import format_for_kakao

SAMPLE_DRAFT = "## 비타민C 세럼\n\n글로우랩 제품 소개입니다."
SAMPLE_SCHEMA = '{"@type": "FAQPage"}'


def _make_package(**kwargs):
    defaults = dict(
        brand_name="글로우랩",
        post_title="비타민C 세럼 효과 | 글로우랩",
        meta_description="비타민C 세럼 효과와 사용법. 글로우랩에서 확인하세요.",
        optimized_draft=SAMPLE_DRAFT,
        json_ld_schema=SAMPLE_SCHEMA,
        post_number=1,
        total_posts=4,
    )
    defaults.update(kwargs)
    return format_for_kakao(**defaults)


def test_package_contains_brand_name():
    pkg = _make_package()
    assert "글로우랩" in pkg
    print("  Brand name present: PASS")


def test_package_contains_post_title():
    pkg = _make_package()
    assert "비타민C 세럼 효과 | 글로우랩" in pkg
    print("  Post title present: PASS")


def test_package_contains_meta_description():
    pkg = _make_package()
    assert "비타민C 세럼 효과와 사용법" in pkg
    print("  Meta description present: PASS")


def test_package_contains_draft_body():
    pkg = _make_package()
    assert "글로우랩 제품 소개입니다" in pkg
    print("  Draft body present: PASS")


def test_package_contains_json_ld():
    pkg = _make_package()
    assert "application/ld+json" in pkg
    assert "FAQPage" in pkg
    print("  JSON-LD block present: PASS")


def test_package_contains_checklist():
    pkg = _make_package()
    assert "체크리스트" in pkg
    assert "[ ]" in pkg
    print("  Upload checklist present: PASS")


def test_package_post_numbering():
    pkg = _make_package(post_number=3, total_posts=4)
    assert "#3/4" in pkg
    print("  Post numbering: PASS")


def test_package_no_em_dashes():
    pkg = _make_package()
    assert "—" not in pkg, "Em dash found in KakaoTalk package -- hard rule violation"
    print("  No em dashes: PASS")


def test_package_is_string_nonempty():
    pkg = _make_package()
    assert isinstance(pkg, str)
    assert len(pkg) > 200
    print(f"  Package length: {len(pkg)} chars")


if __name__ == "__main__":
    print("=== KakaoTalk Package Format Tests ===\n")
    test_package_contains_brand_name()
    test_package_contains_post_title()
    test_package_contains_meta_description()
    test_package_contains_draft_body()
    test_package_contains_json_ld()
    test_package_contains_checklist()
    test_package_post_numbering()
    test_package_no_em_dashes()
    test_package_is_string_nonempty()
    print("\nAll KakaoTalk format tests passed.")
