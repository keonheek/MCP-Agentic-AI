"""
Google Sheets helper.
Uses the Google Sheets REST API directly via google-auth + requests.
This bypasses the gws CLI entirely for all operations, which resolves
Windows command-line Unicode encoding issues with Korean text.

The gws token.json (~/.config/gws/token.json) provides the OAuth credentials.
"""

import json
import os
from datetime import date
from typing import Optional

import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleAuthRequest

from config import SHEET_ID, SHEET_TAB, COL

# ---------------------------------------------------------------------------
# OAuth credential management
# ---------------------------------------------------------------------------

_GWS_TOKEN_PATH = os.path.expanduser("~/.config/gws/token.json")
_SHEETS_API = "https://sheets.googleapis.com/v4/spreadsheets"
_creds: Optional[Credentials] = None


def _get_credentials() -> Credentials:
    """
    Load and refresh OAuth credentials from gws token store.
    Always attempts a refresh on first call (the stored token may be expired
    even if google-auth reports it as valid based on the expiry field).
    """
    global _creds
    if _creds and _creds.valid and _creds.token:
        return _creds

    with open(_GWS_TOKEN_PATH, "r", encoding="utf-8") as f:
        token_data = json.load(f)

    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=token_data.get("client_id"),
        client_secret=token_data.get("client_secret"),
        scopes=token_data.get("scopes"),
    )

    # Always refresh: the stored token may be expired and google-auth can
    # misreport validity if the expiry timestamp is in an unexpected format.
    creds.refresh(GoogleAuthRequest())

    # Persist refreshed token so gws CLI stays in sync
    token_data["token"] = creds.token
    token_data["expiry"] = creds.expiry.isoformat() if creds.expiry else None
    with open(_GWS_TOKEN_PATH, "w", encoding="utf-8") as f:
        json.dump(token_data, f, ensure_ascii=False, indent=2)

    _creds = creds
    return creds


def _auth_header() -> dict:
    creds = _get_credentials()
    return {"Authorization": f"Bearer {creds.token}", "Content-Type": "application/json"}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _range(cell_range: str) -> str:
    return f"{SHEET_TAB}!{cell_range}"


def _api_get(path: str, params: dict = None) -> dict:
    url = f"{_SHEETS_API}/{SHEET_ID}{path}"
    resp = requests.get(url, headers=_auth_header(), params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def _api_post(path: str, body: dict, params: dict = None) -> dict:
    url = f"{_SHEETS_API}/{SHEET_ID}{path}"
    resp = requests.post(
        url, headers=_auth_header(), params=params,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def _api_put(path: str, body: dict, params: dict = None) -> dict:
    url = f"{_SHEETS_API}/{SHEET_ID}{path}"
    resp = requests.put(
        url, headers=_auth_header(), params=params,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def read_all_rows() -> list[list[str]]:
    """Return all data rows (excluding header, row 1) as list of lists."""
    data = _api_get(f"/values/{_range('A2:P1000')}")
    return data.get("values", [])


def append_row(row: list) -> None:
    """Append a single row to the sheet."""
    normalised = [str(v) if v is not None else "" for v in row]
    _api_post(
        f"/values/{_range('A1')}:append",
        body={"values": [normalised]},
        params={"valueInputOption": "RAW", "insertDataOption": "INSERT_ROWS"},
    )


def update_cell(row_index_1based: int, col_key: str, value: str) -> None:
    """
    Update a single cell.
    row_index_1based: 2 = first data row (row 1 is the header).
    """
    col_letter = _col_letter(COL[col_key] + 1)
    cell = f"{col_letter}{row_index_1based}"
    _api_put(
        f"/values/{_range(cell)}",
        body={"values": [[str(value)]]},
        params={"valueInputOption": "RAW"},
    )


def update_row_fields(row_index_1based: int, updates: dict) -> None:
    """
    Update multiple fields for a row in one batchUpdate call.
    updates: {col_key: value, ...}
    """
    data = []
    for col_key, value in updates.items():
        col_letter = _col_letter(COL[col_key] + 1)
        cell = f"{col_letter}{row_index_1based}"
        data.append({
            "range": _range(cell),
            "values": [[str(value) if value is not None else ""]],
        })

    _api_post(
        "/values:batchUpdate",
        body={"valueInputOption": "RAW", "data": data},
    )


def build_empty_row(brand_kr: str, brand_en: str = "", ig_handle: str = "",
                     website: str = "") -> list:
    """Return a 16-element row populated with just the basics."""
    row = [""] * 16
    row[COL["date_added"]] = str(date.today())
    row[COL["brand_kr"]] = brand_kr
    row[COL["brand_en"]] = brand_en
    row[COL["ig_handle"]] = ig_handle
    row[COL["website"]] = website
    row[COL["status"]] = "New"
    return row


def get_existing_brands() -> set[str]:
    """Return set of brand names (KR) already in the sheet."""
    rows = read_all_rows()
    return {r[COL["brand_kr"]] for r in rows if len(r) > COL["brand_kr"]}


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _col_letter(n: int) -> str:
    """Convert 1-based column number to spreadsheet letter (A, B, ..., Z, AA...)."""
    result = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result
