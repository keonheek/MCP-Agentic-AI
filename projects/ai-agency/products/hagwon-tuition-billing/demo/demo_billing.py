"""
Runnable demo: Hagwon Tuition Auto-Billing

Usage:
    python demo/demo_billing.py --students 5 --date 2026-06-05 --simulate
    python demo/demo_billing.py --mode dunning --student "테스트 학생" --days_overdue 3
    python demo/demo_billing.py --mode report

No external keys required for demo mode.
"""
import argparse
import sys
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

DEMO_STUDENTS = [
    {"id": f"s{i}", "name": n, "parent_phone": f"010{i:08d}", "tuition_amount": random.choice([200000, 300000, 350000]), "billing_key": f"demo_key_{i}"}
    for i, n in enumerate(["김민준", "박서연", "이지훈", "최유진", "한동훈"], start=1)
]


def simulate_billing(num_students: int, billing_date: str):
    students = DEMO_STUDENTS[:num_students]
    print(f"\n[BILLING SIM] {billing_date} 수강료 자동 결제 시작")
    print(f"[BILLING SIM] 대상: {num_students}명\n")

    results = []
    for i, student in enumerate(students):
        # Simulate 80% success rate
        success = i < (num_students * 4 // 5)
        status = "success" if success else "failure"

        print(f"  [{status.upper()}] {student['name']} - ₩{student['tuition_amount']:,}")
        if success:
            print(f"    -> 학부모 영수증 알림톡 발송 완료")
        else:
            print(f"    -> 원장님 즉시 알림 발송 + 학부모 재결제 안내 알림톡")

        results.append({"student": student["name"], "status": status, "amount": student["tuition_amount"]})

    success_count = sum(1 for r in results if r["status"] == "success")
    total_amount = sum(r["amount"] for r in results if r["status"] == "success")

    print(f"\n[RESULT] 성공: {success_count}/{num_students}")
    print(f"[RESULT] 총 수령액: ₩{total_amount:,}")
    print(f"[RESULT] 원장님 조치 필요: {num_students - success_count}건")


def simulate_dunning(student_name: str, days_overdue: int):
    print(f"\n[DUNNING] {student_name} - {days_overdue}일 미납")
    if days_overdue == 3:
        print(f"  D+3 알림톡 발송: '[학원명] {student_name}학생 수강료가 3일째 미납입니다. 확인 부탁드립니다.'")
    elif days_overdue == 7:
        print(f"  D+7 알림톡 발송: '[학원명] {student_name}학생 수강료가 7일째 미납입니다. 빠른 처리 부탁드립니다.'")
    else:
        print(f"  해당 일자({days_overdue}일)에는 자동 독촉 없음. D+3, D+7에만 발송.")


def show_report():
    print("\n[월간 결제 리포트] 2026년 5월")
    print("-" * 40)
    print(f"총 결제 대상: 5명")
    print(f"성공: 4명 (₩1,150,000)")
    print(f"실패/미납: 1명 (₩300,000)")
    print(f"성공률: 80.0%")
    print(f"사이다페이 수수료 절약: ₩17,250 (₩1,150,000 x 1.5%)")
    print(f"원장 절약 시간: 약 2.5시간")
    print("-" * 40)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--students", type=int, default=5)
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-05"))
    parser.add_argument("--mode", choices=["billing", "dunning", "report"], default="billing")
    parser.add_argument("--simulate", action="store_true")
    parser.add_argument("--student", default="테스트 학생")
    parser.add_argument("--days_overdue", type=int, default=3)
    args = parser.parse_args()

    if args.mode == "billing" or args.simulate:
        simulate_billing(args.students, args.date)
    elif args.mode == "dunning":
        simulate_dunning(args.student, args.days_overdue)
    elif args.mode == "report":
        show_report()


if __name__ == "__main__":
    main()
