"""
A5: DM draft writer -- Pure Data Collector
Computes hot prospect score (0-100).
Writes score to sheet (column 13).
Writes pending_drafts.json for /service-a-daily slash command to generate DM text.

DM structure (handled by slash command):
  1. Specific observation referencing their recent product / ad / platform
  2. Specific problem (response time delay or platform friction)
  3. Soft ask

Scoring weights:
  Running ads active   = 30 pts
  Response time > 2hr  = 30 pts
  Decision maker found = 20 pts
  Platform automation-ready (Cafe24 / Imweb) = 20 pts
"""

import sys
import json
from pathlib import Path

import sheet_utils
from config import (
    COL,
    SCORE_ADS_ACTIVE,
    SCORE_SLOW_RESPONSE,
    SCORE_DM_FOUND,
    SCORE_PLATFORM,
    A2_SLOW_THRESHOLD_HRS,
)

AUTOMATION_READY_PLATFORMS = {"Cafe24", "Imweb"}
DATA_DIR = Path(__file__).parent / "data"


def draft(dry_run: bool = False) -> None:
    """
    For each sheet row with sufficient data (columns 1-12 mostly filled):
    - Compute score and write to sheet
    - Collect brand context into pending_drafts.json for slash command
    """
    print("[A5] Starting scoring + pending draft collection...")
    rows = sheet_utils.read_all_rows()

    pending = []

    for i, row in enumerate(rows):
        row_sheet_index = i + 2

        # Skip if already has a draft
        already_drafted = len(row) > COL["dm_draft"] and row[COL["dm_draft"]].strip()
        if already_drafted:
            continue

        brand_kr = _get(row, "brand_kr")
        if not brand_kr:
            continue

        # Compute score
        score = _compute_score(row)
        print(f"[A5]   {brand_kr}: score={score}")

        if not dry_run:
            sheet_utils.update_row_fields(row_sheet_index, {
                "score": str(score),
            })

        # Collect context for slash command
        pending.append({
            "row_sheet_index": row_sheet_index,
            "brand_kr": brand_kr,
            "brand_en": _get(row, "brand_en"),
            "ig_handle": _get(row, "ig_handle"),
            "platform": _get(row, "platform"),
            "running_ads": _get(row, "running_ads"),
            "response_time": _get(row, "response_time"),
            "dm_name": _get(row, "dm_name"),
            "dm_role": _get(row, "dm_role"),
            "score": score,
        })

    # Write pending drafts JSON for slash command
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_DIR / "pending_drafts.json"
    out_path.write_text(json.dumps(pending, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[A5] {len(pending)} prospects written to {out_path}")
    print("[A5] Next: /service-a-daily will generate DM drafts in-session and write them back to sheet.")

    if dry_run:
        print("[A5] DRY RUN: Sheet score update skipped.")

    print("[A5] Done.")


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _compute_score(row: list) -> int:
    score = 0

    if _get(row, "running_ads").upper() == "Y":
        score += SCORE_ADS_ACTIVE

    resp_raw = _get(row, "response_time")
    if resp_raw and resp_raw not in ("Unknown", ""):
        try:
            hrs = float(resp_raw)
            if hrs > A2_SLOW_THRESHOLD_HRS:
                score += SCORE_SLOW_RESPONSE
        except ValueError:
            pass
    elif not resp_raw:
        score += SCORE_SLOW_RESPONSE // 2

    if _get(row, "dm_name") and _get(row, "dm_name") not in ("Unknown", ""):
        score += SCORE_DM_FOUND

    platform = _get(row, "platform")
    if platform in AUTOMATION_READY_PLATFORMS:
        score += SCORE_PLATFORM
    elif platform in ("Smart Store", "Makeshop"):
        score += SCORE_PLATFORM // 2

    return min(score, 100)


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _get(row: list, col_key: str) -> str:
    idx = COL[col_key]
    if len(row) > idx:
        return row[idx].strip()
    return ""


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    draft(dry_run=dry)
