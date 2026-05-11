"""
Strand 4: Positioning Gaps -- Pure Data Gatherer
Returns current positioning state + search queries for the slash command to run.
NO LLM calls.
"""


CURRENT_POSITIONING = """
Current claimed positioning (as of 2026-05-11):
- GitHub: keonheek (profile repo exists, READMEs updated with consulting framing)
- LinkedIn: Korean + English bilingual About (SDIC founder, FinAgent, DART app)
- Deployed apps: keonhee-finagent.streamlit.app, keonhee-strategy.streamlit.app, keonhee-leadintelligence.streamlit.app
- Instagram: @1stmover.ai (opportunistic only, not actively posted)
- Agency brand name: NOT YET DECIDED (blocker)
- Public price page: NOT YET PUBLISHED (identified as high-impact, effort S)
- Case studies: ZERO published (first 2 clients planned at 500K discount price)

Services not publicly listed anywhere yet:
- Service V (AI 영상 광고)
- Service A (AI 자동화, PIPA Tier P)
- Service W (AI 웹사이트)
"""

SEARCH_QUERIES = [
    "best Korean agentic AI developer 2026",
    "Korean AI agency Seoul 2026",
    "Claude Code Korea developer 2026",
    "AI 자동화 에이전시 서울 2026",
    "화장품 AI 광고 에이전시 한국",
    "PIPA compliance AI Korea 2026",
    "한국 AI 에이전시 포트폴리오",
    "LangGraph Korean developer 2026",
]


def run() -> dict:
    """
    Returns current positioning state + queries for the slash command to WebSearch and synthesize.
    """
    return {
        "current_positioning": CURRENT_POSITIONING.strip(),
        "queries": SEARCH_QUERIES,
    }
