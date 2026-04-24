"""
AI Engine for ERP Demo — Follow-ups, speed-to-lead, quote suggestions, reporting.
Uses Claude Haiku (cheap). Graceful fallback if ANTHROPIC_API_KEY missing.
"""

import os
from datetime import datetime
from pathlib import Path

for _p in [Path(__file__).parent / ".env", Path(__file__).parent.parent / ".env",
           Path(__file__).parent.parent.parent / ".env"]:
    if _p.exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=_p)
        break

_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


def _has_api() -> bool:
    return bool(_API_KEY)


def _call_haiku(system: str, user: str) -> str:
    """Call Claude Haiku. Returns empty string on failure."""
    if not _has_api():
        return ""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=_API_KEY)
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=800,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return resp.content[0].text
    except Exception:
        return ""


# ─── Rule-Based (no API, instant) ─────────────────────────

NEXT_ACTION_RULES = {
    ("lead", 0): "새 리드 - 24시간 내 첫 연락 추천",
    ("lead", 3): "리드 3일 경과 - 즉시 첫 연락 필요",
    ("lead", 7): "리드 1주 경과 - 긴급: 연락 없으면 이탈 위험",
    ("contacted", 0): "연락 완료 - 반응 대기 중",
    ("contacted", 3): "연락 후 3일 무응답 - 카카오톡 팔로업 추천",
    ("contacted", 7): "연락 후 1주 무응답 - 전화 팔로업 추천",
    ("contacted", 14): "2주 무응답 - 마지막 팔로업 또는 보류 처리",
    ("quoted", 0): "견적 발송 완료 - 3일 내 팔로업 예정",
    ("quoted", 3): "견적 발송 3일 경과 - 카카오톡 팔로업 추천",
    ("quoted", 7): "견적 1주 경과 - 전화로 의사결정 확인",
    ("quoted", 14): "견적 2주 경과 - 할인 또는 조건 변경 제안",
    ("converted", 0): "계약 완료 - 온보딩 진행",
    ("retainer", 0): "리테이너 고객 - 월간 리포트 준비",
    ("retainer", 30): "리테이너 갱신일 접근 - 갱신 논의 필요",
    ("churned", 0): "이탈 고객 - 재활성화 캠페인 대상",
}


def get_next_action(client: dict, last_interaction_days: int) -> str:
    """Rule-based next-action recommendation. No API call."""
    status = client.get("status", "lead")

    # Find the best matching rule (closest days threshold that doesn't exceed actual)
    best_msg = ""
    best_days = -1
    for (s, d), msg in NEXT_ACTION_RULES.items():
        if s == status and d <= last_interaction_days and d > best_days:
            best_days = d
            best_msg = msg

    if best_msg:
        return best_msg
    return f"상태: {status} — 특별한 조치 불필요"


# ─── API-Powered (Claude Haiku) ────────────────────────────

def generate_followup(client: dict, interactions: list[dict]) -> str:
    """Generate Korean follow-up message draft based on interaction history."""
    if not _has_api():
        return "[AI 비활성] ANTHROPIC_API_KEY를 .env에 설정하면 자동 팔로업이 생성됩니다."

    history = "\n".join(
        f"- [{i['type']}] {i['created_at']}: {i['content']}"
        for i in interactions[:5]
    )
    return _call_haiku(
        system="You are a Korean business communication expert. Write a natural, professional KakaoTalk follow-up message. Keep it under 100 words. Be warm but direct. Do not use emojis excessively.",
        user=f"""고객 정보:
- 이름: {client['name']}
- 상호: {client['business_name']}
- 상태: {client['status']}
- GEO 점수: {client.get('geo_score', 'N/A')}

최근 상호작용:
{history or '없음'}

이 고객에게 보낼 팔로업 메시지를 작성해주세요. 카카오톡 스타일로."""
    ) or "팔로업 메시지 생성에 실패했습니다."


def generate_speed_to_lead_message(client: dict, geo_score: int | None = None,
                                    weak_dims: list[str] | None = None) -> str:
    """Generate personalized outreach for a new lead based on GEO weak spots."""
    if not _has_api():
        return "[AI 비활성] ANTHROPIC_API_KEY를 .env에 설정하면 자동 아웃리치 메시지가 생성됩니다."

    dims_text = ", ".join(weak_dims) if weak_dims else "전반적 개선 필요"
    return _call_haiku(
        system="You are a Korean GEO (Generative Engine Optimization) consultant. Write a cold outreach KakaoTalk message to a business owner. Be respectful, mention SKKU, offer free audit. Under 80 words. Professional Korean.",
        user=f"""대상 업체:
- 상호: {client['business_name']}
- 웹사이트: {client.get('website', 'N/A')}
- GEO 점수: {geo_score or 'N/A'}/100
- 취약 항목: {dims_text}

성균관대 경영학과 재학 중인 AI 컨설턴트로서, 이 업체에 무료 GEO 진단을 제안하는 첫 메시지를 작성해주세요."""
    ) or "아웃리치 메시지 생성에 실패했습니다."


