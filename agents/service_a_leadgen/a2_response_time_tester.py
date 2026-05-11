"""
A2: Lead response time tester (READ-ONLY mode)
Infers estimated response time from publicly visible signals.
Does NOT submit any forms or fake inquiries.

Signals checked (in order):
  1. Explicit SLA text on contact/about/CS pages ("평균 응답 시간 X시간" etc.)
  2. KakaoTalk channel operating hours (infer off-hours delay)
  3. Presence / absence of live chat widget (no widget = likely slow)
  4. Falls back to "Unknown" with confidence=low if no signal found.
"""

import re
import sys
import time
from typing import Optional

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import requests

import sheet_utils
from config import COL, PLAYWRIGHT_HEADLESS, REQUEST_TIMEOUT_MS, A2_SLOW_THRESHOLD_HRS

# Pages to probe per brand (appended to website URL)
CONTACT_PATHS = ["/contact", "/about", "/cs", "/help", "/고객센터", "/문의"]

# Regex patterns for explicit SLA mentions
SLA_PATTERNS = [
    re.compile(r"평균\s*응답\s*시간[:\s]*(\d+)\s*시간", re.IGNORECASE),
    re.compile(r"응답\s*시간[:\s]*(\d+)\s*(?:시간|hours?)", re.IGNORECASE),
    re.compile(r"(\d+)\s*(?:시간|hours?)\s*(?:내|이내|within)", re.IGNORECASE),
    re.compile(r"within\s*(\d+)\s*hours?", re.IGNORECASE),
]

# Indicators that a live chat / quick response widget is present
LIVE_CHAT_SIGNALS = [
    "channel.io", "channeltalk", "tawk.to", "intercom",
    "카카오 채널", "kakao channel", "채팅 상담",
]

# Indicators of kakao hours limitations
KAKAO_HOURS_PATTERN = re.compile(
    r"(?:카카오|kakao).*?(?:운영|상담)\s*시간.*?(\d{1,2}:\d{2})\s*[-~]\s*(\d{1,2}:\d{2})",
    re.IGNORECASE | re.DOTALL,
)


def test(dry_run: bool = False) -> None:
    """
    For every sheet row missing response time (column 8), attempt inference.
    Writes estimated response time and a confidence note back to the sheet.
    """
    print("[A2] Starting response time inference...")
    rows = sheet_utils.read_all_rows()

    for i, row in enumerate(rows):
        row_sheet_index = i + 2  # row 1 is header
        website = row[COL["website"]] if len(row) > COL["website"] else ""
        already_filled = len(row) > COL["response_time"] and row[COL["response_time"]].strip()

        if already_filled:
            continue
        if not website:
            print(f"[A2]   Row {row_sheet_index}: no website, skipping.")
            continue

        brand = row[COL["brand_kr"]] if len(row) > COL["brand_kr"] else f"row {row_sheet_index}"
        print(f"[A2]   Probing: {brand} ({website})")

        if dry_run:
            est_hrs = "Unknown"
            confidence = "low"
            note = "DRY RUN: no actual request made"
        else:
            est_hrs, confidence, note = _infer_response_time(website)

        print(f"[A2]     Result: ~{est_hrs} hrs (conf={confidence}) | {note}")

        updates = {
            "response_time": str(est_hrs) if est_hrs != "Unknown" else "",
            "notes": _append_note(
                row[COL["notes"]] if len(row) > COL["notes"] else "",
                f"[A2] Response signal: {note} (confidence={confidence})"
            ),
        }
        sheet_utils.update_row_fields(row_sheet_index, updates)

    print("[A2] Done.")


# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------

def _infer_response_time(website: str) -> tuple[str | int, str, str]:
    """
    Returns (estimated_hours_or_Unknown, confidence, explanation_note).
    """
    website = website.rstrip("/")
    page_texts = []

    # Try static fetch first (faster, less resource)
    for path in CONTACT_PATHS:
        url = website + path
        text = _static_fetch(url)
        if text:
            page_texts.append(text)

    # Also try homepage
    homepage_text = _static_fetch(website)
    if homepage_text:
        page_texts.append(homepage_text)

    combined = " ".join(page_texts)

    # 1. Explicit SLA mention
    for pattern in SLA_PATTERNS:
        m = pattern.search(combined)
        if m:
            hrs = int(m.group(1))
            return hrs, "high", f"Explicit SLA found: {m.group(0).strip()}"

    # 2. KakaoTalk operating hours
    m = KAKAO_HOURS_PATTERN.search(combined)
    if m:
        start_hr = int(m.group(1).split(":")[0])
        end_hr = int(m.group(2).split(":")[0])
        # If window is short (< 8 hrs), assume slow off-hours response
        window = (end_hr - start_hr) % 24
        if window < 8:
            return max(4, 24 - window), "medium", f"KakaoTalk hours: {m.group(1)}-{m.group(2)}"
        else:
            return 2, "medium", f"KakaoTalk hours: {m.group(1)}-{m.group(2)} (reasonable window)"

    # 3. Live chat presence
    combined_lower = combined.lower()
    for signal in LIVE_CHAT_SIGNALS:
        if signal in combined_lower:
            return 1, "medium", f"Live chat widget detected: {signal}"

    # 4. No signals found
    if combined:
        return "Unknown", "low", "Contact pages found but no response time signal detected"

    return "Unknown", "low", "Could not fetch contact pages"


def _static_fetch(url: str, timeout: int = 8) -> Optional[str]:
    """Fetch URL with requests; return text or None on failure."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8",
        }
        resp = requests.get(url, headers=headers, timeout=timeout)
        if resp.status_code == 200:
            return resp.text
    except Exception:
        pass
    return None


def _append_note(existing: str, new_note: str) -> str:
    if existing.strip():
        return f"{existing.strip()} | {new_note}"
    return new_note


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    test(dry_run=dry)
