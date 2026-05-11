"""
Creates the Master Generation Sheet for 1stmover AI Video pipeline.
Uses Google Sheets API directly via OAuth from client_secret.json.

Run: python create_sheet.py
Opens browser once to authorize → saves token → creates sheet.
"""
import json
import os
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SECRET_FILE = Path("C:/Users/keonh/.config/gws/client_secret.json")
TOKEN_FILE  = Path("C:/Users/keonh/.config/gws/token.json")

SHEET_TITLE = "1stmover - AI Video Master Generation Log"

TABS = {
    "all_generations": [
        "timestamp", "client_slug", "angle_id", "angle_name",
        "hook_variant", "model", "style", "prompt",
        "result_url", "job_id", "status", "eval_score",
        "ctr", "cpm", "cvr", "notes"
    ],
    "by_client": [
        "client_slug", "brand_name", "icp_track",
        "total_generations", "approved_count", "live_count",
        "best_angle_id", "best_ctr", "best_cpm"
    ],
    "by_angle": [
        "angle_id", "angle_name", "hook_type",
        "objection_killed", "belief_installed",
        "generation_count", "approval_rate",
        "avg_ctr", "avg_cpm", "avg_cvr", "fatigue_flag"
    ],
    "creative_slate": [
        "priority", "client_slug", "angle_id",
        "style", "hook_variant", "prompt_draft",
        "status", "notes"
    ],
}


def get_credentials():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
    return creds


def create_sheet(service):
    body = {"properties": {"title": SHEET_TITLE}}
    sheet = service.spreadsheets().create(body=body).execute()
    sheet_id = sheet["spreadsheetId"]
    print(f"[ok] Sheet created: https://docs.google.com/spreadsheets/d/{sheet_id}")
    return sheet_id, sheet["sheets"][0]["properties"]["sheetId"]


def add_tabs_and_headers(service, sheet_id, first_sheet_gid):
    requests = []

    # Rename first default tab to all_generations
    first_tab = list(TABS.keys())[0]
    requests.append({
        "updateSheetProperties": {
            "properties": {"sheetId": first_sheet_gid, "title": first_tab},
            "fields": "title"
        }
    })

    # Add remaining tabs
    for tab_name in list(TABS.keys())[1:]:
        requests.append({"addSheet": {"properties": {"title": tab_name}}})

    service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={"requests": requests}
    ).execute()

    # Fetch updated sheet to get all tab IDs
    meta = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    tab_gids = {s["properties"]["title"]: s["properties"]["sheetId"]
                for s in meta["sheets"]}

    # Write headers to each tab
    data = []
    for tab_name, headers in TABS.items():
        data.append({
            "range": f"{tab_name}!A1",
            "values": [headers]
        })

    service.spreadsheets().values().batchUpdate(
        spreadsheetId=sheet_id,
        body={"valueInputOption": "RAW", "data": data}
    ).execute()

    # Bold + freeze header row on all tabs
    fmt_requests = []
    for tab_name, headers in TABS.items():
        gid = tab_gids[tab_name]
        fmt_requests.append({
            "repeatCell": {
                "range": {"sheetId": gid, "startRowIndex": 0, "endRowIndex": 1},
                "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                "fields": "userEnteredFormat.textFormat.bold"
            }
        })
        fmt_requests.append({
            "updateSheetProperties": {
                "properties": {"sheetId": gid, "gridProperties": {"frozenRowCount": 1}},
                "fields": "gridProperties.frozenRowCount"
            }
        })

    service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={"requests": fmt_requests}
    ).execute()

    print("[ok] All tabs created with headers (bold + frozen row 1)")


def main():
    creds   = get_credentials()
    service = build("sheets", "v4", credentials=creds)

    sheet_id, first_gid = create_sheet(service)
    add_tabs_and_headers(service, sheet_id, first_gid)

    env_path = Path("C:/Users/keonh/Dev/MCP_Agentic_AI/.env")
    line = f"\nGWS_GENERATION_SHEET_ID={sheet_id}\n"
    with open(env_path, "a", encoding="utf-8") as f:
        f.write(line)

    print(f"\n[ok] Added to .env: GWS_GENERATION_SHEET_ID={sheet_id}")
    print(f"\n>>> Open: https://docs.google.com/spreadsheets/d/{sheet_id}")


if __name__ == "__main__":
    main()
