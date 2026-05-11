"""
access_request.py
-----------------
본인정보 열람청구 handler.
PIPA Art. 35 (개인정보 열람), Art. 36 (정정/삭제), Art. 37 (처리 정지).

2026 amendment: Response deadline confirmed at 10 business days.
Failure to respond = administrative fine up to ₩10M per case.

Data subject rights covered:
- Art. 35: Right of access (열람)
- Art. 36: Right to rectification and erasure (정정/삭제)
- Art. 37: Right to restriction of processing (처리 정지)
- Art. 37-2 (2026 new): Right to automated decision-making explanation
           (AI가 자동 처리한 결정에 대한 설명 요구권)
"""

import datetime
from dataclasses import dataclass
from typing import Optional
from enum import Enum
from pathlib import Path
import json


class RequestType(str, Enum):
    ACCESS = "열람"                     # Art. 35
    RECTIFICATION = "정정"              # Art. 36
    ERASURE = "삭제"                    # Art. 36
    RESTRICTION = "처리정지"            # Art. 37
    AI_EXPLANATION = "자동결정설명"     # Art. 37-2 (2026 new)
    DATA_PORTABILITY = "이전"           # Art. 35-2 (2026 new)


class RequestStatus(str, Enum):
    RECEIVED = "접수"
    IN_PROGRESS = "처리중"
    COMPLETED = "완료"
    REJECTED = "거부"
    PENDING_VERIFICATION = "본인확인중"


RESPONSE_DEADLINE_BUSINESS_DAYS = 10

REQUEST_STORE_PATH = Path("data/access_requests.jsonl")


@dataclass
class AccessRequest:
    request_id: str
    user_id: str
    request_type: RequestType
    received_at: str
    deadline: str
    identity_verified: bool
    status: RequestStatus
    details: dict
    response: Optional[str] = None
    responded_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "request_type": self.request_type.value,
            "received_at": self.received_at,
            "deadline": self.deadline,
            "identity_verified": self.identity_verified,
            "status": self.status.value,
            "details": self.details,
            "response": self.response,
            "responded_at": self.responded_at,
        }


def _compute_deadline(received_at: str, business_days: int = RESPONSE_DEADLINE_BUSINESS_DAYS) -> str:
    """
    Compute deadline skipping weekends (simplified: adds 14 calendar days as proxy).
    Production: use Korea public holiday calendar.
    """
    received = datetime.datetime.fromisoformat(received_at.rstrip("Z"))
    # Add business days (approximated as 1.4x calendar days)
    deadline = received + datetime.timedelta(days=business_days + 4)
    return deadline.isoformat() + "Z"


def _generate_request_id(user_id: str, request_type: RequestType) -> str:
    import hashlib
    ts = datetime.datetime.utcnow().isoformat()
    raw = f"{user_id}:{request_type.value}:{ts}"
    return "REQ-" + hashlib.sha256(raw.encode()).hexdigest()[:12].upper()


def receive_request(
    user_id: str,
    request_type: RequestType,
    details: dict,
    identity_verified: bool = False,
    store_path: Path = REQUEST_STORE_PATH,
) -> AccessRequest:
    """
    Register a new data subject rights request.
    Auto-calculates the 10 business day response deadline.
    """
    now = datetime.datetime.utcnow().isoformat() + "Z"
    request_id = _generate_request_id(user_id, request_type)
    deadline = _compute_deadline(now)

    req = AccessRequest(
        request_id=request_id,
        user_id=user_id,
        request_type=request_type,
        received_at=now,
        deadline=deadline,
        identity_verified=identity_verified,
        status=RequestStatus.PENDING_VERIFICATION if not identity_verified else RequestStatus.IN_PROGRESS,
        details=details,
    )

    store_path.parent.mkdir(parents=True, exist_ok=True)
    with store_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(req.to_dict(), ensure_ascii=False) + "\n")

    return req


def fulfill_access_request(request_id: str, user_data: dict) -> str:
    """
    Generate the response document for an Art. 35 열람 request.
    user_data: dict of the personal data held for this user.
    """
    return f"""개인정보 열람 결과 통보 (PIPA 제35조)

요청 번호: {request_id}
처리 일시: {datetime.datetime.utcnow().isoformat()}Z

귀하가 요청하신 개인정보 열람 결과를 아래와 같이 통보드립니다.

[보유 중인 개인정보]
{json.dumps(user_data, ensure_ascii=False, indent=2)}

[처리 현황]
- 수집 목적: 마케팅 자동화 서비스 제공
- 보유 기간: 서비스 이용 종료 후 30일
- 제3자 제공 현황: Anthropic API (미국), Make.com (EU)
- 자동화 처리 여부: AI 기반 리드 스코어링 적용

[추가 권리 안내]
- 정정/삭제 요청: 본 이메일에 회신하시거나 서비스 내 설정에서 직접 처리 가능
- 처리 정지 요청: 동의 철회 시 AI 처리 즉시 중단
- 자동결정 설명 요청: AI 스코어링 근거 설명 요청 가능 (PIPA 제37조의2)

문의: 개인정보 보호 책임자 | keonhee3337@gmail.com
"""


def generate_erasure_confirmation(user_id: str, deleted_fields: list[str]) -> str:
    """Generate PIPA Art. 36 erasure confirmation."""
    fields_str = ", ".join(deleted_fields)
    return f"""개인정보 삭제 완료 통보 (PIPA 제36조)

정보주체: {user_id}
삭제 완료 일시: {datetime.datetime.utcnow().isoformat()}Z
삭제된 항목: {fields_str}

삭제 방법: 복구 불가능한 방식으로 영구 삭제 완료
백업 삭제: 다음 정기 백업 파기 일정(30일 이내)에 포함 예정

이후 귀하의 개인정보는 더 이상 처리되지 않습니다.
"""


def generate_ai_explanation(user_id: str, decision: str, features_used: list[str], score: float) -> str:
    """
    Generate explanation for automated decision-making.
    PIPA Art. 37-2 (신설 2026): Right to explanation for AI decisions.
    """
    features_str = "\n".join(f"  - {f}" for f in features_used)
    return f"""자동화 의사결정 설명 (PIPA 제37조의2)

정보주체: {user_id}
결정 내용: {decision}
AI 스코어: {score:.2f} / 1.00
처리 일시: {datetime.datetime.utcnow().isoformat()}Z

[사용된 데이터 항목]
{features_str}

[결정 근거]
본 결정은 AI 언어 모델(Claude/GPT)을 통한 자동화 처리 결과입니다.
사용된 모델은 입력 텍스트 패턴, 행동 이력, 프로필 완성도를 기반으로 점수를 산출합니다.

[이의 제기 방법]
자동 결정에 동의하지 않으시면, 담당자의 직접 검토를 요청하실 수 있습니다.
요청 방법: keonhee3337@gmail.com (제목: "자동결정 이의제기 -- {user_id}")
처리 기한: 요청 접수 후 10 영업일 이내
"""


def get_overdue_requests(store_path: Path = REQUEST_STORE_PATH) -> list[dict]:
    """Return all requests past their deadline that are not yet completed."""
    if not store_path.exists():
        return []
    now = datetime.datetime.utcnow().isoformat() + "Z"
    overdue = []
    with store_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            req = json.loads(line)
            if req["status"] not in ("완료", "거부") and req["deadline"] < now:
                overdue.append(req)
    return overdue
