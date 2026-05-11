"""
A6: Telegram digest sender
Reads the prospect sheet, selects top 5 by score with status="New",
composes a Telegram message, sends it via the Bot API,
then marks those 5 rows as "Ready to DM" in the sheet.
"""

import os
import sys
from datetime import date

# Ensure sibling modules (sheet_utils, config) are importable when
# this file is invoked from the repo root (e.g. python -c "from agents...")
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)

import requests
from dotenv import load_dotenv

load_dotenv()

import sheet_utils
from config import COL, SHEET_URL, A6_TOP_N

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TELEGRAM_CHAR_LIMIT = 4096
SPLIT_AT = 4000  # leave headroom for safety


def push(text: str, parse_mode: str = "Markdown") -> dict:
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True,
        },
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def push_safe(text: str, parse_mode: str = "Markdown") -> None:
    """Split and send if text exceeds limit."""
    if len(text) <= SPLIT_AT:
        push(text, parse_mode)
        return
    chunks = [text[i:i + SPLIT_AT] for i in range(0, len(text), SPLIT_AT)]
    for chunk in chunks:
        push(chunk, parse_mode)


def digest(dry_run: bool = False) -> None:
    """Main entry point. Picks top 5 prospects, sends Telegram message."""
    print("[A6] Composing morning brief...")
    rows = sheet_utils.read_all_rows()

    candidates = []
    for i, row in enumerate(rows):
        row_sheet_index = i + 2
        status = _get(row, "status")
        score_raw = _get(row, "score")

        if status != "New":
            continue
        if not score_raw:
            continue

        try:
            score = int(score_raw)
        except ValueError:
            score = 0

        candidates.append((score, row_sheet_index, row))

    candidates.sort(key=lambda x: x[0], reverse=True)
    top = candidates[:A6_TOP_N]

    if not top:
        print("[A6] No scored prospects with status=New. Nothing to send.")
        return

    today = str(date.today())

    if dry_run:
        print(f"[A6] DRY RUN: would send Telegram digest for {len(top)} prospects.")
        for score, row_idx, row in top:
            brand = _get(row, "brand_kr")
            ig = _get(row, "ig_handle")
            dm_preview = _get(row, "dm_draft")[:100] if _get(row, "dm_draft") else "(no draft)"
            print(f"  [{score}] {brand} ({ig}): {dm_preview}...")
        return

    if not TOKEN or not CHAT_ID:
        msg = _build_message(top, today)
        print("[A6] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set. Printing message instead:")
        print(msg)
        return

    msg = _build_message(top, today)
    push_safe(msg)

    for _, row_sheet_index, _ in top:
        sheet_utils.update_row_fields(row_sheet_index, {"status": "Ready to DM"})
        print(f"[A6]   Marked row {row_sheet_index} as Ready to DM.")

    print(f"[A6] Done. Sent {len(top)} prospects to Telegram.")


def _build_message(top: list[tuple], today: str) -> str:
    """Build the Telegram Markdown message."""
    lines = [
        f"*Service A Morning Brief: {today}*",
        f"Top {len(top)} 유망 고객. DM 발송 준비 완료.\n",
    ]

    for score, _, row in top:
        brand_kr = _get(row, "brand_kr")
        brand_en = _get(row, "brand_en")
        ig = _get(row, "ig_handle")
        platform = _get(row, "platform") or "?"
        running_ads = _get(row, "running_ads")
        resp_time = _get(row, "response_time")
        dm_name = _get(row, "dm_name")
        dm_role = _get(row, "dm_role")
        dm_draft = _get(row, "dm_draft")

        signals = []
        if running_ads.upper() == "Y":
            signals.append("Meta 광고 active")
        if resp_time and resp_time not in ("Unknown", ""):
            try:
                hrs = float(resp_time)
                if hrs > 2:
                    signals.append(f"응답 {hrs:.0f}h 이상")
            except ValueError:
                pass
        if platform in ("Cafe24", "Imweb"):
            signals.append(f"{platform} (자동화 적합)")
        if dm_name and dm_name != "Unknown":
            signals.append(f"DM: {dm_name} ({dm_role})")
        hot_signal = " / ".join(signals) if signals else "신호 미확인"

        dm_preview = ""
        if dm_draft:
            sentences = [s.strip() for s in dm_draft.replace(".", ".|").split("|") if s.strip()]
            dm_preview = " ".join(sentences[:2])
            if len(dm_preview) > 200:
                dm_preview = dm_preview[:197] + "..."

        name_display = brand_kr
        if brand_en and brand_en != brand_kr:
            name_display += f" ({brand_en})"

        lines.append(f"*[{score}점] {name_display}*")
        lines.append(f"IG: {ig or '미확인'}")
        lines.append(f"신호: {hot_signal}")
        lines.append(f"DM 미리보기: {dm_preview or '(초안 없음)'}")
        lines.append("")

    lines.append(f"Sheet: {SHEET_URL}")
    return "\n".join(lines)


def _get(row: list, col_key: str) -> str:
    idx = COL[col_key]
    if len(row) > idx:
        return row[idx].strip()
    return ""


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    digest(dry_run=dry)
