"""
Government grant application draft generator.
Combines RAG search results with GPT-4o structured generation.
"""
import os
import json
from openai import OpenAI
from rag_engine import search

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """당신은 한국 정부지원사업 신청서 전문 작성자입니다.
과거 합격 사례를 참고하여, 심사위원이 선호하는 구조와 키워드로 각 질문에 답변합니다.

규칙:
- 각 답변은 200-400자로 작성
- 구체적인 숫자와 근거 포함 (예: "시장 규모 5조원", "월 평균 고객 100명")
- 지나친 형용사 사용 금지 ("최고", "혁신적" 등)
- 신청자의 실제 사업 정보를 기반으로 작성
- 심사 기준에 맞는 키워드 자연스럽게 포함
"""

STANDARD_QUESTIONS = {
    "모두의창업": [
        "Q1. 창업 동기 및 문제 인식",
        "Q2. 목표 고객 및 시장 규모",
        "Q3. 제품/서비스 차별점",
        "Q4. 비즈니스 모델 (수익 구조)",
        "Q5. 팀 구성 및 역량",
        "Q6. 사업 추진 일정",
        "Q7. 자금 사용 계획",
        "Q8. 기대 성과 및 목표",
        "Q9. 사회적 가치 및 지속가능성",
    ],
    "소상공인진흥공단": [
        "Q1. 사업 개요",
        "Q2. 현재 운영 현황",
        "Q3. 지원 필요성",
        "Q4. 지원금 사용 계획",
        "Q5. 기대 효과",
    ],
}


def generate_draft(program: str, business_info: dict) -> dict:
    """
    Generate full grant application draft.
    Returns dict with question: answer pairs.
    """
    questions = STANDARD_QUESTIONS.get(program, STANDARD_QUESTIONS["모두의창업"])
    similar_cases = search(f"{program} {business_info.get('business_idea', '')}", top_k=3)
    context = "\n\n---\n\n".join([c["text"][:500] for c in similar_cases])

    draft = {}
    for question in questions:
        user_prompt = f"""
프로그램: {program}
질문: {question}
신청자 사업 정보: {json.dumps(business_info, ensure_ascii=False)}

참고 합격 사례 (일부):
{context}

위 질문에 대한 답변을 작성해주세요.
"""
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=400,
            temperature=0.3,
        )
        draft[question] = resp.choices[0].message.content.strip()

    return draft
