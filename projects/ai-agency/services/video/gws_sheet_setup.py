"""
Step 8: GWS CLI Master Generation Sheet setup
Run: python gws_sheet_setup.py
Creates a Google Sheet with 4 tabs for tracking all Higgsfield generations.

Prerequisites:
  npm install -g @google/gws-cli
  gws auth login
"""

import subprocess
import json
import sys

SHEET_TITLE = "1stmover - AI Video Master Generation Log"

SCHEMA = {
    "sheets": [
        {
            "name": "all_generations",
            "headers": [
                "timestamp", "client_slug", "angle_id", "angle_name",
                "hook_variant", "model", "style",
                "prompt", "result_url", "job_id",
                "status",          # discovered / approved / filming / complete / blocked
                "eval_score",      # 1-10, from Braintrust
                "ctr", "cpm", "cvr",  # filled in after ad goes live
                "notes"
            ]
        },
        {
            "name": "by_client",
            "headers": [
                "client_slug", "brand_name", "icp_track",
                "total_generations", "approved_count", "live_count",
                "best_angle_id", "best_ctr", "best_cpm"
            ]
        },
        {
            "name": "by_angle",
            "headers": [
                "angle_id", "angle_name", "hook_type",
                "objection_killed", "belief_installed",
                "generation_count", "approval_rate",
                "avg_ctr", "avg_cpm", "avg_cvr",
                "fatigue_flag"  # TRUE when CTR drops below baseline * 0.7
            ]
        },
        {
            "name": "creative_slate",
            "headers": [
                "priority", "client_slug", "angle_id",
                "style", "hook_variant", "prompt_draft",
                "status",   # blank / queued / generated / approved / live
                "notes"
            ]
        }
    ]
}

def create_sheet():
    """Create the Google Sheet using GWS CLI."""
    print(f"Creating: {SHEET_TITLE}")

    GWS = "C:/Users/keonh/AppData/Roaming/npm/gws.cmd"
    cmd = [GWS, "sheets", "create", "--title", SHEET_TITLE]

    result = subprocess.run(cmd, capture_output=True, text=True, shell=False)

    if result.returncode != 0:
        print(f"[error] {result.stderr}")
        print("\n--- MANUAL FALLBACK ---")
        print("GWS CLI not available. Create the sheet manually:")
        print(f"1. Open Google Sheets → New spreadsheet → Rename to:\n   '{SHEET_TITLE}'")
        print("2. Create 4 tabs:")
        for sheet in SCHEMA["sheets"]:
            print(f"   Tab: {sheet['name']}")
            print(f"   Row 1 headers: {', '.join(sheet['headers'])}")
        return

    print(f"[ok] Sheet created: {result.stdout.strip()}")
    print("\nAdd the sheet URL to .env:")
    print("GWS_GENERATION_SHEET_ID=<id from URL>")


def log_generation(slug, angle_id, angle_name, hook, model, style, prompt, result_url, job_id):
    """
    Append one row to all_generations tab.
    Call this after every Higgsfield generation.
    """
    from datetime import datetime
    row = {
        "timestamp": datetime.now().isoformat(),
        "client_slug": slug,
        "angle_id": angle_id,
        "angle_name": angle_name,
        "hook_variant": hook,
        "model": model,
        "style": style,
        "prompt": prompt,
        "result_url": result_url,
        "job_id": job_id,
        "status": "discovered",
        "eval_score": "",
        "ctr": "", "cpm": "", "cvr": "",
        "notes": ""
    }

    cmd = [
        "gws", "sheets", "append",
        "--sheet-id", "${GWS_GENERATION_SHEET_ID}",
        "--tab", "all_generations",
        "--data", json.dumps(row)
    ]
    subprocess.run(cmd)
    print(f"[logged] {slug} / {angle_id} / {job_id}")


if __name__ == "__main__":
    create_sheet()
