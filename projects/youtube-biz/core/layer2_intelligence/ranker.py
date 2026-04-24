"""
Layer 2: 후보 아이템 랭킹
채널별 dimensions으로 Claude Haiku 채점 후 top-N 선정
"""
import json
import os
from pathlib import Path

import anthropic

BASE_DIR = Path(__file__).resolve().parents[3]

DIMENSIONS = {
    "first_mover_ai_youtube": ["virality_signal", "korean_market_relevance", "translatability", "longform_retention"],
    "first_mover_ai_instagram_claude": ["news_freshness", "claude_specificity", "hook_strength", "shareability"],
    "first_mover_ai_instagram_business": ["news_freshness", "korean_market_relevance", "numeric_clarity", "shareability"],
    "first_mover_ai_instagram_trends": ["hook_strength", "trend_alignment", "evolving_ai_style", "shareability"],
}

DIMENSION_DESCRIPTIONS = {
    "virality_signal": "원본 영상의 조회수/반응 강도 (바이럴 가능성) (0-10)",
    "korean_market_relevance": "한국 AI 엔지니어/업계에 직접적 시사점 (0-10)",
    "translatability": "한국어 번역/재편집해도 메시지 유지되는 정도 (0-10)",
    "longform_retention": "10-20분 롱폼으로 풀어낼 깊이 있는가 (0-10)",
    "news_freshness": "뉴스의 최신성 (48시간 이내 = 10) (0-10)",
    "claude_specificity": "Claude/Anthropic에 직접 관련되는 정도 (0-10)",
    "hook_strength": "첫 3초 호기심 유발 강도 (0-10)",
    "shareability": "IG Stories 공유 가능성 (0-10)",
    "numeric_clarity": "금액/수치/통계 명확성 (사업 뉴스) (0-10)",
    "trend_alignment": "현재 AI 트렌드와의 부합도 (0-10)",
    "evolving_ai_style": "evolving.ai 스타일 — 반전/흥미 훅 적합도 (0-10)",
}


def score_candidates(candidates: list[dict], channel: str, top_n: int = 5) -> list[dict]:
    if not candidates:
        return []

    dims = DIMENSIONS.get(channel, DIMENSIONS["first_mover_ai_youtube"])
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    scored = []
    for candidate in candidates:
        title = candidate.get("title", "")
        description = candidate.get("description", "")
        view_count = candidate.get("view_count") or candidate.get("votes") or 0

        dim_prompts = "\n".join(
            f"- {d} ({DIMENSION_DESCRIPTIONS.get(d, '')}): ?" for d in dims
        )

        prompt = f"""다음 컨텐츠 후보를 '{channel}' 채널 기준으로 채점해줘.

제목: {title}
설명: {description}
조회수/반응: {view_count}

다음 차원에서 각각 0-10점으로 채점하고, 평균 점수도 계산해줘:
{dim_prompts}

응답 형식 (JSON만):
{{"scores": {{{", ".join(f'"{d}": 0' for d in dims)}}}, "average": 0.0, "reason": "한 문장 이유"}}"""

        try:
            resp = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            text = resp.content[0].text.strip()
            # JSON 추출
            start = text.find("{")
            end = text.rfind("}") + 1
            result = json.loads(text[start:end])
            candidate["scores"] = result.get("scores", {})
            candidate["score_average"] = result.get("average", 0.0)
            candidate["score_reason"] = result.get("reason", "")
        except Exception as e:
            candidate["scores"] = {}
            candidate["score_average"] = view_count / 1_000_000 * 5  # 조회수 fallback
            candidate["score_reason"] = f"채점 실패: {e}"

        scored.append(candidate)

    scored.sort(key=lambda x: x.get("score_average", 0), reverse=True)
    return scored[:top_n]


def run(inbox_path: str, channel: str, top_n: int = 5) -> list[dict]:
    with open(inbox_path, encoding="utf-8") as f:
        candidates = json.load(f)

    top = score_candidates(candidates, channel, top_n)
    print(f"[Layer2] {channel} 채점 완료: {len(candidates)}개 → top {len(top)}개 선정")
    for i, c in enumerate(top, 1):
        print(f"  {i}. [{c.get('score_average', 0):.1f}] {c.get('title', '')[:50]}")
    return top


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python ranker.py <inbox_json_path> <channel>")
        sys.exit(1)
    results = run(sys.argv[1], sys.argv[2])
    print(json.dumps(results, ensure_ascii=False, indent=2))
