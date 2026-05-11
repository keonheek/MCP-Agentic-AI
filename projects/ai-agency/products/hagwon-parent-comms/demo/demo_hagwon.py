"""
Runnable demo: Hagwon Parent-Comms Agent

Usage:
    python demo/demo_hagwon.py --scenario attendance --student "김민준" --status "결석"
    python demo/demo_hagwon.py --scenario homework --student "박서연" --subject "수학" --missing_count 3
    python demo/demo_hagwon.py --scenario progress --student "이지훈" --subject "영어" --grade "A"

Requires: OPENAI_API_KEY in environment.
Sends to console (dry run) unless KAKAO keys are set.
"""
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from message_generator import generate_alimtalk
from kakao_sender import send_alimtalk
from notion_logger import log_to_notion

DEMO_SCENARIOS = {
    "attendance": {
        "description": "출결 알림 (결석/지각/조퇴)",
        "example_details": {"status": "결석", "reason": "발열"},
    },
    "homework": {
        "description": "숙제 미제출 알림",
        "example_details": {"subject": "수학", "missing_count": 1},
    },
    "progress": {
        "description": "진도 알림",
        "example_details": {"subject": "영어", "chapter": "5단원", "grade": "B+"},
    },
    "notice": {
        "description": "공지 알림 (휴원, 행사)",
        "example_details": {"content": "이번 주 금요일 휴원"},
    },
}


def main():
    parser = argparse.ArgumentParser(description="학원 알림톡 AI 비서 데모")
    parser.add_argument("--scenario", choices=list(DEMO_SCENARIOS.keys()), default="attendance")
    parser.add_argument("--student", default="테스트 학생")
    parser.add_argument("--status", default="결석")
    parser.add_argument("--reason", default="")
    parser.add_argument("--subject", default="수학")
    parser.add_argument("--missing_count", type=int, default=1)
    parser.add_argument("--grade", default="B")
    parser.add_argument("--phone", default="01012345678")
    args = parser.parse_args()

    scenario = args.scenario
    student = args.student

    if scenario == "attendance":
        details = {"status": args.status, "reason": args.reason}
    elif scenario == "homework":
        details = {"subject": args.subject, "missing_count": args.missing_count}
    elif scenario == "progress":
        details = {"subject": args.subject, "grade": args.grade}
    else:
        details = DEMO_SCENARIOS[scenario]["example_details"]

    print(f"\n[DEMO] 시나리오: {DEMO_SCENARIOS[scenario]['description']}")
    print(f"[DEMO] 학생: {student}")
    print(f"[DEMO] 세부 정보: {details}")
    print("[DEMO] 메시지 생성 중...")

    if not os.environ.get("OPENAI_API_KEY"):
        # Offline fallback for demo without API key
        message = f"[학원명] 안녕하세요. {student} 학부모님. {scenario} 관련 알림입니다. (데모 메시지)"
        print("[DEMO] OpenAI API 키 없음: 오프라인 예시 메시지 사용")
    else:
        message = generate_alimtalk(scenario, student, details)

    print(f"\n[생성된 알림톡]\n{message}\n")

    result = send_alimtalk(args.phone, message)
    print(f"[발송 결과] {result}")

    log_to_notion({"event_type": scenario, "student": student, "message": message, "status": result.get("status", "demo")})
    print("[Notion 기록 완료]")


if __name__ == "__main__":
    main()
