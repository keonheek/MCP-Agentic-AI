"""
ai_visibility_check.py
Checks how visible a Korean skincare brand is in AI systems.

Per the hard rules in CLAUDE.md: LLM-dependent calls defer to slash command
pattern. This module builds the query set and parses responses when they are
provided externally (e.g., via run_demo.py which calls Claude directly).

For production use inside a session: call build_queries() to get the
prompts, pass them to your LLM of choice, then parse_responses() to score.

If ANTHROPIC_API_KEY is set, run_live_check() will call Claude directly
(used in demo mode only).
"""

import os
import sys
import json
import re
from pathlib import Path

for _p in [
    Path(__file__).parent.parent.parent.parent / ".env",
    Path(__file__).parent.parent.parent.parent.parent / ".env",
    Path(__file__).parent.parent.parent.parent.parent.parent / ".env",
]:
    if _p.exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=_p)
        break

sys.stdout.reconfigure(encoding="utf-8")

SKINCARE_QUERY_TEMPLATES = [
    "{brand} 스킨케어 어때요?",
    "{brand} 제품 추천해줘",
    "한국 스킨케어 브랜드 중에 {brand} 써봤어? 어때?",
    "{brand} 비타민C 세럼 효과 있어?",
    "{brand} 어디서 살 수 있어?",
]

GENERIC_QUERY_TEMPLATES = [
    "한국 스킨케어 브랜드 추천해줘",
    "민감성 피부에 좋은 한국 화장품 브랜드는?",
    "가성비 좋은 한국 스킨케어 추천",
    "비타민C 세럼 한국 브랜드 추천",
    "수분크림 한국 브랜드 추천해줘",
]


def build_queries(brand_name: str) -> dict:
    """Returns brand-specific and generic queries for AI visibility testing."""
    brand_queries = [t.format(brand=brand_name) for t in SKINCARE_QUERY_TEMPLATES]
    return {
        "brand_queries": brand_queries,
        "generic_queries": GENERIC_QUERY_TEMPLATES,
    }


def parse_responses(brand_name: str, responses: list[str]) -> dict:
    """
    Given a list of LLM response strings, calculate how often the brand
    was mentioned and score brand visibility 0-100.

    Returns:
        {
          "brand": str,
          "mentions": int,
          "total_responses": int,
          "mention_rate": float,
          "visibility_score": int (0-100),
          "raw_responses": list[str]
        }
    """
    brand_lower = brand_name.lower()
    mentions = sum(
        1 for r in responses if brand_lower in r.lower()
    )
    total = len(responses) if responses else 1
    mention_rate = mentions / total
    # Score: 100 if mentioned in all, 0 if never
    visibility_score = round(mention_rate * 100)

    return {
        "brand": brand_name,
        "mentions": mentions,
        "total_responses": total,
        "mention_rate": round(mention_rate, 2),
        "visibility_score": visibility_score,
        "raw_responses": responses,
    }


def run_live_check(brand_name: str, website_url: str = "") -> dict:
    """
    Runs a live AI visibility check using Claude (claude-haiku-4-5-20251001).
    Requires ANTHROPIC_API_KEY in environment.

    Used in demo mode. In production, defer to /slash-command pattern.
    """
    try:
        import anthropic
    except ImportError:
        return {"error": "anthropic package not installed. Run: pip install anthropic"}

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return {"error": "ANTHROPIC_API_KEY not set in environment"}

    client = anthropic.Anthropic(api_key=api_key)
    queries = build_queries(brand_name)
    all_queries = queries["brand_queries"] + queries["generic_queries"]
    responses = []

    for q in all_queries:
        try:
            resp = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=300,
                system=(
                    "You are a helpful Korean beauty advisor. "
                    "Answer naturally as you would to a friend asking for skincare advice. "
                    "If you know the brand, mention it honestly. If not, say so. "
                    "Keep responses under 5 sentences. Answer in Korean."
                ),
                messages=[{"role": "user", "content": q}],
            )
            responses.append(resp.content[0].text.strip())
        except Exception as e:
            responses.append(f"[ERROR: {e}]")

    result = parse_responses(brand_name, responses)
    result["queries_used"] = all_queries
    result["website_url"] = website_url
    return result


if __name__ == "__main__":
    brand = sys.argv[1] if len(sys.argv) > 1 else "글로우랩"
    result = run_live_check(brand)
    print(json.dumps(result, ensure_ascii=False, indent=2))
