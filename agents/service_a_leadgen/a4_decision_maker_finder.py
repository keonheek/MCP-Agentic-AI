"""
A4: Decision maker finder
Searches for CMO / 마케팅 팀장 / 대표 for each brand.
Uses WebSearch (via requests to DuckDuckGo HTML) and pattern extraction.
Prefers marketing roles over CEO (marketing team more likely to reply).

Writes columns 10-12 (Decision maker name, role, contact).
"""

import re
import sys
import time
from typing import Optional
from urllib.parse import quote_plus

import requests

import sheet_utils
from config import COL

# Role priority (lower index = preferred)
TARGET_ROLES = [
    ("마케팅 팀장", "Marketing Lead"),
    ("CMO", "CMO"),
    ("마케팅 이사", "Marketing Director"),
    ("마케팅 본부장", "Marketing VP"),
    ("브랜드 매니저", "Brand Manager"),
    ("대표", "CEO/Founder"),
    ("CEO", "CEO"),
    ("창업자", "Founder"),
]

# LinkedIn URL pattern
LINKEDIN_PATTERN = re.compile(
    r"https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9\-_%]+", re.IGNORECASE
)

# Korean name pattern (2-4 Korean characters)
KR_NAME_PATTERN = re.compile(r"[가-힣]{2,4}")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8",
}


def find(dry_run: bool = False) -> None:
    """
    For every sheet row missing decision maker (columns 10-12), search and fill.
    """
    print("[A4] Starting decision maker search...")
    rows = sheet_utils.read_all_rows()

    for i, row in enumerate(rows):
        row_sheet_index = i + 2
        already_filled = (
            len(row) > COL["dm_name"] and row[COL["dm_name"]].strip()
        )
        if already_filled:
            continue

        brand_kr = row[COL["brand_kr"]] if len(row) > COL["brand_kr"] else ""
        brand_en = row[COL["brand_en"]] if len(row) > COL["brand_en"] else brand_kr
        if not brand_kr and not brand_en:
            continue

        print(f"[A4]   Searching: {brand_kr} / {brand_en}")

        if dry_run:
            print(f"[A4]   DRY RUN: would search decision maker for {brand_kr}")
            continue

        name, role, contact = _find_decision_maker(brand_kr, brand_en)
        print(f"[A4]     Found: {name} | {role} | {contact}")

        updates: dict = {}
        if name:
            updates["dm_name"] = name
        if role:
            updates["dm_role"] = role
        if contact:
            updates["dm_contact"] = contact

        if updates:
            sheet_utils.update_row_fields(row_sheet_index, updates)

        time.sleep(1.5)  # polite rate limiting

    print("[A4] Done.")


# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------

def _find_decision_maker(brand_kr: str, brand_en: str) -> tuple[str, str, str]:
    """
    Returns (name, role, contact_url_or_email).
    Tries multiple search queries in priority order.
    """
    for role_kr, role_en in TARGET_ROLES:
        # Try Korean brand + Korean role title
        result = _search(f'"{brand_kr}" {role_kr} LinkedIn')
        if result:
            name, contact = result
            return name, role_en, contact

        # Try English brand + Korean role
        if brand_en and brand_en != brand_kr:
            result = _search(f'"{brand_en}" {role_kr} LinkedIn')
            if result:
                name, contact = result
                return name, role_en, contact

    # Fallback: 잡코리아 / 원티드 search for current employees
    for role_kr, role_en in TARGET_ROLES[:4]:
        result = _search(f'"{brand_kr}" {role_kr} 마케팅 site:kr.linkedin.com OR site:wanted.co.kr')
        if result:
            name, contact = result
            return name, role_en, contact

    return "", "", ""


def _search(query: str) -> Optional[tuple[str, str]]:
    """
    Search DuckDuckGo HTML for the query.
    Returns (name, linkedin_url) if a LinkedIn profile is found, else None.
    """
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return None

        html = resp.text

        # Extract LinkedIn URLs from results
        linkedin_urls = LINKEDIN_PATTERN.findall(html)
        if not linkedin_urls:
            return None

        linkedin_url = linkedin_urls[0]

        # Try to extract a name near the URL in the HTML
        # Look for Korean name in snippet around the URL position
        idx = html.find(linkedin_url.split("//")[1][:20])  # find partial URL
        if idx == -1:
            return None

        snippet = html[max(0, idx - 300) : idx + 300]
        # Remove HTML tags
        clean_snippet = re.sub(r"<[^>]+>", " ", snippet)

        # Try Korean name first
        kr_names = KR_NAME_PATTERN.findall(clean_snippet)
        if kr_names:
            # Most likely the first 2-3 char sequence near the LinkedIn URL
            name = kr_names[0]
            return name, linkedin_url

        # Try Latin name (First Last pattern)
        latin_name_match = re.search(r"([A-Z][a-z]+ [A-Z][a-z]+)", clean_snippet)
        if latin_name_match:
            return latin_name_match.group(1), linkedin_url

        # URL found but no name extracted
        return "Unknown", linkedin_url

    except Exception as e:
        print(f"[A4]     Search error for '{query[:50]}...': {e}")
        return None


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    find(dry_run=dry)
