"""
A3: E-commerce platform detector
Detects whether a brand's site runs on Cafe24, Imweb, Smart Store, Shopify, or other.
Writes column 9 (Platform) for each sheet row that is missing it.

Detection method: fetch homepage HTML, check for platform fingerprints in:
  - Meta tags
  - Asset / script URLs
  - Footer text
  - HTTP response headers
"""

import re
import sys
from typing import Optional

import requests

import sheet_utils
from config import COL

# --- Platform detection rules ---
# Each entry: (platform_name, list_of_regex_or_string_signals)
PLATFORM_SIGNATURES: list[tuple[str, list[str]]] = [
    (
        "Cafe24",
        [
            r"cafe24\.com",
            r"EC_PRODUCT_DETAIL",
            r"ecshop",
            r"ECPayment",
            r"cafe24shop\.com",
        ],
    ),
    (
        "Imweb",
        [
            r"imweb\.me",
            r"imwebimg\.com",
            r"imweb-img\.com",
            r"cdn\.imweb",
        ],
    ),
    (
        "Smart Store",
        [
            r"smartstore\.naver\.com",
            r"naver\.me/shop",
            r"pay\.naver\.com",
            r"smartstore",
        ],
    ),
    (
        "Shopify",
        [
            r"cdn\.shopify\.com",
            r"Shopify\.theme",
            r"myshopify\.com",
            r"shopify-section",
        ],
    ),
    (
        "Makeshop",
        [
            r"makeshop\.co\.kr",
            r"makeshopdf\.co\.kr",
        ],
    ),
    (
        "WooCommerce",
        [
            r"wp-content",
            r"woocommerce",
        ],
    ),
]

# Compile all patterns
COMPILED: list[tuple[str, list[re.Pattern]]] = [
    (name, [re.compile(sig, re.IGNORECASE) for sig in sigs])
    for name, sigs in PLATFORM_SIGNATURES
]


def detect(dry_run: bool = False) -> None:
    """
    For every sheet row missing Platform (column 9), detect and write it.
    """
    print("[A3] Starting platform detection...")
    rows = sheet_utils.read_all_rows()

    for i, row in enumerate(rows):
        row_sheet_index = i + 2
        website = row[COL["website"]] if len(row) > COL["website"] else ""
        already_filled = len(row) > COL["platform"] and row[COL["platform"]].strip()

        if already_filled:
            continue
        if not website:
            print(f"[A3]   Row {row_sheet_index}: no website, skipping.")
            continue

        brand = row[COL["brand_kr"]] if len(row) > COL["brand_kr"] else f"row {row_sheet_index}"

        if dry_run:
            print(f"[A3]   DRY RUN: would detect platform for {brand} ({website})")
            continue

        print(f"[A3]   Detecting: {brand} ({website})")
        platform = _detect_platform(website)
        print(f"[A3]     Platform: {platform}")

        sheet_utils.update_row_fields(row_sheet_index, {"platform": platform})

    print("[A3] Done.")


# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------

def _detect_platform(website: str) -> str:
    """Fetch website and return detected platform name, or 'Other'."""
    html, headers_str = _fetch_page(website.rstrip("/"))
    if not html:
        return "Other"

    content = html + " " + headers_str

    for platform_name, patterns in COMPILED:
        for pattern in patterns:
            if pattern.search(content):
                return platform_name

    # Check meta generator tag
    gen_match = re.search(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if gen_match:
        gen_value = gen_match.group(1)
        if "cafe24" in gen_value.lower():
            return "Cafe24"
        if "shopify" in gen_value.lower():
            return "Shopify"
        if "wordpress" in gen_value.lower():
            return "WooCommerce"

    return "Other"


def _fetch_page(url: str, timeout: int = 10) -> tuple[str, str]:
    """Return (html_body, headers_as_string) or ("", "") on failure."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8",
        }
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        if resp.status_code == 200:
            headers_str = str(resp.headers)
            # Also check final URL for Smart Store redirect
            if "smartstore.naver.com" in resp.url:
                return resp.text, headers_str + " smartstore.naver.com"
            return resp.text, headers_str
    except Exception as e:
        print(f"[A3]     Fetch error: {e}")
    return "", ""


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    detect(dry_run=dry)
