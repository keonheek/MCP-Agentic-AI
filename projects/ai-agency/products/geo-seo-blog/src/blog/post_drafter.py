"""
post_drafter.py
Blog post drafting module.

Per CLAUDE.md hard rules: LLM-dependent work (post drafting) defers to
slash command pattern. This module provides:
  1. build_draft_prompt() -- generates the system + user prompt for
     use inside a Claude Code session via slash command
  2. parse_draft_response() -- cleans and validates the LLM output
  3. run_draft_with_api() -- direct API call for demo/testing only
     (requires ANTHROPIC_API_KEY)

Production workflow:
  1. Call build_draft_prompt(topic, client_config)
  2. Paste into Claude Code session / slash command
  3. Pass the output to parse_draft_response()
  4. Feed into geo_optimizer.optimize_post() and naver_seo_optimizer.run_naver_seo_pass()
"""

import os
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

for _p in [
    Path(__file__).parents[4] / ".env",
    Path(__file__).parents[5] / ".env",
]:
    if _p.exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=_p)
        break

DRAFT_SYSTEM_PROMPT = """당신은 한국 스킨케어 브랜드 전문 블로그 작가입니다.
Naver SEO와 AI 인용 최적화(GEO)를 모두 고려한 블로그 포스트를 작성합니다.

작성 규칙:
- 길이: 800-1,200 단어 (한국어 기준)
- 구조: 서론 (100자) + 본론 H2 섹션 3개 + 마무리 (100자)
- 첫 200자 안에 주요 키워드 포함
- H2 헤더 최소 3개 사용
- 명확하고 직접적인 문장 (수동태 지양)
- 브랜드 멘션 자연스럽게 2-3회
- 인용 가능한 factual 문장 포함 (ChatGPT/Perplexity 인용 최적화)
- 말줄임표(...), 감탄부호 과다 사용 금지"""


def build_draft_prompt(topic: str, client_config: dict, brand_voice_prompt: str = "") -> dict:
    """
    Builds the system and user prompt for blog post drafting.

    Returns:
        {"system": str, "user": str}
    """
    brand = client_config.get("brand_name", "브랜드")
    keywords = client_config.get("target_keywords", [])
    primary_kw = keywords[0] if keywords else topic
    voice = brand_voice_prompt or client_config.get("brand_voice", "친근하고 전문적인 스킨케어 전문가 톤")

    user_prompt = f"""다음 주제로 네이버 블로그 포스트를 작성해주세요.

주제: {topic}
브랜드명: {brand}
주요 키워드: {primary_kw}
보조 키워드: {', '.join(keywords[1:3]) if len(keywords) > 1 else '없음'}
톤앤매너: {voice}

필수 포함 요소:
1. 첫 200자 안에 "{primary_kw}" 키워드 포함
2. H2 헤더 최소 3개
3. "{brand}" 브랜드 자연스럽게 2-3회 언급
4. AI가 인용하기 쉬운 factual 문장 최소 2개
   (예: "A는 B에 효과적입니다", "전문가들은 C를 권장합니다")

출력 형식: 마크다운 (제목은 #, 소제목은 ##)"""

    return {"system": DRAFT_SYSTEM_PROMPT, "user": user_prompt}


def parse_draft_response(llm_response: str) -> dict:
    """
    Parses and validates an LLM-generated blog post draft.

    Returns:
        {
          "title": str,
          "body": str,
          "word_count": int,
          "h2_count": int,
          "valid": bool,
          "issues": list[str]
        }
    """
    text = llm_response.strip()

    # Extract title
    title_match = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else ""

    # Count H2 headers
    h2_count = len(re.findall(r'^##\s+', text, re.MULTILINE))

    # Word count (Korean: count chars / 2 as rough proxy)
    word_count = len(text.split())

    issues = []
    if not title:
        issues.append("제목(#) 없음")
    if h2_count < 3:
        issues.append(f"H2 헤더 {h2_count}개 (최소 3개 필요)")
    if word_count < 400:
        issues.append(f"본문 너무 짧음 ({word_count} 단어)")

    return {
        "title": title,
        "body": text,
        "word_count": word_count,
        "h2_count": h2_count,
        "valid": len(issues) == 0,
        "issues": issues,
    }


def run_draft_with_api(topic: str, client_config: dict) -> dict:
    """
    Calls Claude API directly to draft a post.
    For demo/testing only. Production: use slash command pattern.

    Requires ANTHROPIC_API_KEY.
    """
    try:
        import anthropic
    except ImportError:
        return {"error": "anthropic package not installed"}

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return {"error": "ANTHROPIC_API_KEY not set"}

    from src.shared.brand_voice import format_for_prompt

    client = anthropic.Anthropic(api_key=api_key)
    brand_context = format_for_prompt(client_config)
    prompts = build_draft_prompt(topic, client_config, brand_context)

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2000,
            system=prompts["system"],
            messages=[{"role": "user", "content": prompts["user"]}],
        )
        raw = response.content[0].text
        parsed = parse_draft_response(raw)
        return parsed
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    demo_config = {
        "brand_name": "글로우랩",
        "target_keywords": ["비타민C 세럼", "수분크림"],
        "brand_voice": "친근하고 전문적인 뷰티 전문가 톤",
    }
    prompts = build_draft_prompt("비타민C 세럼 효과 완벽 가이드", demo_config)
    print("=== SYSTEM PROMPT ===")
    print(prompts["system"])
    print("\n=== USER PROMPT ===")
    print(prompts["user"])
