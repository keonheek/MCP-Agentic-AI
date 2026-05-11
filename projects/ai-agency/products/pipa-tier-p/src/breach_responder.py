"""
breach_responder.py
-------------------
72-hour PIPC breach notification template generator.
PIPA Art. 34 (개인정보 유출 통지 및 신고).

2026 amendment key changes:
- Art. 34(1): Notification to PIPC within 72 hours (previously 5 business days)
- Art. 34(3): Notify affected individuals "without delay" (지체 없이)
- New: If >1,000 persons affected, mandatory press release in addition to PIPC report
- Fine for late notification: up to ₩30M per incident

Breach severity levels:
- CRITICAL: >10,000 persons OR sensitive data (건강, 금융, 주민번호)
- HIGH: 1,000-10,000 persons OR any unique identifiers
- MEDIUM: 100-1,000 persons, general personal data
- LOW: <100 persons, non-sensitive data
"""

import datetime
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class BreachEvent:
    discovered_at: str             # ISO timestamp
    breach_type: str               # "unauthorized_access" | "data_leak" | "ransomware" | "insider"
    affected_count: int
    data_types: list[str]          # e.g. ["이름", "전화번호", "피부상태"]
    systems_affected: list[str]    # e.g. ["CRM DB", "Anthropic API logs"]
    suspected_cause: str
    containment_status: str        # "contained" | "ongoing"
    discovered_by: str             # "자동 탐지" | "고객 신고" | "내부 발견"


def assess_severity(event: BreachEvent) -> Severity:
    """Determine breach severity per PIPA Art. 34 criteria."""
    sensitive_types = {
        "주민등록번호", "건강정보", "피부상태", "알레르기", "카드번호",
        "계좌번호", "생체정보", "정신건강", "성생활",
    }
    has_sensitive = any(d in sensitive_types for d in event.data_types)

    if event.affected_count > 10_000 or (has_sensitive and event.affected_count > 100):
        return Severity.CRITICAL
    if event.affected_count >= 1_000 or has_sensitive:
        return Severity.HIGH
    if event.affected_count >= 100:
        return Severity.MEDIUM
    return Severity.LOW


def compute_deadlines(discovered_at: str) -> dict:
    """
    Compute all statutory deadlines from breach discovery time.
    PIPA Art. 34 (2026 amendment).
    """
    discovered = datetime.datetime.fromisoformat(discovered_at.rstrip("Z"))
    return {
        "pipc_notification_deadline": (discovered + datetime.timedelta(hours=72)).isoformat() + "Z",
        "individual_notification_deadline": (discovered + datetime.timedelta(hours=72)).isoformat() + "Z",
        "internal_escalation_t0": discovered.isoformat() + "Z",
        "containment_target_t4h": (discovered + datetime.timedelta(hours=4)).isoformat() + "Z",
        "forensics_report_t7d": (discovered + datetime.timedelta(days=7)).isoformat() + "Z",
        "post_incident_review_t30d": (discovered + datetime.timedelta(days=30)).isoformat() + "Z",
    }


def generate_pipc_notification(event: BreachEvent, company_name: str, company_reg_no: str) -> str:
    """
    Generate the PIPC (개인정보보호위원회) notification document.
    Submit via: https://privacy.go.kr (개인정보 포털)
    """
    severity = assess_severity(event)
    deadlines = compute_deadlines(event.discovered_at)
    data_types_str = ", ".join(event.data_types)
    systems_str = ", ".join(event.systems_affected)

    return f"""개인정보 유출 신고서
(PIPA Art. 34 -- 개인정보보호위원회 제출용)

신고 일시: {datetime.datetime.utcnow().isoformat()}Z
신고 기관: 개인정보보호위원회 (privacy.go.kr)

===== 신고 기업 정보 =====
기업명: {company_name}
사업자등록번호: {company_reg_no}
개인정보 보호 책임자: 김건희 (1stmover AI Agency)
연락처: keonhee3337@gmail.com

===== 유출 개요 =====
유출 인지 일시: {event.discovered_at}
인지 방법: {event.discovered_by}
유출 유형: {event.breach_type}
피해 심각도: {severity.value}
피해 추정 인원: {event.affected_count:,}명
유출된 개인정보 항목: {data_types_str}
관련 시스템: {systems_str}
추정 원인: {event.suspected_cause}
현재 상황: {event.containment_status}

===== 조치 현황 =====
1. 즉각 조치: 유출 경로 차단 및 시스템 격리
2. 증거 보전: 로그 및 시스템 이미지 보관 중
3. 정보주체 통지: {deadlines['individual_notification_deadline']} 이전 완료 예정
4. 후속 조치 계획: 보안 패치, 접근 권한 재점검, 임직원 교육

===== 법적 의무 =====
PIPC 신고 기한: {deadlines['pipc_notification_deadline']}
정보주체 통지 기한: {deadlines['individual_notification_deadline']}
근거 조문: PIPA 제34조 (2026.09.11. 개정)

{"[주의] 피해자 1,000명 이상 -- 인터넷 홈페이지 공지 추가 의무 (Art. 34(3))" if event.affected_count >= 1000 else ""}

신고인: 김건희
서명: ________________
"""


