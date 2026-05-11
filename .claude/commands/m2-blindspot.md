---
description: Synthesize weekly M2 blindspot report from collected data, create Google Doc, post Discord summary
---

# /m2-blindspot

Read `agents/m2_blindspot/data/blindspot_<today's date>.json`.

The file contains 5 strands of raw data. Process each strand:

## Strand 1: Competitive Moves
The JSON contains `strand1_competitive` with `queries` (list of search strings) and `baseline_pricing` and `competitor_scrape_excerpt`.
- Run WebSearch for each query (limit to 2026 content)
- Compare fresh results against the baseline pricing
- Find: new AI agency entrants in Korea, any competitor pricing below baseline, new service offerings, anyone claiming the 화장품 D2C vertical
- Output 2-5 findings with sources, or "No new competitive moves detected this week"
- Output 1 action item

## Strand 2: Stack Obsolescence
The JSON contains `strand2_stack` with `current_stack` manifest and `queries`.
- Run WebSearch for each query (look for releases in the past 7 days only)
- Score each finding: HIGH (would change architecture), MEDIUM (worth monitoring), LOW (minor tweak)
- Prioritize: Anthropic > OpenAI > Google > Korean-specific > others
- Output 2-5 findings, or "No significant stack-affecting releases this week"
- Output 1 action item

## Strand 3: Regulation Drift
The JSON contains `strand3_regulation` with `regulation_baseline` and `queries`.
- Run WebSearch for each query
- Only flag changes from the past 7 days OR upcoming effective dates within 90 days
- Any PIPA change = HIGH priority regardless of magnitude
- Output 2-5 findings with service impact, or "No regulation changes detected this week"
- Output 1 action item

## Strand 4: Positioning Gaps
The JSON contains `strand4_positioning` with `current_positioning` and `queries`.
- Run WebSearch for each query
- Flag unclaimed territory (things he could rank for that no one owns yet)
- Flag defensive gaps (queries where competitors rank and he has zero presence)
- Be specific about what content/page/GitHub repo would close each gap
- Output 2-5 findings, or "No new positioning gaps detected this week"
- Output 1 action item

## Strand 5: Internal Drift
The JSON contains `strand5_internal_drift` with decisions, lessons, todo, priorities, and Obsidian notes as raw text.
- NO web search needed for this strand
- Find 1-3 specific internal drift signals:
  - The 2026-04-06 build-vs-ship pattern: is he building more tools instead of contacting clients?
  - Lessons that are clearly being violated right now (match lesson text to current behavior)
  - Decisions made but then quietly abandoned without a log entry
- Each finding must cite a specific file, date, or entry
- Do NOT soften findings
- Output 1-3 findings maximum, or "No drift detected this week"
- Output 1 brutally direct action

## Report Rules
- NO em dashes anywhere. Use commas, colons, periods, or parentheses.
- Mix Korean and English naturally.
- Be brutal and specific. No filler.

## After synthesizing all 5 strands:

1. Create a Google Doc via `gws docs create --title "M2 Blindspot Report <date>" --body-file <tmp_file> --folder 1PU6EX-ay-gr3B8FeDwyKOac2zpwXynKy --format json`. Write the full report to a temp file first, pass path to gws.

2. Post Telegram summary using `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` from the root `.env`:

```python
import os, requests
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def push(text: str, parse_mode: str = "Markdown"):
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    )
    r.raise_for_status()
    return r.json()

summary = "*M2 Blindspot Report Ready: <date>*\n<5-line summary, one per strand, first finding each>\nDoc: <doc URL>"
# Split if over 4000 chars
if len(summary) <= 4000:
    push(summary)
else:
    for chunk in [summary[i:i+4000] for i in range(0, len(summary), 4000)]:
        push(chunk)
```

If gws CLI is not found, skip Doc creation and print report to chat. If `TELEGRAM_BOT_TOKEN` or `TELEGRAM_CHAT_ID` is not set, print the Telegram payload to chat.
