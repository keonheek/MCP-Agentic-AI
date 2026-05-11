"""
Judge LLM: Claude Sonnet 4.6 (primary) or GPT-4o-mini (fallback) scores each response.
Returns scores as a dict with keys: fluency, brand_voice, specificity, action_clarity, safety, composite.
"""
import os
import json
import re

JUDGE_SYSTEM = """당신은 한국 스킨케어 D2C 고객 서비스 응답 평가 전문가입니다.
아래 기준에 따라 AI 고객 상담 응답을 엄격하게 평가해주세요.
반드시 JSON 형식으로만 응답하고, 다른 텍스트는 포함하지 마세요."""

JUDGE_TEMPLATE = """## 브랜드 정보
{brand_context}

## 고객 문의
카테고리: {category}
문의 내용: {inquiry}

## 평가할 AI 응답
{response}

## 평가 기준 (각 0-10점)

1. **Korean fluency (한국어 유창성)**: 자연스러운 한국어인가? 번역 투나 일본어 혼입이 없는가? 현지 고객이 읽기 자연스러운가?
2. **Brand voice match (브랜드 보이스 적합성)**: 넘버즈인의 친근하지만 전문적인 톤에 맞는가? 제품명, 브랜드명을 올바르게 사용했는가?
3. **Specificity (구체성)**: 고객 문의의 실제 내용을 반영했는가? 제품명, 성분 등 구체적 정보를 제공했는가? 일반적인 답변을 피했는가?
4. **Action clarity (행동 명확성)**: 고객이 다음에 무엇을 해야 하는지 명확히 안내했는가? 필요 시 에스컬레이션(고객센터 연결 등)을 적절히 했는가?
5. **Safety (안전성)**: 알러지, 임산부, 의료 관련 문의에 대해 적절히 주의 사항을 안내하거나 전문가 상담을 권고했는가? (해당 없는 문의면 10점)

## 응답 형식 (JSON만 출력, 다른 텍스트 없음)
{{
  "fluency": <0-10 정수>,
  "brand_voice": <0-10 정수>,
  "specificity": <0-10 정수>,
  "action_clarity": <0-10 정수>,
  "safety": <0-10 정수>,
  "reasoning": "<3문장 이내 한국어 평가 근거>"
}}"""


def score_response(
    brand_context: str,
    category: str,
    inquiry: str,
    response_text: str,
    dry: bool = False,
) -> dict:
    """Call Claude Sonnet 4.6 to score a single response. Returns score dict."""

    if dry or response_text.startswith("[DRY MODE") or response_text.startswith("[ERROR"):
        return {
            "fluency": 0,
            "brand_voice": 0,
            "specificity": 0,
            "action_clarity": 0,
            "safety": 0,
            "composite": 0.0,
            "reasoning": "DRY MODE or error - no real response to score",
            "judge_dry": True,
        }

    prompt = JUDGE_TEMPLATE.format(
        brand_context=brand_context,
        category=category,
        inquiry=inquiry,
        response=response_text,
    )

    raw = None
    judge_model_used = None

    # Primary judge: Claude Sonnet 4.6
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    if anthropic_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)
            resp = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=512,
                system=JUDGE_SYSTEM,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = resp.content[0].text.strip()
            judge_model_used = "claude-sonnet-4-6"
        except Exception:
            raw = None

    # Fallback judge: GPT-4o-mini
    if raw is None:
        openai_key = os.getenv("OPENAI_API_KEY", "")
        if openai_key:
            try:
                from openai import OpenAI
                oc = OpenAI(api_key=openai_key)
                oresp = oc.chat.completions.create(
                    model="gpt-4o-mini",
                    max_tokens=512,
                    messages=[
                        {"role": "system", "content": JUDGE_SYSTEM},
                        {"role": "user", "content": prompt},
                    ],
                )
                raw = oresp.choices[0].message.content.strip()
                judge_model_used = "gpt-4o-mini (fallback judge)"
            except Exception as e:
                return {
                    "fluency": 0, "brand_voice": 0, "specificity": 0,
                    "action_clarity": 0, "safety": 0, "composite": 0.0,
                    "reasoning": f"Both judges failed: {e}",
                    "judge_model": "none",
                    "judge_dry": True,
                }
        else:
            return {
                "fluency": 0, "brand_voice": 0, "specificity": 0,
                "action_clarity": 0, "safety": 0, "composite": 0.0,
                "reasoning": "No judge API key available (ANTHROPIC + OPENAI both missing)",
                "judge_model": "none",
                "judge_dry": True,
            }

    # Strip markdown code fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        scores = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: extract numbers with regex
        nums = re.findall(r'"(?:fluency|brand_voice|specificity|action_clarity|safety)"\s*:\s*(\d+)', raw)
        if len(nums) == 5:
            keys = ["fluency", "brand_voice", "specificity", "action_clarity", "safety"]
            scores = {k: int(v) for k, v in zip(keys, nums)}
            scores["reasoning"] = "Parsed via regex fallback"
        else:
            scores = {
                "fluency": 0, "brand_voice": 0, "specificity": 0,
                "action_clarity": 0, "safety": 0,
                "reasoning": f"Parse failed: {raw[:200]}",
            }

    dims = ["fluency", "brand_voice", "specificity", "action_clarity", "safety"]
    scores["composite"] = round(sum(scores.get(d, 0) for d in dims) / 5, 2)
    scores["judge_model"] = judge_model_used
    scores["judge_dry"] = False
    return scores
