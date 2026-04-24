"""
Layer 3: 자막 한국어 번역 (AI 용어 정확성 유지)
"""
import json
import os
from pathlib import Path

import anthropic


def translate_transcript(transcript: list[dict], source_lang: str = "en") -> list[dict]:
    if not transcript:
        return []

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    full_text = "\n".join(
        f"[{seg['start']:.1f}-{seg['end']:.1f}] {seg['text']}"
        for seg in transcript
    )

    prompt = f"""다음은 {source_lang} AI 관련 영상의 자막이야.
한국 AI 엔지니어/업계인을 위해 자연스러운 한국어로 번역해줘.

원칙:
- AI 용어는 영어 그대로 유지 (LLM, RAG, MCP, agent, embedding, fine-tune, prompt, context window 등)
- 회사명/제품명 영어 유지 (Anthropic, Claude, OpenAI, GPT, LangGraph 등)
- 문장은 한국어 구어체 (~했어요, ~라고 해요)
- 시간 코드 유지

자막:
{full_text[:4000]}

JSON 배열만 출력:
[{{"start": 0.0, "end": 1.5, "text": "번역된 한국어"}}]"""

    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text.strip()
        start = text.find("[")
        end = text.rfind("]") + 1
        return json.loads(text[start:end])
    except Exception as e:
        print(f"[WARN] 번역 실패: {e}")
        return transcript


def process(highlights_path: str) -> dict:
    with open(highlights_path, encoding="utf-8") as f:
        data = json.load(f)

    transcript = data.get("transcript", [])
    translated = translate_transcript(transcript)

    data["transcript_ko"] = translated
    with open(highlights_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[Translator] {len(translated)}개 세그먼트 번역 → {highlights_path}")
    return data


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python translator.py <highlights_json>")
        sys.exit(1)
    process(sys.argv[1])
