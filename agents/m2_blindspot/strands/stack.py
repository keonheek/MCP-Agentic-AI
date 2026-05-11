"""
Strand 2: Stack Obsolescence -- Pure Data Gatherer
Returns current stack manifest + search queries for the slash command to run.
NO LLM calls.
"""


CURRENT_STACK = """
- AI Video: Higgsfield Pro (Nano Banana + Cinema Studio), Kling 2.5 Pro, Veo 3, ElevenLabs v3, Suno Pro
- AI Automation: Flask/ngrok (demo), Make.com (first client), n8n on NCP (prod), Claude Sonnet (triage/reply)
- AI Website: Claude Design + Next.js 15 + Vercel
- LLM: Claude Sonnet 4.6 (primary), Claude Haiku (fast triage)
- Dev: LangGraph, FastAPI, Streamlit, OpenAI text-embedding-3-small
- Infra: NCP (Naver Cloud Platform), ngrok, Notion, Supabase
"""

WATCH_QUERIES = [
    "Anthropic new model release 2026",
    "Anthropic memory tool agents 2026",
    "Claude Code subagent update 2026",
    "OpenAI Agents SDK update 2026",
    "LangGraph new release 2026",
    "Higgsfield AI update 2026",
    "ElevenLabs v3 update 2026",
    "Veo 3 Google video AI 2026",
    "Naver Cloud AI product 2026 HyperCLOVA",
    "Cafe24 API update 2026",
    "Make.com n8n automation update 2026",
    "Korean AI tool release 2026 Upstage Solar",
]


def run() -> dict:
    """
    Returns current stack + queries for the slash command to WebSearch and synthesize.
    """
    return {
        "current_stack": CURRENT_STACK.strip(),
        "queries": WATCH_QUERIES,
    }
