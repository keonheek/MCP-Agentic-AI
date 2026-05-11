"""
A1: Meta Ad Library scanner
Finds Korean skincare brands running active paid ads in the past 30 days.
Writes new rows to the prospect sheet (columns 1-7).

Uses Playwright in headless mode. Facebook's Ad Library is a public page,
no login required for basic results.
"""

import re
import sys
import time
from datetime import date

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

import sheet_utils
from config import (
    META_AD_LIBRARY_URL,
    A1_MAX_BRANDS,
    PLAYWRIGHT_HEADLESS,
    REQUEST_TIMEOUT_MS,
    COL,
)

# Known ICP seed brands - used to pre-populate the sheet and validate scraping
SEED_BRANDS = [
    {"brand_kr": "넘버즈인", "brand_en": "Numbuzin", "ig": "@numbuzin.co", "site": "https://numbuzin.com"},
    {"brand_kr": "티르티르", "brand_en": "Tirtir", "ig": "@tirtir_official", "site": "https://tirtir.co.kr"},
    {"brand_kr": "조선미녀", "brand_en": "Beauty of Joseon", "ig": "@beautyofjoseon", "site": "https://beautyofjoseon.com"},
    {"brand_kr": "아누아", "brand_en": "Anua", "ig": "@anua_official", "site": "https://anuabeauty.com"},
    {"brand_kr": "라운드랩", "brand_en": "Round Lab", "ig": "@round_lab", "site": "https://roundlab.kr"},
    {"brand_kr": "스킨1004", "brand_en": "Skin1004", "ig": "@skin1004_official", "site": "https://skin1004.com"},
    {"brand_kr": "아이소이", "brand_en": "Isoi", "ig": "@isoi_official", "site": "https://isoi.com"},
    {"brand_kr": "마녀공장", "brand_en": "Manyo Factory", "ig": "@manyofactory_official", "site": "https://manyofactory.com"},
    {"brand_kr": "코스알엑스", "brand_en": "COSRX", "ig": "@cosrx", "site": "https://cosrx.com"},
    {"brand_kr": "클리오", "brand_en": "Clio", "ig": "@clio_cosmetics", "site": "https://clio-cosmetics.com"},
]


def scan(dry_run: bool = False) -> list[dict]:
    """
    Main entry point. Returns list of brand dicts found.
    In dry_run mode, uses seed brands only (no browser).
    """
    print("[A1] Starting Meta Ad Library scan...")

    if dry_run:
        print("[A1] DRY RUN: using seed brands, skipping Playwright.")
        brands = _format_seed_brands()
    else:
        try:
            scraped = _scrape_meta_ad_library()
            # Merge scraped brands with seeds (seeds fill gaps if scraping thin)
            brands = _merge_brands(scraped, _format_seed_brands())
        except Exception as e:
            print(f"[A1] Playwright scrape failed: {e}. Falling back to seed brands.")
            brands = _format_seed_brands()

    brands = brands[: A1_MAX_BRANDS]

    if dry_run:
        print(f"[A1] DRY RUN: would write {len(brands)} brands to sheet:")
        for b in brands:
            print(f"  {b['brand_kr']} | {b.get('ig', '')} | {b.get('site', '')}")
        print("[A1] Done (dry run, no sheet writes).")
        return brands

    existing = sheet_utils.get_existing_brands()
    added = 0
    for b in brands:
        if b["brand_kr"] in existing:
            print(f"[A1]   Skip (already in sheet): {b['brand_kr']}")
            continue
        row = sheet_utils.build_empty_row(
            brand_kr=b["brand_kr"],
            brand_en=b.get("brand_en", ""),
            ig_handle=b.get("ig", ""),
            website=b.get("site", ""),
        )
        row[COL["running_ads"]] = b.get("running_ads", "Y")
        row[COL["latest_ad_url"]] = b.get("latest_ad_url", "")
        sheet_utils.append_row(row)
        print(f"[A1]   Added: {b['brand_kr']}")
        added += 1

    print(f"[A1] Done. Added {added} new brands to sheet.")
    return brands


# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------

def _format_seed_brands() -> list[dict]:
    return [
        {
            "brand_kr": s["brand_kr"],
            "brand_en": s["brand_en"],
            "ig": s["ig"],
            "site": s["site"],
            "running_ads": "Y",   # seeds are known active advertisers
            "latest_ad_url": f"https://www.facebook.com/ads/library/?q={s['brand_en'].replace(' ', '+')}&country=KR",
        }
        for s in SEED_BRANDS
    ]


def _merge_brands(scraped: list[dict], seeds: list[dict]) -> list[dict]:
    """Merge scraped brands with seeds, deduplicating by brand_en (case-insensitive)."""
    seen = set()
    merged = []
    for b in scraped + seeds:
        key = b.get("brand_en", b.get("brand_kr", "")).lower()
        if key and key not in seen:
            seen.add(key)
            merged.append(b)
    return merged


def _scrape_meta_ad_library() -> list[dict]:
    """
    Scrape Facebook Ad Library for Korean skincare brands.
    Returns list of brand dicts with partial info.
    Note: Facebook heavily JS-renders; we extract advertiser names from page text.
    """
    brands = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=PLAYWRIGHT_HEADLESS)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="ko-KR",
        )
        page = context.new_page()

        try:
            page.goto(META_AD_LIBRARY_URL, timeout=REQUEST_TIMEOUT_MS * 2)
            # Wait for ad cards to appear
            page.wait_for_selector('[data-testid="ad-archive-renderer"]', timeout=REQUEST_TIMEOUT_MS)
        except PWTimeout:
            print("[A1] Timeout waiting for ad library results; returning partial.")
            browser.close()
            return brands

        # Scroll to load more results
        for _ in range(5):
            page.keyboard.press("End")
            time.sleep(1.5)

        # Extract advertiser names from ad cards
        try:
            cards = page.query_selector_all('[data-testid="ad-archive-renderer"]')
            seen_names = set()
            for card in cards[:A1_MAX_BRANDS * 2]:
                name_el = card.query_selector("strong") or card.query_selector("h3") or card.query_selector("span")
                if name_el:
                    name = name_el.inner_text().strip()
                    if name and name not in seen_names and len(name) > 1:
                        seen_names.add(name)
                        # Build a search URL for this brand as "latest ad URL"
                        ad_search_url = (
                            "https://www.facebook.com/ads/library/"
                            f"?q={name.replace(' ', '+')}&country=KR&active_status=active"
                        )
                        brands.append({
                            "brand_kr": name,
                            "brand_en": name,
                            "ig": "",
                            "site": "",
                            "running_ads": "Y",
                            "latest_ad_url": ad_search_url,
                        })
        except Exception as e:
            print(f"[A1] Error extracting ad cards: {e}")

        browser.close()

    print(f"[A1] Scraped {len(brands)} brands from Meta Ad Library.")
    return brands


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    scan(dry_run=dry)
