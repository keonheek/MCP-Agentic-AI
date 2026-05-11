"""
M2 Blindspot Scanner -- Pure Data Collector
Runs weekly on Sundays at 10pm KST.
Collects all inputs from strands, writes to JSON.
NO LLM calls. Synthesis happens via /m2-blindspot slash command in Claude Code session.
"""

import sys
import os
import json
import datetime
from pathlib import Path

from dotenv import load_dotenv

# Force UTF-8 output (Korean text on Windows)
sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
REPO_ROOT = Path("C:/Users/keonh/Dev/MCP_Agentic_AI")
DATA_DIR = Path(__file__).parent / "data"
load_dotenv(REPO_ROOT / ".env")

DISCORD_WEBHOOK = os.getenv("DISCORD_M2_WEBHOOK")
GDRIVE_FOLDER_ID = "1PU6EX-ay-gr3B8FeDwyKOac2zpwXynKy"

COMPETITOR_SCRAPE = REPO_ROOT / "projects" / "ai-agency" / "research" / "competitor_scrape_2026-05-09.md"

DRY_RUN_DISCORD = not DISCORD_WEBHOOK

# ---------------------------------------------------------------------------
# Strand imports
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent))
from strands import competitive, stack, regulation, positioning, internal_drift


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    today = datetime.date.today()
    today_str = today.isoformat()

    print(f"[M2] Starting data collection for {today_str}")
    print()

    results = {}

    # Strand 1: Competitive Moves
    print("[M2] Strand 1: Competitive Moves...")
    try:
        results["strand1_competitive"] = competitive.run(competitor_scrape_path=COMPETITOR_SCRAPE)
        print("  -> OK")
    except Exception as e:
        print(f"  [ERROR] {e}")
        results["strand1_competitive"] = {"error": str(e)}

    # Strand 2: Stack Obsolescence
    print("[M2] Strand 2: Stack Obsolescence...")
    try:
        results["strand2_stack"] = stack.run()
        print("  -> OK")
    except Exception as e:
        print(f"  [ERROR] {e}")
        results["strand2_stack"] = {"error": str(e)}

    # Strand 3: Regulation Drift
    print("[M2] Strand 3: Regulation Drift...")
    try:
        results["strand3_regulation"] = regulation.run()
        print("  -> OK")
    except Exception as e:
        print(f"  [ERROR] {e}")
        results["strand3_regulation"] = {"error": str(e)}

    # Strand 4: Positioning Gaps
    print("[M2] Strand 4: Positioning Gaps...")
    try:
        results["strand4_positioning"] = positioning.run()
        print("  -> OK")
    except Exception as e:
        print(f"  [ERROR] {e}")
        results["strand4_positioning"] = {"error": str(e)}

    # Strand 5: Internal Drift
    print("[M2] Strand 5: Internal Drift...")
    try:
        results["strand5_internal_drift"] = internal_drift.run(REPO_ROOT, today_str)
        print("  -> OK")
    except Exception as e:
        print(f"  [ERROR] {e}")
        results["strand5_internal_drift"] = {"error": str(e)}

    # Write JSON output
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_DIR / f"blindspot_{today_str}.json"
    payload = {
        "date": today_str,
        "gdrive_folder_id": GDRIVE_FOLDER_ID,
        "discord_webhook_set": bool(DISCORD_WEBHOOK),
        "strands": results,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print()
    print(f"[M2] Data written to {out_path}")
    print("[M2] Next step: run /m2-blindspot in your Claude Code session to synthesize, create Google Doc, and post to Discord.")

    if DRY_RUN_DISCORD:
        print("[M2] DRY RUN: DISCORD_M2_WEBHOOK not set.")
        print("[SETUP NEEDED] Add DISCORD_M2_WEBHOOK=<webhook url> to .env")


if __name__ == "__main__":
    main()
