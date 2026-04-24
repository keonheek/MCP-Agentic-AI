"""
Layer 2: 스크립트 + 메타데이터 생성
- First Mover AI YouTube: 해외 영상 번역 롱폼 스크립트
- First Mover AI Instagram: Claude / AI 사업 / 시사 트렌드 33/33/33 캐러셀
"""
import json
import os
import random
from datetime import datetime
from pathlib import Path

import anthropic

BASE_DIR = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = BASE_DIR / "data" / "scripts"
CHANNEL_DRAFTS = BASE_DIR / "channels" / "first-mover-ai" / "drafts"
HOOK_TEMPLATES_PATH = BASE_DIR / "config" / "hook-templates.json"


def load_hooks(namespace: str) -> list[dict]:
    with open(HOOK_TEMPLATES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    ns = data.get(namespace, {})
    if isinstance(ns, dict) and "hooks" in ns:
        return ns["hooks"]
    return []


def generate_youtube_longform_script(candidate: dict) -> dict:
    """해외 AI 영상 → 한국어 번역 롱폼 스크립트 초안"""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    hooks = load_hooks("first_mover_ai_youtube")
    hook_examples = "\n".join(f"- {h['template']}" for h in hooks[:3])

    prompt = f"""너는 "First Mover AI" YouTube 채널 (@firstmoverai_kr) 기획자야.
해외 AI 바이럴 영상을 한국어로 번역+재편집해서 10-20분 롱폼으로 만드는 채널이야.

원본 영상:
- 제목: {candidate.get('title', '')}
- 채널: {candidate.get('channel', '')}
- 조회수: {candidate.get('view_count', 0):,}
- URL: {candidate.get('url', '')}

훅 프레임 예시:
{hook_examples}

다음 구조로 롱폼 스크립트 초안을 만들어. 10-20분 분량. 한국어.

JSON만 출력:
{{
  "title_options": ["한국어 제목 1", "한국어 제목 2", "한국어 제목 3"],
  "hook_10s": "첫 10초 한국어 훅 (시청 유지 결정적)",
  "intro_1min": "1분 이내 소개 (원본 영상 맥락 설명 + 왜 한국에 중요한지)",
  "key_segments": [
    {{"timestamp": "1:00-3:00", "topic": "핵심 1", "korean_script": "한국어 나레이션"}},
    {{"timestamp": "3:00-6:00", "topic": "핵심 2", "korean_script": "..."}},
    {{"timestamp": "6:00-10:00", "topic": "핵심 3", "korean_script": "..."}}
  ],
  "korean_context_addition": "한국 시장/산업 관점에서 추가 해설 (원본에 없는 부분)",
  "outro": "마무리 + 다음 영상 예고",
  "thumbnail_text": "썸네일 큰 글씨 (12자 이내)",
  "youtube_description": "설명란 (첫 줄에 '원본: {candidate.get('url', '')}' 크레딧 필수, 200자 이내)",
  "hashtags": ["#태그1", "#태그2", "#태그3", "#태그4", "#태그5"],
  "fair_use_note": "원본 인용 범위와 변형 내용 요약 (takedown 대응용)"
}}"""

    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text.strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        script = json.loads(text[start:end])
        script["source_candidate"] = candidate
        script["channel"] = "first_mover_ai"
        script["platform"] = "youtube"
        script["generated_at"] = datetime.now().isoformat()
        return script
    except Exception as e:
        return {
            "error": str(e),
            "source_candidate": candidate,
            "channel": "first_mover_ai",
            "platform": "youtube",
            "generated_at": datetime.now().isoformat(),
        }


def generate_instagram_carousel(candidate: dict, category: str) -> dict:
    """Instagram Stories 캐러셀 (5슬라이드)"""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    category_instructions = {
        "claude_news": "Anthropic/Claude 최신 뉴스. 기술적 정확성 + 한국 AI 엔지니어 시각.",
        "ai_business": "AI 스타트업/투자/인수 뉴스. 수치 중심, 한국 시장 함의 포함.",
        "ai_trends": "AI 시사/트렌드. evolving.ai 스타일 (흥미 유발 훅, 반전 포함).",
    }
    instruction = category_instructions.get(category, category_instructions["ai_trends"])

    prompt = f"""너는 "First Mover AI" Instagram (@firstmoverai_kr) 크리에이터야.
카테고리: {category}
스타일: {instruction}

컨텐츠 소스:
- 제목: {candidate.get('title', '')}
- 설명: {candidate.get('description', '')[:200]}
- URL: {candidate.get('url', '')}
- 소스: {candidate.get('source_platform', '')}

5장 캐러셀 슬라이드를 만들어. 한국어. Stories 포맷 (9:16, 큰 글씨).

JSON만 출력:
{{
  "hook_title": "캐러셀 첫 슬라이드 큰 제목 (15자 이내)",
  "slides": [
    {{"num": 1, "role": "hook", "text": "호기심 유발 훅", "big_text": "썸네일 큰 글씨"}},
    {{"num": 2, "role": "context", "text": "무슨 일이 일어났나 (한 문장)", "big_text": ""}},
    {{"num": 3, "role": "key_1", "text": "핵심 인사이트 1", "big_text": ""}},
    {{"num": 4, "role": "key_2", "text": "핵심 인사이트 2 또는 한국 관점", "big_text": ""}},
    {{"num": 5, "role": "cta", "text": "마무리 + 팔로우 유도", "big_text": "First Mover AI"}}
  ],
  "caption": "IG 캡션 (첫 줄 훅 + 본문 + 해시태그, 500자 이내)",
  "hashtags": ["#AI", "#Claude", "#AI뉴스", "#태그4", "#태그5"]
}}"""

    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text.strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        carousel = json.loads(text[start:end])
        carousel["source_candidate"] = candidate
        carousel["channel"] = "first_mover_ai"
        carousel["platform"] = "instagram"
        carousel["category"] = category
        carousel["generated_at"] = datetime.now().isoformat()
        return carousel
    except Exception as e:
        return {
            "error": str(e),
            "source_candidate": candidate,
            "channel": "first_mover_ai",
            "platform": "instagram",
            "category": category,
            "generated_at": datetime.now().isoformat(),
        }


def run_youtube(candidates: list[dict], date_str: str = None) -> str:
    """YouTube 롱폼 스크립트 top 3 생성"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    scripts = []
    for candidate in candidates[:3]:
        print(f"[Layer2/YT] 스크립트 생성: {candidate.get('title', '')[:50]}")
        scripts.append(generate_youtube_longform_script(candidate))

    CHANNEL_DRAFTS_YT = CHANNEL_DRAFTS / "youtube"
    CHANNEL_DRAFTS_YT.mkdir(parents=True, exist_ok=True)
    output_path = CHANNEL_DRAFTS_YT / f"{date_str}-scripts.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scripts, f, ensure_ascii=False, indent=2)
    print(f"[Layer2/YT] 스크립트 {len(scripts)}개 저장 → {output_path}")
    return str(output_path)


def run_instagram(
    claude_candidates: list[dict],
    business_candidates: list[dict],
    trends_candidates: list[dict],
    date_str: str = None,
) -> str:
    """IG 캐러셀 5개 (33/33/33 균형 - 2/2/1 또는 1/2/2 랜덤 배분)"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    # 5개 = 2/2/1 카테고리 분배 (매일 다르게)
    distribution = random.choice([
        ("claude_news", 2), ("ai_business", 2), ("ai_trends", 1),
    ])
    # 간단히 고정 배분: 2/2/1
    plan = [
        ("claude_news", claude_candidates[:2]),
        ("ai_business", business_candidates[:2]),
        ("ai_trends", trends_candidates[:1]),
    ]

    carousels = []
    for category, cands in plan:
        for c in cands:
            print(f"[Layer2/IG] {category}: {c.get('title', '')[:50]}")
            carousels.append(generate_instagram_carousel(c, category))

    CHANNEL_DRAFTS_IG = CHANNEL_DRAFTS / "instagram"
    CHANNEL_DRAFTS_IG.mkdir(parents=True, exist_ok=True)
    output_path = CHANNEL_DRAFTS_IG / f"{date_str}-carousels.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(carousels, f, ensure_ascii=False, indent=2)
    print(f"[Layer2/IG] 캐러셀 {len(carousels)}개 저장 → {output_path}")
    return str(output_path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python script_generator.py <youtube|instagram>")
        sys.exit(1)
    mode = sys.argv[1]
    if mode == "youtube":
        sample = [{"title": "OpenAI's latest model reveals shocking capabilities", "channel": "@mreflow", "view_count": 500000, "url": "https://youtu.be/example"}]
        run_youtube(sample)
    elif mode == "instagram":
        s = [{"title": "Anthropic launches Claude 4", "description": "Major update", "url": "https://anthropic.com/news/claude-4", "source_platform": "anthropic_official"}]
        run_instagram(s, s, s)
