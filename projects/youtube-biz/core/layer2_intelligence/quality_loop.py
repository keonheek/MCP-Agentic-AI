"""
Layer 2: autoresearch 품질 루프 래퍼
기존 .claude/skills/autoresearch Mode 1 패턴 재사용
Haiku 채점 → Sonnet 개선 → 임계값 7.5 도달까지 최대 4회 반복
"""
import json
import os
from pathlib import Path

import anthropic

QUALITY_THRESHOLD = 7.5
MAX_ITERATIONS = 4

SCORE_DIMENSIONS = {
    "singit": ["hook_strength", "translation_quality", "cta_effectiveness", "virality"],
    "ai": ["clarity", "trend_relevance", "actionability", "engagement"],
}


def score_script(script: dict, channel: str, client: anthropic.Anthropic) -> tuple[float, str]:
    dims = SCORE_DIMENSIONS.get(channel, SCORE_DIMENSIONS["ai"])
    content_preview = json.dumps(script, ensure_ascii=False)[:500]

    prompt = f"""다음 YouTube Shorts 스크립트를 '{channel}' 채널 기준으로 채점해줘.

스크립트:
{content_preview}

채점 기준 (각 0-10):
{chr(10).join(f'- {d}' for d in dims)}

JSON만 응답:
{{"scores": {{{", ".join(f'"{d}": 0' for d in dims)}}}, "average": 0.0, "weakest": "가장 약한 항목", "fix_suggestion": "한 문장 개선 제안"}}"""

    try:
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text.strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        result = json.loads(text[start:end])
        return result.get("average", 0.0), result.get("fix_suggestion", "")
    except Exception as e:
        return 5.0, f"채점 실패: {e}"


def improve_script(script: dict, suggestion: str, channel: str, client: anthropic.Anthropic) -> dict:
    content_preview = json.dumps(script, ensure_ascii=False)[:800]

    prompt = f"""다음 {channel} 채널 Shorts 스크립트를 개선해줘.

현재 스크립트:
{content_preview}

개선 제안: {suggestion}

같은 JSON 구조로 개선된 버전만 출력해. 다른 설명 없이 JSON만."""

    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text.strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        improved = json.loads(text[start:end])
        # 원본 메타데이터 유지
        improved["source_candidate"] = script.get("source_candidate")
        improved["generated_at"] = script.get("generated_at")
        return improved
    except Exception:
        return script  # 개선 실패 시 원본 유지


def run_quality_loop(script: dict, channel: str) -> tuple[dict, float, int]:
    """
    Returns: (final_script, final_score, iterations_used)
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    current = script
    iterations = 0

    for i in range(MAX_ITERATIONS):
        score, suggestion = score_script(current, channel, client)
        iterations = i + 1
        print(f"  [QA iter {i+1}] 점수: {score:.1f} / 개선 제안: {suggestion[:60]}")

        if score >= QUALITY_THRESHOLD:
            print(f"  [QA] 임계값 {QUALITY_THRESHOLD} 달성. 완료.")
            return current, score, iterations

        if i < MAX_ITERATIONS - 1:
            current = improve_script(current, suggestion, channel, client)

    final_score, _ = score_script(current, channel, client)
    return current, final_score, iterations


def process_scripts(scripts_path: str, channel: str) -> str:
    with open(scripts_path, encoding="utf-8") as f:
        scripts = json.load(f)

    refined = []
    for script in scripts:
        if "error" in script:
            refined.append(script)
            continue
        title = script.get("source_candidate", {}).get("title", "")[:40]
        print(f"[Layer2/QA] {title}")
        final, score, iters = run_quality_loop(script, channel)
        final["qa_score"] = score
        final["qa_iterations"] = iters
        refined.append(final)

    output_path = scripts_path.replace("-scripts.json", "-scripts-refined.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(refined, f, ensure_ascii=False, indent=2)

    avg = sum(s.get("qa_score", 0) for s in refined) / max(len(refined), 1)
    print(f"[Layer2/QA] 완료. 평균 품질 점수: {avg:.1f} | 저장: {output_path}")
    return output_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python quality_loop.py <scripts_json_path> <channel>")
        sys.exit(1)
    process_scripts(sys.argv[1], sys.argv[2])
