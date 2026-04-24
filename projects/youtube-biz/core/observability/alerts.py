"""
Observability: 에러 알림 (webhook)
3회 연속 실패 시 알림 발송
"""
import json
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
LOGS_DIR = BASE_DIR / "logs"
FAILURE_TRACKER_PATH = LOGS_DIR / ".failure_counts.json"


def load_failure_counts() -> dict:
    if FAILURE_TRACKER_PATH.exists():
        with open(FAILURE_TRACKER_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_failure_counts(counts: dict):
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with open(FAILURE_TRACKER_PATH, "w", encoding="utf-8") as f:
        json.dump(counts, f, ensure_ascii=False, indent=2)


def record_result(step: str, success: bool) -> int:
    """
    실패 횟수 추적. 성공 시 카운트 리셋.
    Returns: current consecutive failures
    """
    counts = load_failure_counts()
    if success:
        counts[step] = 0
    else:
        counts[step] = counts.get(step, 0) + 1
    save_failure_counts(counts)
    return counts[step]


def send_webhook_alert(message: str):
    """웹훅 알림 발송 (Slack/Discord/카카오 호환)"""
    webhook_url = os.getenv("ALERT_WEBHOOK_URL", "")
    if not webhook_url:
        print(f"[ALERT] ALERT_WEBHOOK_URL 미설정. 알림 내용: {message}")
        return

    try:
        import httpx
        payload = {"text": message, "content": message}  # Slack/Discord 호환
        httpx.post(webhook_url, json=payload, timeout=10)
        print(f"[Alert] 웹훅 발송 완료")
    except Exception as e:
        print(f"[Alert] 웹훅 발송 실패: {e}")


def check_and_alert(step: str, success: bool, error_msg: str = ""):
    """
    실패 추적 + 3회 연속 실패 시 알림
    """
    failures = record_result(step, success)
    threshold = 3

    if not success:
        print(f"[Alert] {step} 실패 ({failures}회 연속)")
        if failures >= threshold:
            msg = (
                f"[YouTube Biz] {step} {failures}회 연속 실패!\n"
                f"시각: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                f"오류: {error_msg[:200]}"
            )
            send_webhook_alert(msg)


if __name__ == "__main__":
    # 테스트
    check_and_alert("test_step", False, "테스트 에러")
    check_and_alert("test_step", False, "테스트 에러")
    check_and_alert("test_step", False, "테스트 에러")  # 3회 → 알림 발송
    check_and_alert("test_step", True)  # 리셋
