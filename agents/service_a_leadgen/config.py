"""
Service A Lead-Gen Fleet: Central config.
All env vars, sheet IDs, thresholds, and constants live here.
"""

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# --- Google Sheets ---
SHEET_ID = "1w8X2uzo0ARrspp00Tpz8CL3LCXOF4RXIMp_tCemTqSI"
SHEET_TAB = "Prospects"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"

# Column index map (0-based, matches the 16-column header)
COL = {
    "date_added": 0,
    "brand_kr": 1,
    "brand_en": 2,
    "ig_handle": 3,
    "website": 4,
    "running_ads": 5,
    "latest_ad_url": 6,
    "response_time": 7,
    "platform": 8,
    "dm_name": 9,
    "dm_role": 10,
    "dm_contact": 11,
    "score": 12,
    "dm_draft": 13,
    "status": 14,
    "notes": 15,
}

# --- LLM ---
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY", "")
UPSTAGE_BASE_URL = "https://api.upstage.ai/v1/solar"
UPSTAGE_MODEL = "solar-pro"

# --- Telegram ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# --- Scoring weights ---
SCORE_ADS_ACTIVE = 30       # brand is running Meta ads right now
SCORE_SLOW_RESPONSE = 30    # estimated response time > 2 hrs
SCORE_DM_FOUND = 20         # decision maker found
SCORE_PLATFORM = 20         # platform = Cafe24 or Imweb (automation-ready)

# --- Playwright ---
PLAYWRIGHT_HEADLESS = True
REQUEST_TIMEOUT_MS = 15_000   # 15 s per page load

# --- A1 ---
META_AD_LIBRARY_URL = (
    "https://www.facebook.com/ads/library/"
    "?active_status=active&ad_type=all&country=KR"
    "&q=skincare&search_type=keyword_unordered"
)
A1_MAX_BRANDS = 20

# --- A2 ---
A2_SLOW_THRESHOLD_HRS = 2   # response time above this triggers slow-response score

# --- A6 ---
A6_TOP_N = 5                # prospects to include in morning brief
