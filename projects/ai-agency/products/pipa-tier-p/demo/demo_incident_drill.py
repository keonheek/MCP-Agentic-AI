"""
demo_incident_drill.py
----------------------
Simulates a realistic breach scenario for a Korean cosmetics D2C brand.
Walks through the full 72-hour PIPA Art. 34 response process.

Run: python demo/demo_incident_drill.py
No API calls, no external dependencies beyond stdlib.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import datetime
import time
from src.breach_responder import (
    BreachEvent,
    assess_severity,
    compute_deadlines,
    generate_pipc_notification,
    generate_individual_notice,
    run_breach_timeline,
)
from src.audit_logger import log_breach, log_event
from src.pii_redactor import redact_string


SEPARATOR = "=" * 60
THIN = "-" * 60


def print_step(step: int, title: str):
    print(f"\n{SEPARATOR}")
    print(f"  STEP {step}: {title}")
    print(SEPARATOR)


def simulate_drill():
    print("\n" + SEPARATOR)
    print("  PIPA TIER P -- 침해 대응 드릴 (Incident Response Drill)")
    print("  시나리오: 화장품 D2C 브랜드 CRM DB 무단 접근")
    print(SEPARATOR)

    # -----------------------------------------------------------------------
    # STEP 1: Breach Discovery
    # -----------------------------------------------------------------------
    print_step(1, "침해 인지 (T+0)")

    discovered_at = datetime.datetime.utcnow().isoformat() + "Z"

    event = BreachEvent(
        discovered_at=discovered_at,
        breach_type="unauthorized_access",
        affected_count=2_450,
        data_types=["이름", "전화번호", "이메일", "배송 주소", "피부 타입", "알레르기 정보"],
        systems_affected=["CRM DB (MySQL)", "Make.com 자동화 로그", "Anthropic API 캐시"],
        suspected_cause="CRM 관리자 계정 비밀번호 노출 (피싱 이메일)",
        containment_status="ongoing",
        discovered_by="고객 신고 (의심 문자 수신)",
    )

    print(f"[!] 침해 인지 시각: {discovered_at}")
    print(f"[!] 침해 유형: {event.breach_type}")
    print(f"[!] 영향 인원 (추정): {event.affected_count:,}명")
    print(f"[!] 유출 데이터: {', '.join(event.data_types)}")
    print(f"[!] 포함 민감정보: 피부 타입, 알레르기 정보 (PIPA 제23조 대상)")

    # -----------------------------------------------------------------------
    # STEP 2: Severity Assessment
    # -----------------------------------------------------------------------
    print_step(2, "심각도 판정")

    severity = assess_severity(event)
    print(f"[결과] 심각도: {severity.value}")
    print("[근거] 민감정보(피부상태, 알레르기) 포함 + 1,000명 이상")
    print("[법령] PIPA 제23조 (민감정보) + 제34조 (침해 신고)")

    # -----------------------------------------------------------------------
    # STEP 3: Deadlines
    # -----------------------------------------------------------------------
    print_step(3, "법정 기한 계산")

    deadlines = compute_deadlines(discovered_at)
    for key, deadline in deadlines.items():
        label = {
            "pipc_notification_deadline": "PIPC 신고 기한 (72h)",
            "individual_notification_deadline": "정보주체 통지 기한",
            "internal_escalation_t0": "내부 에스컬레이션 (즉시)",
            "containment_target_t4h": "격리 완료 목표 (T+4h)",
            "forensics_report_t7d": "포렌식 보고서 (T+7d)",
            "post_incident_review_t30d": "사후 감사 (T+30d)",
        }.get(key, key)
        print(f"  {label}: {deadline}")

    # -----------------------------------------------------------------------
    # STEP 4: Audit Log
    # -----------------------------------------------------------------------
    print_step(4, "감사 로그 기록 (불변 체인)")

    import tempfile, pathlib
    with tempfile.TemporaryDirectory() as tmpdir:
        import src.audit_logger as al
        original_path = al.AUDIT_LOG_PATH
        al.AUDIT_LOG_PATH = pathlib.Path(tmpdir) / "audit.jsonl"

        entry = log_breach(severity.value, event.affected_count, event.data_types)
        print(f"  [+] 감사 로그 기록 완료")
        print(f"  [+] 항목 해시: {entry['entry_hash'][:16]}...")
        print(f"  [+] 이전 해시: {entry['prev_hash'][:16]}... (제네시스)")
        print(f"  [+] PIPC 기한: {entry['details']['pipc_notification_deadline']}")

        from src.audit_logger import verify_chain
        valid, broken = verify_chain(al.AUDIT_LOG_PATH)
        print(f"  [+] 체인 무결성 검증: {'PASS' if valid else 'FAIL'}")

        al.AUDIT_LOG_PATH = original_path

    # -----------------------------------------------------------------------
    # STEP 5: PII Redaction from logs
    # -----------------------------------------------------------------------
    print_step(5, "로그 PII 자동 마스킹")

    raw_log_lines = [
        "2026-05-11T03:12:44Z CRM SELECT * WHERE phone='010-9876-5432' user='김민지'",
        "API request body: {email: 'kim@naver.com', skin: '건성', allergy: '향료'} addr: 서울특별시 강남구 테헤란로 123",
        "card_processed: 4321-1234-5678-9999 amount: 89000",
    ]

    print("  [원본 로그 (PII 노출)]")
    for line in raw_log_lines:
        print(f"    {line}")

    print("\n  [마스킹 후 로그]")
    for line in raw_log_lines:
        redacted = redact_string(line)
        print(f"    {redacted}")

    # -----------------------------------------------------------------------
    # STEP 6: PIPC Notification
    # -----------------------------------------------------------------------
    print_step(6, "PIPC 신고서 생성 (PIPA 제34조)")

    pipc_doc = generate_pipc_notification(event, "스킨테라피 주식회사", "123-45-67890")
    print(pipc_doc[:800] + "\n  [... 이하 생략 ...]")

    # -----------------------------------------------------------------------
    # STEP 7: Individual Notice (Email)
    # -----------------------------------------------------------------------
    print_step(7, "정보주체 통지 문자 생성 (SMS)")

    sms = generate_individual_notice(event, "스킨테라피", channel="sms")
    print(f"  [SMS 문자 ({len(sms)}자)]")
    print(f"  {sms}")

    # -----------------------------------------------------------------------
    # STEP 8: Timeline
    # -----------------------------------------------------------------------
    print_step(8, "72시간 대응 타임라인")

    timeline = run_breach_timeline(event)
    for item in timeline:
        print(f"  {item['t']:10s} | [{item['owner']:10s}] {item['action']}")

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    print(f"\n{SEPARATOR}")
    print("  드릴 완료 요약")
    print(SEPARATOR)
    print(f"  심각도: {severity.value}")
    print(f"  PIPC 신고 기한: {deadlines['pipc_notification_deadline']}")
    print(f"  개별 통지 기한: {deadlines['individual_notification_deadline']}")
    print(f"  1,000명 이상 -> 홈페이지 공지 의무: YES")
    print(f"  자동 마스킹: 전화번호, 이메일, 카드번호, 주소 처리 완료")
    print(f"  감사 로그: 불변 체인 기록 완료")
    print()
    print("  [다음 단계]")
    print("  1. privacy.go.kr 접속, 개인정보 유출 신고 접수")
    print("  2. SMS/이메일 2,450명 전체 발송")
    print("  3. 홈페이지 공지 게시 (1,000명 이상 의무)")
    print("  4. 보안 업체 포렌식 착수")
    print(SEPARATOR + "\n")


if __name__ == "__main__":
    simulate_drill()
