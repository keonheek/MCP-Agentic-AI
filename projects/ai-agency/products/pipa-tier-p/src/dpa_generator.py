"""
dpa_generator.py
----------------
Generates a Data Processing Agreement (DPA) in Korean.
PIPA Art. 26 (처리위탁), Art. 28-2 (국외 이전).

The DPA is required when a brand (controller) delegates personal data
processing to a third-party automation/AI service (processor = 1stmover).
"""

import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class ClientInfo:
    company_name: str          # 위탁사 (브랜드)
    representative: str        # 대표이사
    business_reg_no: str       # 사업자등록번호 (XXX-XX-XXXXX)
    address: str               # 주소
    contact_email: str         # 담당자 이메일
    contact_phone: str         # 담당자 전화번호


@dataclass
class ProcessorInfo:
    company_name: str = "1stmover AI Agency"
    representative: str = "김건희"
    business_reg_no: str = "TBD"
    address: str = "서울특별시"
    contact_email: str = "keonhee3337@gmail.com"


def generate_dpa(
    client: ClientInfo,
    data_types: list[str],
    processing_purposes: list[str],
    retention_period: str = "서비스 종료 후 30일 이내 삭제",
    overseas_services: Optional[list[str]] = None,
    effective_date: Optional[str] = None,
) -> str:
    """
    Generate a Korean DPA document as a plain-text string.
    Caller can write this to .txt or .md file.

    data_types: e.g. ["이름", "전화번호", "이메일", "피부 상태 정보"]
    processing_purposes: e.g. ["마케팅 자동화", "AI 상담 응답", "리드 관리"]
    overseas_services: e.g. ["Anthropic API (미국)", "Make.com (EU)"]
    """
    processor = ProcessorInfo()
    today = effective_date or datetime.date.today().isoformat()
    overseas_services = overseas_services or []

    data_types_str = "\n".join(f"    - {d}" for d in data_types)
    purposes_str = "\n".join(f"    - {p}" for p in processing_purposes)
    overseas_str = (
        "\n".join(f"    - {s}" for s in overseas_services)
        if overseas_services
        else "    - 해당 없음"
    )

    return f"""개인정보 처리위탁 계약서
(Data Processing Agreement)

작성일: {today}

===========================================================
제1조 (목적)
===========================================================
본 계약은 「개인정보 보호법」(이하 "PIPA") 제26조 및 관련 규정에 따라,
위탁사(이하 "갑")가 수탁사(이하 "을")에게 개인정보 처리 업무를 위탁함에 있어
필요한 사항을 규정함을 목적으로 합니다.

===========================================================
제2조 (당사자)
===========================================================
[갑 -- 위탁사]
  상호: {client.company_name}
  대표이사: {client.representative}
  사업자등록번호: {client.business_reg_no}
  주소: {client.address}
  담당자 이메일: {client.contact_email}
  담당자 전화: {client.contact_phone}

[을 -- 수탁사]
  상호: {processor.company_name}
  대표: {processor.representative}
  사업자등록번호: {processor.business_reg_no}
  주소: {processor.address}
  연락처: {processor.contact_email}

===========================================================
제3조 (위탁 업무 범위)
===========================================================
을은 갑으로부터 다음 개인정보 처리 업무를 위탁받습니다.

[처리 목적]
{purposes_str}

[처리하는 개인정보 항목]
{data_types_str}

[보유 및 이용 기간]
  {retention_period}

===========================================================
제4조 (국외 이전 -- PIPA 제28조의2)
===========================================================
업무 처리를 위해 다음 해외 서비스가 사용됩니다. 갑은 이에 사전 동의합니다.
{overseas_str}

을은 해외 처리 업체와 별도의 데이터 처리 계약을 유지하며,
해당 국가의 개인정보 보호 수준이 한국 PIPA 기준에 준하는 경우에 한해 이전합니다.

===========================================================
제5조 (을의 의무)
===========================================================
1. 을은 위탁받은 업무 목적 외 개인정보를 처리하지 않습니다.
2. 을은 PIPA 제29조에 따른 안전조치를 이행합니다.
   - AES-256 암호화 (저장 데이터)
   - TLS 1.3 암호화 (전송 데이터)
   - 접근 권한 최소화 원칙
   - 정기 보안 점검 (분기 1회)
3. 을은 개인정보 침해 발생 시 72시간 이내 갑에게 통보합니다. (PIPA Art. 34)
4. 을은 계약 종료 시 모든 개인정보를 안전하게 파기합니다. (PIPA Art. 21)
5. 을은 갑의 개인정보 처리 현황 조사 요청에 협조합니다.

===========================================================
제6조 (갑의 의무)
===========================================================
1. 갑은 개인정보 수집 시 정보주체로부터 적법한 동의를 받습니다. (PIPA Art. 15, 22)
2. 갑은 개인정보처리방침에 위탁 현황을 공개합니다. (PIPA Art. 26(2))
3. 갑은 을의 개인정보 처리 업무를 정기적으로 감독합니다.

===========================================================
제7조 (손해배상)
===========================================================
을의 귀책 사유로 개인정보 침해가 발생한 경우, 을은 갑에게 실손해를 배상합니다.
단, 갑의 지시에 따른 처리 결과 발생한 손해는 갑이 부담합니다.

===========================================================
제8조 (계약의 효력)
===========================================================
본 계약은 서명일로부터 효력이 발생하며, 위탁 업무 종료 시까지 유효합니다.

===========================================================
서명
===========================================================

갑 (위탁사)
회사명: {client.company_name}
대표이사: ________________ (인)
날짜: ___________________

을 (수탁사)
회사명: {processor.company_name}
대표: ________________ (인)
날짜: ___________________

---
본 계약서는 「개인정보 보호법」(2026.09.11. 개정 시행) 기준으로 작성되었습니다.
"""
