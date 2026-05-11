"""
Dunning (late payment follow-up) scheduler.
Runs D+3 and D+7 auto-notifications for unpaid tuition.
"""
import os
from datetime import datetime, timedelta
from supabase_client import get_unpaid_students
from kakao_notifier import send_dunning_alimtalk


def run_dunning_check(today: datetime = None) -> list:
    """
    Check for unpaid students and send dunning messages.
    Returns list of actions taken.
    """
    if today is None:
        today = datetime.now()

    unpaid = get_unpaid_students()
    actions = []

    for student in unpaid:
        due_date_str = student.get("due_date")
        if not due_date_str:
            continue

        due_date = datetime.fromisoformat(due_date_str)
        days_overdue = (today - due_date).days

        if days_overdue == 3:
            result = send_dunning_alimtalk(
                phone=student["parent_phone"],
                student_name=student["name"],
                amount=student["tuition_amount"],
                message_type="D3",
            )
            actions.append({"student": student["name"], "action": "D3_dunning", "result": result})

        elif days_overdue == 7:
            result = send_dunning_alimtalk(
                phone=student["parent_phone"],
                student_name=student["name"],
                amount=student["tuition_amount"],
                message_type="D7",
            )
            actions.append({"student": student["name"], "action": "D7_dunning", "result": result})

    return actions


DUNNING_TEMPLATES = {
    "D3": "[학원명] 안녕하세요. {student}학생 수강료 ₩{amount:,}원이 3일 전 미납 상태입니다. 확인 부탁드립니다.",
    "D7": "[학원명] {student}학생 수강료 ₩{amount:,}원이 7일째 미납입니다. 빠른 처리 부탁드립니다. 문의: {phone}",
}
