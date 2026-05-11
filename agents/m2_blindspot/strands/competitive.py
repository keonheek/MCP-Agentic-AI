"""
Strand 1: Competitive Moves -- Pure Data Gatherer
Returns search queries + baseline context for the slash command to process.
NO LLM calls.
"""

from pathlib import Path


SEARCH_QUERIES = [
    "Korean AI automation agency 2026",
    "AI 영상 광고 에이전시 한국 2026",
    "AI 자동화 화장품 한국 2026",
    "한국 AI 에이전시 가격 2026",
    "AI agency Korea pricing 2026",
]

# Known competitor pricing baseline (from 2026-05-09 scrape)
BASELINE = {
    "service_a_setup": 500000,
    "service_a_monthly": 200000,
    "service_v_flat": 1500000,
    "service_v_retainer_low": 2500000,
    "pipa_tier_p": 3000000,
}


def run(competitor_scrape_path=None) -> dict:
    """
    Returns raw data for the slash command to synthesize.
    Keys: queries, baseline, competitor_scrape_excerpt
    """
    competitor_context = ""
    if competitor_scrape_path and Path(competitor_scrape_path).exists():
        try:
            competitor_context = Path(competitor_scrape_path).read_text(encoding="utf-8")[:3000]
        except Exception:
            competitor_context = "[Could not read competitor scrape file]"
    else:
        competitor_context = "[No baseline competitor scrape file found]"

    return {
        "queries": SEARCH_QUERIES,
        "baseline_pricing": BASELINE,
        "competitor_scrape_excerpt": competitor_context,
    }
