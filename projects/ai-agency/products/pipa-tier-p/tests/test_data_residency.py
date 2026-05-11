"""
test_data_residency.py
----------------------
Tests for data_residency.py endpoint validation.
Zero API calls.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.data_residency import (
    check_endpoint,
    validate_stack,
    generate_all_disclosures,
    APPROVED_REGIONS,
    OVERSEAS_ENDPOINTS,
    PROHIBITED_REGIONS,
)


def test_ncp_kr1_is_compliant():
    result = check_endpoint("ncp-kr-1")
    assert result.is_compliant is True
    assert result.requires_overseas_disclosure is False


def test_aws_seoul_is_compliant():
    result = check_endpoint("aws-ap-northeast-2")
    assert result.is_compliant is True


def test_anthropic_api_requires_disclosure():
    result = check_endpoint("anthropic-api")
    assert result.is_compliant is False
    assert result.requires_overseas_disclosure is True
    assert "Art. 28-2" in result.disclosure_text or "28조" in result.disclosure_text


def test_make_com_requires_disclosure():
    result = check_endpoint("make-com")
    assert result.requires_overseas_disclosure is True
    assert len(result.disclosure_text) > 0


def test_prohibited_region_flagged():
    result = check_endpoint("aws-us-east-1")
    assert result.is_compliant is False
    assert result.requires_overseas_disclosure is True


def test_unknown_endpoint_flagged():
    result = check_endpoint("some-random-cloud-xyz")
    assert result.is_compliant is False


def test_validate_stack_pure_korean():
    summary = validate_stack(["ncp-kr-1"])
    assert summary["overall_compliant_with_disclosure"] is True
    assert summary["endpoints"][0]["compliant"] is True


def test_validate_stack_with_ai_api():
    summary = validate_stack(["ncp-kr-1", "anthropic-api"])
    # Not compliant without disclosure but overall flag accounts for disclosed overseas
    assert len(summary["disclosures_required"]) >= 1


def test_validate_stack_multiple():
    stack = ["ncp-kr-1", "anthropic-api", "make-com", "google-workspace"]
    summary = validate_stack(stack)
    assert len(summary["endpoints"]) == 4
    assert "stack_assessed_at" in summary


def test_generate_all_disclosures_contains_all_overseas():
    text = generate_all_disclosures()
    for endpoint_id in OVERSEAS_ENDPOINTS:
        assert endpoint_id in text


def test_disclosure_text_contains_pipa_article():
    result = check_endpoint("anthropic-api")
    # Should reference Art. 28-2 or the Korean equivalent
    assert "28" in result.disclosure_text


def test_approved_regions_not_in_prohibited():
    for region in APPROVED_REGIONS:
        assert region not in PROHIBITED_REGIONS
