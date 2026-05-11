"""
test_geo_schema_validity.py
Tests JSON-LD FAQ schema generation and validity.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from src.blog.geo_optimizer import (
    generate_json_ld_faq,
    generate_faq_pairs,
    inject_faq_section,
    optimize_post,
)

SAMPLE_DRAFT = """# 비타민C 세럼 완벽 가이드

비타민C는 피부 미백에 효과적인 성분입니다.
글로우랩 비타민C 세럼은 안정화 성분을 사용합니다.

## 사용 방법

아침 루틴에서 토너 후 사용합니다.
"""


def test_json_ld_schema_is_valid_json():
    faq_pairs = generate_faq_pairs("비타민C 세럼", "글로우랩")
    schema_str = generate_json_ld_faq(faq_pairs)
    try:
        schema = json.loads(schema_str)
        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "FAQPage"
        assert "mainEntity" in schema
        print(f"  Schema valid: {len(schema['mainEntity'])} FAQ entries")
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid JSON: {e}")


def test_json_ld_has_required_fields():
    faq_pairs = [
        {"q": "질문 1", "a": "답변 1"},
        {"q": "질문 2", "a": "답변 2"},
    ]
    schema_str = generate_json_ld_faq(faq_pairs)
    schema = json.loads(schema_str)

    for entity in schema["mainEntity"]:
        assert entity["@type"] == "Question"
        assert "name" in entity
        assert "acceptedAnswer" in entity
        assert entity["acceptedAnswer"]["@type"] == "Answer"
        assert "text" in entity["acceptedAnswer"]
    print(f"  All required JSON-LD fields present")


def test_faq_pairs_generated():
    pairs = generate_faq_pairs("수분크림", "달바")
    assert len(pairs) >= 2
    for pair in pairs:
        assert "q" in pair and "a" in pair
        assert len(pair["q"]) > 0
        assert len(pair["a"]) > 0
    print(f"  Generated {len(pairs)} FAQ pairs")


def test_faq_injection_appends_to_draft():
    faq_pairs = [{"q": "테스트 질문", "a": "테스트 답변"}]
    result = inject_faq_section(SAMPLE_DRAFT, faq_pairs)
    assert "자주 묻는 질문" in result
    assert "테스트 질문" in result
    assert "테스트 답변" in result
    assert len(result) > len(SAMPLE_DRAFT)
    print(f"  FAQ section injected: {len(result) - len(SAMPLE_DRAFT)} chars added")


def test_optimize_post_returns_full_dict():
    result = optimize_post(SAMPLE_DRAFT, "비타민C 세럼", "글로우랩")
    assert "optimized_draft" in result
    assert "json_ld_schema" in result
    assert "faq_pairs" in result
    assert len(result["optimized_draft"]) > len(SAMPLE_DRAFT)

    # Validate the schema is parseable
    schema = json.loads(result["json_ld_schema"])
    assert schema["@type"] == "FAQPage"
    print(f"  Full optimize_post pipeline: PASS")


def test_empty_faq_pairs_safe():
    result = inject_faq_section(SAMPLE_DRAFT, [])
    assert result == SAMPLE_DRAFT, "Empty FAQ should return draft unchanged"
    print(f"  Empty FAQ pairs: safe (no injection)")


if __name__ == "__main__":
    print("=== GEO Schema Validity Tests ===\n")
    test_json_ld_schema_is_valid_json()
    print("test_json_ld_schema_is_valid_json: PASS")
    test_json_ld_has_required_fields()
    print("test_json_ld_has_required_fields: PASS")
    test_faq_pairs_generated()
    print("test_faq_pairs_generated: PASS")
    test_faq_injection_appends_to_draft()
    print("test_faq_injection_appends_to_draft: PASS")
    test_optimize_post_returns_full_dict()
    print("test_optimize_post_returns_full_dict: PASS")
    test_empty_faq_pairs_safe()
    print("test_empty_faq_pairs_safe: PASS")
    print("\nAll schema validity tests passed.")