def generate_individual_notice(
    event: BreachEvent,
    company_name: str,
    channel: str = "email",
) -> str:
    """
    Generate notice to affected individuals.
    PIPA Art. 34(1): Must notify "지체 없이" (without delay).
    channel: "email" | "sms" | "app_push" | "postal"
    """
    data_types_str = ", ".join(event.data_types)
    severity = assess_severity(event)

    if channel == "sms":
        # SMS has character limit
        return (
            f"[{company_name}] 개인정보 유출 안내\n"
            f"유출항목: {data_types_str[:30]}...\n"
            f"유출일: {event.discovered_at[:10]}\n"
            f"비밀번호 즉시 변경 권고. 자세히: [URL]"
        )

    return f"""[개인정보 유출 피해 안내]

안녕하세요. {company_name}입니다.

고객님의 개인정보 일부가 유출된 사실을 확인하여 안내드립니다.
(PIPA 제34조에 따른 의무 통지)

1. 유출 인지 일시: {event.discovered_at[:10]}
2. 유출 경위: {event.suspected_cause}
3. 유출된 개인정보 항목: {data_types_str}
4. 유출 규모: 약 {event.affected_count:,}명
5. 피해 최소화 조치:
   - 유출 경로 즉시 차단 완료
   - 비밀번호를 즉시 변경해 주세요
   - 의심 거래 발생 시 카드사/금융기관에 신고하세요
   - 스팸/피싱 문자에 주의하세요

6. 문의: {company_name} 개인정보 보호 담당 | 이메일 문의

이 사실을 즉시 통보하지 못한 점 진심으로 사과드립니다.
향후 동일 사고 재발 방지를 위해 최선을 다하겠습니다.

{company_name} 드림
"""


def run_breach_timeline(event: BreachEvent) -> list[dict]:
    """
    Return a prioritized action timeline for the first 72 hours.
    Used by demo_incident_drill.py.
    """
    deadlines = compute_deadlines(event.discovered_at)
    severity = assess_severity(event)

    timeline = [
        {"t": "T+0h",   "action": "사고 대응팀 소집 (CPO, CTO, 법무)", "owner": "CPO"},
        {"t": "T+1h",   "action": "유출 경로 격리 + 증거 보전 (로그 스냅샷)", "owner": "CTO"},
        {"t": "T+2h",   "action": "피해 범위 및 데이터 유형 확인", "owner": "CTO"},
        {"t": "T+4h",   "action": "내부 보고서 초안 완성", "owner": "CPO"},
        {"t": "T+12h",  "action": "법무 검토 + PIPC 신고 초안 확정", "owner": "법무"},
        {"t": "T+24h",  "action": "정보주체 통지 발송 (이메일/SMS)", "owner": "마케팅"},
        {"t": "T+48h",  "action": "PIPC 신고서 제출 (privacy.go.kr)", "owner": "CPO"},
        {"t": "T+72h",  "action": "PIPC 신고 기한 (법정 데드라인)", "owner": "CPO"},
        {"t": "T+7d",   "action": "포렌식 보고서 완성 + 재발 방지 계획 수립", "owner": "CTO"},
        {"t": "T+30d",  "action": "사후 감사 + 개인정보 처리방침 업데이트", "owner": "CPO"},
    ]

    if severity in (Severity.CRITICAL, Severity.HIGH) and event.affected_count >= 1_000:
        timeline.insert(5, {
            "t": "T+12h",
            "action": "홈페이지 공지 게시 (1,000명 이상 -- 의무)",
            "owner": "마케팅",
        })

    return timeline
