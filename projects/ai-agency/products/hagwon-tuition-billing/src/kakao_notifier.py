"""
Kakao Alimtalk notifier for billing events.
Success / failure / dunning templates.
"""
import os
import requests

KAKAO_API_KEY = os.environ.get("KAKAO_ALIMTALK_API_KEY", "")
KAKAO_SENDER_KEY = os.environ.get("KAKAO_SENDER_KEY", "")
MAKE_WEBHOOK_URL = os.environ.get("MAKE_KAKAO_WEBHOOK_URL", "")

TEMPLATES = {
    "success": "[학원명] {student}학생 수강료 ₩{amount:,}원이 정상 결제되었습니다. 감사합니다.",
    "failure": "[학원명] {student}학생 수강료 결제가 실패하였습니다. 카드 정보를 확인해 주세요.",
    "D3": "[학원명] {student}학생 수강료 ₩{amount:,}원이 3일째 미납입니다. 확인 부탁드립니다.",
    "D7": "[학원명] {student}학생 수강료 ₩{amount:,}원이 7일째 미납입니다. 빠른 처리 부탁드립니다.",
}


def send_billing_result(phone: str, student_name: str, amount: int, status: str) -> dict:
    """Send payment success or failure notification."""
    template_key = "success" if status == "success" else "failure"
    message = TEMPLATES[template_key].format(student=student_name, amount=amount)
    return _send(phone, message)


def send_dunning_alimtalk(phone: str, student_name: str, amount: int, message_type: str) -> dict:
    """Send D+3 or D+7 dunning notification."""
    template = TEMPLATES.get(message_type, TEMPLATES["D3"])
    message = template.format(student=student_name, amount=amount)
    return _send(phone, message)


def _send(phone: str, message: str) -> dict:
    if not KAKAO_API_KEY and not MAKE_WEBHOOK_URL:
        print(f"[DRY RUN] {phone}: {message[:60]}...")
        return {"status": "dry_run"}

    if MAKE_WEBHOOK_URL:
        resp = requests.post(MAKE_WEBHOOK_URL, json={"phone": phone, "message": message}, timeout=10)
        return {"status": "sent" if resp.ok else "failed", "via": "make"}

    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "sender_key": KAKAO_SENDER_KEY,
        "template_msg": message,
        "receiver_num": phone,
        "msg_type": "AT",
        "fail_over": "Y",
    }
    resp = requests.post("https://alimtalk-api.kakao.com/v2/sender/send", json=payload, headers=headers, timeout=10)
    return {"status": "sent" if resp.ok else "failed"}
