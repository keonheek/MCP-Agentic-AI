"""
GPT-4o message generator for hagwon parent alimtalk.
Loads hagwon-specific voice/style sheet and generates natural Korean messages.
"""
import os
import json
from pathlib import Path
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

STYLE_SHEET_PATH = Path(__file__).parent.parent / "data" / "style_sheet.json"

SYSTEM_PROMPT = """당신은 한국 학원의 학부모 소통 전문가입니다.
주어진 학원 말투 시트를 반드시 참고하여 자연스럽고 따뜻한 한국어 알림톡 메시지를 작성합니다.
규칙:
- 90자 이내로 작성 (카카오 알림톡 권장 길이)
- 경어체 유지 (존댓말)
- 학원 이름은 [학원명]으로 표기
- 학생 이름은 직접 사용
- 감정적이거나 비판적인 표현 금지
"""


def _load_style_sheet() -> str:
    if STYLE_SHEET_PATH.exists():
        data = json.loads(STYLE_SHEET_PATH.read_text(encoding="utf-8"))
        return "\n".join(data.get("examples", []))
    return "기본 정중한 어체로 작성해주세요."


def generate_alimtalk(event_type: str, student_name: str, details: dict) -> str:
    """Generate a single alimtalk message using GPT-4o."""
    style_examples = _load_style_sheet()

    user_prompt = f"""
이벤트 유형: {event_type}
학생 이름: {student_name}
세부 정보: {json.dumps(details, ensure_ascii=False)}

학원 말투 예시:
{style_examples}

위 예시와 동일한 말투로 알림톡 메시지를 1개 작성해주세요.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=200,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


EVENT_TEMPLATES = {
    "attendance": "출결 알림",
    "homework": "숙제 알림",
    "progress": "진도 알림",
    "notice": "공지 알림",
    "consultation": "상담 알림",
}
