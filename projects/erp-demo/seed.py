"""
Seed demo data — 14 Korean SME clients across 세무사, 카페, 음식점, e커머스, 병원 industries.
Target KPIs: 3.5M open quotes | 2M monthly revenue | 58% conversion rate
"""

from datetime import datetime, timedelta
from db import (
    init_db, create_client, add_interaction, create_quote,
    update_quote_status, create_invoice_from_quote, update_invoice_status,
    update_client, queue_message, total_clients, get_db,
)


def _pay_invoice_on(invoice_id: int, paid_date: str) -> None:
    """Mark invoice paid with a specific historical date (bypasses update_invoice_status)."""
    with get_db() as conn:
        conn.execute(
            "UPDATE invoices SET status = 'paid', paid_at = ? WHERE id = ?",
            (paid_date, invoice_id),
        )


def seed_all():
    """Seed 14 realistic demo clients with full pipeline data."""
    if total_clients() > 0:
        return

    now = datetime.now()
    today = now.strftime("%Y-%m-%d")

    # ─── LEADS (4 clients) ────────────────────────────────────────────

    c1 = create_client(
        name="김세무", business_name="김세무 세무사사무소",
        phone="010-1234-5678", kakao_id="tax_kim",
        website="https://kimtax.co.kr", source="naver",
        geo_score=22,
        notes="강남 세무사. ChatGPT '강남 세무사 추천' 검색 시 안 나옴.",
    )
    queue_message(c1, "speed_to_lead",
        "안녕하세요, 김세무 세무사님! SKKU 경영학과 AI 컨설턴트 김건희입니다. "
        "ChatGPT에서 '강남 세무사 추천'을 검색하면 경쟁 사무소가 먼저 나옵니다. "
        "무료 AI 검색 진단 리포트를 드리겠습니다. 관심 있으시면 답변 부탁드립니다!"
    )

    c2 = create_client(
        name="이부동산", business_name="이씨 부동산 공인중개사",
        phone="010-2233-4455", kakao_id="lee_realty",
        website="https://leerealty.kr", source="naver",
        geo_score=18,
        notes="강동구 공인중개사. '강동 빌라 매매 중개' 검색 노출 0.",
    )

    c3 = create_client(
        name="박약국", business_name="박약사 약국",
        phone="02-333-9988", kakao_id="park_pharmacy",
        website="https://parkrx.co.kr", source="soomgo",
        geo_score=31,
        notes="숨고 문의. '마포 약국' 검색 순위 10위권 밖.",
    )

    # ─── CONTACTED (1 client) ─────────────────────────────────────────

    c5 = create_client(
        name="한정식", business_name="한씨정통한정식",
        phone="02-555-7777", email="han@hanjeongsik.kr",
        kakao_id="hanjeongsik_official", website="https://hanjeongsik.kr",
        source="kakao", status="contacted", geo_score=35,
        notes="강남 한정식. 법인카드 단골 식당. '강남 접대 식당' 검색 노출 목표.",
    )
    add_interaction(c5, "kakao", "첫 연락 — 무료 GEO 진단 제안. '관심 있다' 답변 받음.")
    add_interaction(c5, "note", "GEO 점수 35점. schema.org 없음, llms.txt 없음.")

    # ─── QUOTED (2 clients — open quotes = 1.8M + 1.7M = 3.5M) ──────

    c6 = create_client(
        name="최피부", business_name="최피부과의원",
        phone="02-555-1234", email="choi@choiskinclinic.com",
        kakao_id="choiskinclinic", website="https://choiskinclinic.com",
        source="soomgo", status="quoted", geo_score=42,
        notes="프리미엄 피부과. 환자 50%가 ChatGPT로 '강남 피부과 추천' 검색.",
    )
    add_interaction(c6, "call", "숨고 문의. 전화 상담 진행.")
    add_interaction(c6, "meeting", "줌 미팅 30분. GEO 진단 결과 설명. 견적서 요청.")
    add_interaction(c6, "email", "견적서 발송 완료.")
    q6 = create_quote(
        client_id=c6, title="GEO 최적화 패키지 (피부과 특화)",
        items=[
            {"description": "GEO 진단 리포트 (5개 카테고리, 10개 항목)", "quantity": 1, "unit_price": 500000},
            {"description": "구현 파일 패키지 (llms.txt, schema.org, robots.txt)", "quantity": 1, "unit_price": 300000},
            {"description": "웹사이트 구조 개선 (의료 특화 마크업)", "quantity": 1, "unit_price": 800000},
            {"description": "AI 검색 최적화 컨설팅 1회 (60분)", "quantity": 1, "unit_price": 200000},
        ],
        valid_until=(now + timedelta(days=14)).strftime("%Y-%m-%d"),
        notes="부가세 별도. 납품 기한: 계약 후 1주일.",
    )
    update_quote_status(q6, "sent")

    c7 = create_client(
        name="정변호사", business_name="정앤파트너스 법률사무소",
        phone="02-777-5555", email="jung@junglaw.kr",
        kakao_id="jung_partners", website="https://junglaw.kr",
        source="referral", status="quoted", geo_score=39,
        notes="서초 법률사무소. 소개로 연락. '서초 법률사무소 추천' 검색 노출 관심.",
    )
    add_interaction(c7, "kakao", "최변호사 소개로 연락 옴.")
    add_interaction(c7, "meeting", "대면 미팅 1시간. GEO 진단 설명.")
    add_interaction(c7, "email", "견적서 발송.")
    q7 = create_quote(
        client_id=c7, title="GEO 진단 + 구현 패키지 (법무 특화)",
        items=[
            {"description": "GEO 진단 리포트", "quantity": 1, "unit_price": 500000},
            {"description": "구현 파일 패키지", "quantity": 1, "unit_price": 300000},
            {"description": "웹사이트 구조 개선 (법무 특화 스키마)", "quantity": 1, "unit_price": 800000},
            {"description": "콘텐츠 최적화 (판례 기반 FAQ 5개)", "quantity": 1, "unit_price": 100000},
        ],
        valid_until=(now + timedelta(days=10)).strftime("%Y-%m-%d"),
    )
    update_quote_status(q7, "sent")

    # ─── CONVERTED (6 clients — historical revenue trend) ────────────

    def _make_converted(name, biz, phone, email, kakao, website, source, geo, notes,
                        quote_items, paid_date):
        c = create_client(
            name=name, business_name=biz, phone=phone, email=email,
            kakao_id=kakao, website=website, source=source,
            status="converted", geo_score=geo, notes=notes,
        )
        add_interaction(c, "kakao", "문의 인입.")
        add_interaction(c, "meeting", "GEO 진단 미팅 완료.")
        add_interaction(c, "call", "견적 수락. 착수금 입금.")
        add_interaction(c, "note", "구현 파일 전달 완료.")
        q = create_quote(
            client_id=c, title="GEO 최적화 패키지",
            items=quote_items,
            valid_until=(now - timedelta(days=10)).strftime("%Y-%m-%d"),
        )
        update_quote_status(q, "accepted")
        update_client(c, status="converted")
        inv = create_invoice_from_quote(q)
        _pay_invoice_on(inv, paid_date + " 14:00:00")
        return c

    _make_converted(
        "김카페", "김씨 스페셜티 카페", "010-3344-5566", "kim@kimcafe.kr",
        "kimcafe_official", "https://kimcafe.kr", "naver", 61,
        "성수동 스페셜티 카페. '성수 카페 추천' AI 검색 점수 61로 개선.",
        [
            {"description": "GEO 진단 리포트", "quantity": 1, "unit_price": 500000},
            {"description": "구현 파일 패키지", "quantity": 1, "unit_price": 300000},
            {"description": "웹사이트 구조 개선", "quantity": 1, "unit_price": 800000},
        ],
        "2025-11-15",
    )

    _make_converted(
        "이치과", "이브라이트 치과의원", "02-888-4321", "lee@leebrightdental.com",
        "leebright_dental", "https://leebrightdental.com", "soomgo", 67,
        "신촌 치과. '신촌 치과 추천' 점수 67. 구글맵 리뷰 최적화 추가.",
        [
            {"description": "GEO 진단 리포트", "quantity": 1, "unit_price": 500000},
            {"description": "구현 파일 패키지", "quantity": 1, "unit_price": 300000},
            {"description": "콘텐츠 최적화 (FAQ 10개)", "quantity": 1, "unit_price": 400000},
            {"description": "AI 검색 컨설팅 1회", "quantity": 1, "unit_price": 200000},
        ],
        "2025-12-08",
    )

    _make_converted(
        "박학원", "박씨 영어학원", "010-5566-7788", "park@parkenglishshool.com",
        "park_english", "https://parkenglish.co.kr", "naver", 55,
        "목동 영어학원. '목동 영어학원 추천' 검색 순위 5위 → 1위 목표.",
        [
            {"description": "GEO 진단 리포트", "quantity": 1, "unit_price": 500000},
            {"description": "구현 파일 패키지", "quantity": 1, "unit_price": 300000},
            {"description": "웹사이트 구조 개선", "quantity": 1, "unit_price": 800000},
        ],
        "2026-01-20",
    )

    _make_converted(
        "최이커머스", "최씨 패션몰 (e커머스)", "010-9900-1122",
        "choi@choifashionmall.com", "choifashion_kr",
        "https://choifashionmall.com", "kmong", 63,
        "동대문 패션 이커머스. 해외 바이어 AI 검색 대응. 영문 llms.txt 포함.",
        [
            {"description": "GEO 진단 리포트 (영문 포함)", "quantity": 1, "unit_price": 600000},
            {"description": "구현 파일 패키지 (영문/한문)", "quantity": 1, "unit_price": 400000},
            {"description": "웹사이트 구조 개선", "quantity": 1, "unit_price": 800000},
        ],
        "2026-02-10",
    )

    _make_converted(
        "한헬스", "한씨 헬스클럽", "02-444-8888", "han@hanfitness.kr",
        "han_fitness", "https://hanfitness.kr", "kakao", 58,
        "강남 헬스장. '강남 PT 추천' ChatGPT 검색 대응. 회원권 전환율 증가 목표.",
        [
            {"description": "GEO 진단 리포트", "quantity": 1, "unit_price": 500000},
            {"description": "구현 파일 패키지", "quantity": 1, "unit_price": 300000},
            {"description": "콘텐츠 최적화", "quantity": 1, "unit_price": 400000},
        ],
        "2026-03-05",
    )

    _make_converted(
        "유노무", "유씨 노무법인", "02-222-3344", "yoo@yoolaborlaw.kr",
        "yoo_labor", "https://yoolaborlaw.kr", "naver", 52,
        "서울 노무법인. '서울 노무사 추천' 검색 최적화. 중소기업 HR 의뢰 증가 목표.",
        [
            {"description": "GEO 진단 리포트", "quantity": 1, "unit_price": 500000},
            {"description": "구현 파일 패키지", "quantity": 1, "unit_price": 300000},
        ],
        "2026-03-22",
    )

    # ─── RETAINER (2 clients — THIS MONTH revenue = 1M + 1M = 2M) ───

    c_ret1 = create_client(
        name="정코스메틱", business_name="정씨코스메틱 (화장품 이커머스)",
        phone="010-9876-5432", email="jung@jungcosmetic.co.kr",
        kakao_id="jung_cosmetic", website="https://jungcosmetic.co.kr",
        source="kmong", status="retainer", geo_score=74,
        notes="화장품 이커머스. 해외 바이어가 'Korean cosmetics supplier' AI 검색. GEO 42→74 개선.",
    )
    add_interaction(c_ret1, "kakao", "크몽에서 GEO 진단 의뢰.")
    add_interaction(c_ret1, "meeting", "줌 미팅. 진단 + 구현 + 리테이너 패키지 제안.")
    add_interaction(c_ret1, "email", "계약서 발송.")
    add_interaction(c_ret1, "call", "계약 완료. 월간 리테이너 시작.")
    add_interaction(c_ret1, "note", "1차 GEO 점수 42 → 74. 만족도 높음. 재계약 예정.")
    add_interaction(c_ret1, "meeting", "월간 리뷰. 콘텐츠 최적화 추가 요청.")
    q_ret1 = create_quote(
        client_id=c_ret1, title="GEO 종합 패키지 + 월간 리테이너",
        items=[
            {"description": "GEO 진단 리포트", "quantity": 1, "unit_price": 500000},
            {"description": "구현 파일 패키지", "quantity": 1, "unit_price": 300000},
            {"description": "웹사이트 구조 개선", "quantity": 1, "unit_price": 800000},
            {"description": "콘텐츠 최적화", "quantity": 1, "unit_price": 400000},
        ],
        valid_until=(now - timedelta(days=60)).strftime("%Y-%m-%d"),
    )
    update_quote_status(q_ret1, "accepted")
    inv_ret1_onboarding = create_invoice_from_quote(q_ret1)
    _pay_invoice_on(inv_ret1_onboarding, "2026-02-28 14:00:00")

    # Monthly retainer invoice (this month)
    from db import create_invoice_manual
    inv_ret1_monthly = create_invoice_manual(c_ret1, 1000000,
                                              (now + timedelta(days=30)).strftime("%Y-%m-%d"))
    _pay_invoice_on(inv_ret1_monthly, today + " 10:00:00")

    c_ret2 = create_client(
        name="한컨설팅", business_name="한앤김 경영컨설팅",
        phone="010-1111-2222", email="han@hankimconsulting.com",
        kakao_id="hankim_consulting", website="https://hankimconsulting.com",
        source="referral", status="retainer", geo_score=69,
        notes="중소기업 경영컨설팅. '중소기업 컨설팅 추천' ChatGPT 점수 42→69. 기업 고객 소개 활발.",
    )
    add_interaction(c_ret2, "kakao", "소개로 연락. GEO 진단 관심 높음.")
    add_interaction(c_ret2, "meeting", "대면 미팅. 포트폴리오 설명. 리테이너 관심.")
    add_interaction(c_ret2, "email", "계약서 + 첫 진단 결과 발송.")
    add_interaction(c_ret2, "call", "리테이너 계약 완료.")
    add_interaction(c_ret2, "note", "월간 모니터링 + 분기 콘텐츠 업데이트 포함.")
    q_ret2 = create_quote(
        client_id=c_ret2, title="GEO 진단 + 월간 모니터링",
        items=[
            {"description": "GEO 진단 리포트", "quantity": 1, "unit_price": 500000},
            {"description": "구현 파일 패키지", "quantity": 1, "unit_price": 300000},
            {"description": "웹사이트 구조 개선", "quantity": 1, "unit_price": 800000},
        ],
        valid_until=(now - timedelta(days=30)).strftime("%Y-%m-%d"),
    )
    update_quote_status(q_ret2, "accepted")
    inv_ret2_onboarding = create_invoice_from_quote(q_ret2)
    _pay_invoice_on(inv_ret2_onboarding, "2026-03-15 14:00:00")

    # Monthly retainer invoice (this month)
    inv_ret2_monthly = create_invoice_manual(c_ret2, 1000000,
                                              (now + timedelta(days=30)).strftime("%Y-%m-%d"))
    _pay_invoice_on(inv_ret2_monthly, today + " 11:00:00")

    print("Seeded 14 clients: open quotes 3.5M | monthly revenue 2M | conversion 57%")


if __name__ == "__main__":
    init_db()
    seed_all()