def generate_reactivation_message(client: dict, old_score: int | None = None,
                                   new_score: int | None = None) -> str:
    """Generate re-engagement message for churned/cold clients."""
    if not _has_api():
        return "[AI 비활성] ANTHROPIC_API_KEY를 .env에 설정하면 재활성화 메시지가 생성됩니다."

    score_change = ""
    if old_score is not None and new_score is not None:
        diff = new_score - old_score
        if diff < 0:
            score_change = f"지난 진단 대비 GEO 점수가 {abs(diff)}점 하락했습니다."
        elif diff > 0:
            score_change = f"지난 진단 대비 GEO 점수가 {diff}점 상승했습니다."

    return _call_haiku(
        system="You are a Korean business consultant re-engaging a past client. Be warm, reference past work, create urgency without being pushy. Under 80 words. Professional Korean.",
        user=f"""고객 정보:
- 이름: {client['name']}
- 상호: {client['business_name']}
- 이전 상태: {client.get('status', 'churned')}
- {score_change or '점수 변화 데이터 없음'}

이 고객에게 다시 연락하는 재활성화 메시지를 작성해주세요."""
    ) or "재활성화 메시지 생성에 실패했습니다."


def suggest_quote_items(client: dict) -> list[dict]:
    """AI-suggest line items based on client type and GEO score."""
    if not _has_api():
        return [
            {"description": "GEO 진단 리포트", "quantity": 1, "unit_price": 500000},
            {"description": "구현 파일 패키지 (llms.txt, robots.txt, schema.org)", "quantity": 1, "unit_price": 300000},
        ]

    import json
    raw = _call_haiku(
        system="""You are a Korean GEO consultant pricing engine. Return ONLY a JSON array of line items.
Each item: {"description": "Korean description", "quantity": 1, "unit_price": integer_KRW}
Available services:
- GEO 진단 리포트 (500,000 KRW)
- 구현 파일 패키지 llms.txt/robots.txt/schema.org (300,000 KRW)
- AI 검색 최적화 컨설팅 1회 (200,000 KRW)
- 월간 GEO 모니터링 (1,500,000 KRW/month)
- 웹사이트 구조 개선 (800,000 KRW)
- 콘텐츠 최적화 (400,000 KRW)
Return 2-4 items appropriate for the client. JSON only, no explanation.""",
        user=f"""고객: {client['business_name']}
업종: {client.get('notes', 'N/A')}
GEO 점수: {client.get('geo_score', 'N/A')}/100
웹사이트: {client.get('website', 'N/A')}""",
    )
    try:
        items = json.loads(raw)
        if isinstance(items, list) and all("description" in i and "unit_price" in i for i in items):
            return items
    except (json.JSONDecodeError, TypeError):
        pass
    return [
        {"description": "GEO 진단 리포트", "quantity": 1, "unit_price": 500000},
        {"description": "구현 파일 패키지 (llms.txt, robots.txt, schema.org)", "quantity": 1, "unit_price": 300000},
    ]


def generate_weekly_report(stats: dict) -> str:
    """Generate Korean weekly summary paragraph."""
    if not _has_api():
        total = stats.get("total_clients", 0)
        conv = stats.get("conversion_rate", 0)
        rev = stats.get("monthly_revenue", 0)
        oq = stats.get("open_quotes", 0)
        return (f"이번 주 현황: 총 고객 {total}명, 전환율 {conv}%, "
                f"이번 달 매출 {rev:,}원, 미결 견적 {oq:,}원")

    return _call_haiku(
        system="You are a Korean business analyst. Write a concise weekly business summary in Korean. 3-4 sentences max. Include key metrics and one actionable recommendation.",
        user=f"""이번 주 지표:
- 총 고객: {stats.get('total_clients', 0)}명
- 전환율: {stats.get('conversion_rate', 0)}%
- 이번 달 매출: {stats.get('monthly_revenue', 0):,}원
- 미결 견적 금액: {stats.get('open_quotes', 0):,}원
- 만료 임박 견적: {stats.get('expiring_quotes', 0)}건
- 미수금 청구서: {stats.get('overdue_invoices', 0)}건
- 이탈 위험 리드: {stats.get('cold_leads', 0)}명

주간 요약 리포트를 작성해주세요."""
    ) or "주간 리포트 생성에 실패했습니다."
