"""
data_residency.py
-----------------
Enforces NCP Seoul-only storage for Korean personal data.
PIPA Art. 28-2 (국외 이전), Art. 26 (처리위탁).

2026 amendment: If personal data is processed by AI systems on overseas
servers (e.g., Anthropic API = US servers), this must be disclosed
in the privacy policy and requires explicit consent (Art. 28-2(1)).

This module:
1. Validates that storage endpoints are in approved regions
2. Generates the required overseas transfer disclosure
3. Provides a config registry for approved + prohibited endpoints
"""

from dataclasses import dataclass
from typing import Literal
from pathlib import Path
import json
import datetime


# -----------------------------------------------------------------------
# Region registry
# -----------------------------------------------------------------------

APPROVED_REGIONS = {
    "ncp-kr-1": {
        "provider": "Naver Cloud Platform",
        "region_code": "KR",
        "zone": "서울",
        "compliant": True,
        "note": "Primary: Korean personal data MUST reside here",
    },
    "aws-ap-northeast-2": {
        "provider": "AWS",
        "region_code": "KR",
        "zone": "서울",
        "compliant": True,
        "note": "Permitted alternative if NCP unavailable",
    },
}

OVERSEAS_ENDPOINTS = {
    "anthropic-api": {
        "provider": "Anthropic PBC",
        "country": "US",
        "purpose": "AI 언어 모델 처리 (Claude API)",
        "data_transmitted": ["고객 문의 내용", "리드 메시지"],
        "pipa_basis": "Art. 28-2(1) 명시적 동의",
        "requires_disclosure": True,
    },
    "openai-api": {
        "provider": "OpenAI LLC",
        "country": "US",
        "purpose": "AI 언어 모델 처리 (GPT API)",
        "data_transmitted": ["고객 문의 내용"],
        "pipa_basis": "Art. 28-2(1) 명시적 동의",
        "requires_disclosure": True,
    },
    "make-com": {
        "provider": "Celonis SE (Make)",
        "country": "EU",
        "purpose": "자동화 워크플로우 처리",
        "data_transmitted": ["이름", "연락처", "주문 정보"],
        "pipa_basis": "Art. 28-2(1) 명시적 동의",
        "requires_disclosure": True,
    },
    "google-workspace": {
        "provider": "Google LLC",
        "country": "US",
        "purpose": "이메일 / 문서 처리",
        "data_transmitted": ["이메일 주소", "첨부파일"],
        "pipa_basis": "Art. 28-2(1) 명시적 동의",
        "requires_disclosure": True,
    },
}

PROHIBITED_REGIONS = {
    "aws-us-east-1",
    "aws-eu-west-1",
    "azure-eastus",
    "gcp-us-central1",
}


# -----------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------

@dataclass
class ResidencyCheckResult:
    endpoint: str
    is_compliant: bool
    region: str
    requires_overseas_disclosure: bool
    disclosure_text: str
    recommendation: str


def check_endpoint(endpoint_id: str) -> ResidencyCheckResult:
    """
    Check if a storage/processing endpoint is PIPA-compliant.
    Covers both approved Korean regions and disclosed overseas endpoints.
    """
    if endpoint_id in APPROVED_REGIONS:
        info = APPROVED_REGIONS[endpoint_id]
        return ResidencyCheckResult(
            endpoint=endpoint_id,
            is_compliant=True,
            region=info["zone"],
            requires_overseas_disclosure=False,
            disclosure_text="",
            recommendation="적합. 국내 서버 보관 기준 충족.",
        )

    if endpoint_id in OVERSEAS_ENDPOINTS:
        info = OVERSEAS_ENDPOINTS[endpoint_id]
        disclosure = _build_overseas_disclosure(endpoint_id, info)
        return ResidencyCheckResult(
            endpoint=endpoint_id,
            is_compliant=False,  # Not compliant WITHOUT explicit consent + disclosure
            region=info["country"],
            requires_overseas_disclosure=True,
            disclosure_text=disclosure,
            recommendation=(
                f"동의서 및 개인정보처리방침에 국외 이전 고지 필수 (PIPA Art. 28-2). "
                f"고지 없이 사용 시 과태료 대상."
            ),
        )

    if endpoint_id in PROHIBITED_REGIONS:
        return ResidencyCheckResult(
            endpoint=endpoint_id,
            is_compliant=False,
            region="해외",
            requires_overseas_disclosure=True,
            disclosure_text="",
            recommendation="사용 금지. 국외 이전 동의 없이 한국 개인정보 저장 불가.",
        )

    return ResidencyCheckResult(
        endpoint=endpoint_id,
        is_compliant=False,
        region="알 수 없음",
        requires_overseas_disclosure=True,
        disclosure_text="",
        recommendation="미등록 엔드포인트. 법무 검토 필요.",
    )


def validate_stack(endpoint_ids: list[str]) -> dict:
    """
    Validate a full tech stack.
    Returns summary dict with overall compliance flag and per-endpoint results.
    """
    results = [check_endpoint(eid) for eid in endpoint_ids]
    all_compliant = all(
        r.is_compliant or r.requires_overseas_disclosure
        for r in results
    )
    return {
        "stack_assessed_at": datetime.datetime.utcnow().isoformat() + "Z",
        "overall_compliant_with_disclosure": all_compliant,
        "endpoints": [
            {
                "id": r.endpoint,
                "compliant": r.is_compliant,
                "requires_disclosure": r.requires_overseas_disclosure,
                "recommendation": r.recommendation,
            }
            for r in results
        ],
        "disclosures_required": [
            r.disclosure_text
            for r in results
            if r.requires_overseas_disclosure and r.disclosure_text
        ],
    }


# -----------------------------------------------------------------------
# Disclosure generator
# -----------------------------------------------------------------------

def _build_overseas_disclosure(endpoint_id: str, info: dict) -> str:
    """Build the Korean disclosure text required by PIPA Art. 28-2."""
    data_types = ", ".join(info.get("data_transmitted", []))
    return (
        f"[국외 이전 고지 -- PIPA 제28조의2]\n"
        f"이전받는 자: {info['provider']} ({info['country']})\n"
        f"이전 목적: {info['purpose']}\n"
        f"이전 항목: {data_types}\n"
        f"법적 근거: {info['pipa_basis']}\n"
        f"이전 거부 방법: 서비스 이용을 중단하거나 동의를 철회할 수 있습니다.\n"
        f"이전 거부 시 불이익: 해당 기능을 이용할 수 없습니다."
    )


def generate_all_disclosures() -> str:
    """Generate combined overseas transfer disclosure for privacy policy."""
    lines = ["=== 개인정보 국외 이전 현황 (PIPA Art. 28-2) ===\n"]
    for eid, info in OVERSEAS_ENDPOINTS.items():
        lines.append(f"--- {eid} ---")
        lines.append(_build_overseas_disclosure(eid, info))
        lines.append("")
    return "\n".join(lines)
