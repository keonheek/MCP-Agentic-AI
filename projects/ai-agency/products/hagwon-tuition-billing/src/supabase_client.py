"""
Supabase client for hagwon tuition billing data.
Stores student records, billing keys, payment history.
"""
import os
import requests

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}


def get_students_due_today() -> list:
    """Return students whose billing date is today."""
    if not SUPABASE_URL:
        # Demo stub
        return [
            {"id": "1", "name": "김민준", "parent_phone": "01012345678",
             "tuition_amount": 300000, "billing_key": "demo_key_1"},
        ]
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/students",
        params={"billing_day": f"eq.{__import__('datetime').datetime.now().day}"},
        headers=HEADERS,
        timeout=10,
    )
    return resp.json() if resp.ok else []


def get_unpaid_students() -> list:
    """Return students with payment_status = 'unpaid'."""
    if not SUPABASE_URL:
        return []
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/payment_history",
        params={"payment_status": "eq.unpaid"},
        headers=HEADERS,
        timeout=10,
    )
    return resp.json() if resp.ok else []


def log_payment(student_id: str, amount: int, status: str, toss_response: dict) -> bool:
    """Insert a payment record."""
    if not SUPABASE_URL:
        print(f"[SUPABASE LOG] student={student_id}, amount={amount}, status={status}")
        return True
    payload = {
        "student_id": student_id,
        "amount": amount,
        "payment_status": status,
        "toss_order_id": toss_response.get("orderId", ""),
        "paid_at": __import__("datetime").datetime.utcnow().isoformat(),
    }
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/payment_history",
        json=payload,
        headers=HEADERS,
        timeout=10,
    )
    return resp.ok


def kakao_notifier_stub():
    pass  # imported by dunning_scheduler
