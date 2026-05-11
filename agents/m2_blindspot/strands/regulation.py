"""
Strand 3: Regulation Drift -- Pure Data Gatherer
Returns baseline regulatory state + search queries for the slash command to run.
NO LLM calls.
"""


REGULATION_BASELINE = """
Known regulatory state as of 2026-05-11:
- PIPA (개인정보보호법) 개정: effective 2026-09-15. Key impact: automated decision-making must be disclosed;
  sensitive personal data handling requires explicit consent; increased fines up to 3% of global revenue.
  Service A monetized as PIPA Tier P SKU (3M one-shot + 500K/mo monitoring).
- 식약처 화장품 광고 가이드라인: prohibits clinical efficacy claims without substantiation;
  prohibits before/after images unless clinical trial backed; 피부과 테스트 완료 requires certification.
  Service V (AI video ads) and Service W (advertorial landing pages) must lint against these rules.
- AI Basic Act Korea (AI 기본법): passed 2024, enforcement phased in 2025-2026.
  High-risk AI systems require conformity assessment. Current status unclear for marketing AI.
- 표시광고법: general false advertising rules apply to all services.
"""

SEARCH_QUERIES = [
    "PIPA 개정 2026 개인정보보호법",
    "Korean privacy regulation amendment 2026",
    "식약처 화장품 광고 가이드라인 2026",
    "AI Basic Act Korea enforcement 2026 AI 기본법",
    "한국 AI 규제 2026",
    "cosmetics advertising regulation Korea 2026",
    "개인정보보호법 자동화 의사결정 2026",
]


def run() -> dict:
    """
    Returns regulatory baseline + queries for the slash command to WebSearch and synthesize.
    """
    return {
        "regulation_baseline": REGULATION_BASELINE.strip(),
        "queries": SEARCH_QUERIES,
    }
