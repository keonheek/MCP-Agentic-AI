"""
Kakao Alimtalk sender stub.
Wraps Kakao Alimtalk Sender API (or Make.com webhook as proxy).
"""
import os
import requests


KAKAO_API_KEY = os.environ.get("KAKAO_ALIMTALK_API_KEY", "")
KAKAO_SENDER_KEY = os.environ.get("KAKAO_SENDER_KEY", "")
KAKAO_TEMPLATE_CODE = os.environ.get("KAKAO_TEMPLATE_CODE", "hagwon_001")

# Make.com webhook proxy (used during demo/pre-Kakao-approval phase)
MAKE_WEBHOOK_URL = os.environ.get("MAKE_KAKAO_WEBHOOK_URL", "")


def send_alimtalk(phone: str, message: str) -> dict:
    """
    Send a Kakao Alimtalk message.
    Falls back to Make.com webhook if direct API not configured.
    """
    if KAKAO_API_KEY and KAKAO_SENDER_KEY:
        return _send_direct(phone, message)
    elif MAKE_WEBHOOK_URL:
        return _send_via_make(phone, message)
    else:
        # Dry-run mode for demo
        print(f"[DRY RUN] Would send to {phone}: {message[:50]}...")
        return {"status": "dry_run", "phone": phone}


def _send_direct(phone: str, message: str) -> dict:
    """Direct Kakao Alimtalk API call."""
    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "sender_key": KAKAO_SENDER_KEY,
        "template_code": KAKAO_TEMPLATE_CODE,
        "receiver_num": phone,
        "template_msg": message,
        "fail_over": "Y",  # SMS fallback if Kakao fails
        "msg_type": "AT",
    }
    resp = requests.post(
        "https://alimtalk-api.kakao.com/v2/sender/send",
        json=payload,
        headers=headers,
        timeout=10,
    )
    return {"status": "sent" if resp.ok else "failed", "code": resp.status_code}


def _send_via_make(phone: str, message: str) -> dict:
    """Send via Make.com webhook proxy (demo mode)."""
    resp = requests.post(
        MAKE_WEBHOOK_URL,
        json={"phone": phone, "message": message},
        timeout=10,
    )
    return {"status": "sent" if resp.ok else "failed", "via": "make"}
