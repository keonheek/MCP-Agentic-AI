---
description: Read last night's evolution JSON and push Telegram morning summary with ranked impact tiers. Run at 7am KST.
---

# /evolve-report

Read the evolution data from last night and push a ranked Telegram morning summary.

## Step 1: Find and read the JSON

```python
import json
from pathlib import Path
from datetime import date, timedelta

data_dir = Path("C:/Users/keonh/Dev/MCP_Agentic_AI/agents/evolution_loop/data")

# Try today first (if evolve ran past midnight), then yesterday
for delta in [0, 1]:
    target_date = date.today() - timedelta(days=delta)
    f = data_dir / f"evolution_{target_date.isoformat()}.json"
    if f.exists():
        data = json.loads(f.read_text(encoding="utf-8"))
        print(f"Found: {f}")
        break
else:
    print("No evolution JSON found. Has /evolve run yet tonight?")
    data = None
```

If no file found, print "No evolution data for last night. Run /evolve first." and stop.

## Step 2: Also read the skip log

```python
skip_log = data_dir / "evolution_skips.jsonl"
skipped_entries = []
if skip_log.exists():
    for line in skip_log.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            # Only keep entries from last night
            if obj.get("date") == target_date.isoformat():
                skipped_entries.append(obj)
        except Exception:
            pass
```

## Step 3: Classify each strand result by impact tier

Apply this logic to every strand in `data["strands"]`:

```
HIGH impact if ANY of:
  - flag_for_report is True AND live_signal is True
  - improvement_type == "log_pipc_news" AND action_required is True
  - breaking_change is True
  - "LIVE" in summary AND flag_for_report is True

MEDIUM impact if ANY of:
  - improvement_type in ["log_tool_changelog", "add_edge_case_test", "add_case_study", "platform_changelog_check", "scan_brand", "log_query_shift", "add_kakao_variant", "add_e2e_edge_case"]
  - live_signal is True (but not HIGH)
  - tests_passed is True AND committed is True

LOW impact if:
  - improvement_type in ["add_pipa_metric", "log_kakao_changelog", "add_backlog_stub", "log_edge_case_patch", "add_schema_pattern", "update_keyword_bank", "update_stack_status", "log_ad_observation"]
  - Or none of the MEDIUM/HIGH conditions match
```

For skipped strands (quality gate failed, test failed, or no signal): do NOT rank them. List separately in SKIPPED STRANDS section.

## Step 4: Determine THE ONE THING

- If any HIGH items: THE ONE THING = the single most actionable HIGH finding in plain English
- If no HIGH items: THE ONE THING = "Nothing critical overnight. Sleep was clean."

## Step 5: Build the Telegram message

Format the message EXACTLY as:

```
*Evolution overnight (YYYY-MM-DD)*

THE ONE THING: [one sentence, plain English, no jargon]

*HIGH IMPACT (N):*
- [strand]: [summary] [FLAG if flag_for_report=True]

*MEDIUM IMPACT (N):*
- [strand]: [summary]

*LOW IMPACT (N):*
- [strand]: [summary]

*SKIPPED STRANDS:*
[strand]: [reason]
(or "None" if no skips)

Full diff: `git log --since=yesterday --oneline`
Today's M2 directive still standing: 1 cold IG DM before 10am.
```

Rules:
- No em dashes anywhere in the message
- Use Markdown bold (*text*) for section headers
- If a strand has tests_passed: False, append "(tests failed, not committed)"
- If a strand has an error, show: "ERROR: check evolution log"
- If a strand was skipped by quality gate: list in SKIPPED STRANDS with the gate reason
- If no HIGH items at all, omit the HIGH section entirely (do not show "HIGH IMPACT (0):")
- Same for MEDIUM and LOW: omit if empty

## Step 6: Push to Telegram

```python
import os, requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path("C:/Users/keonh/Dev/MCP_Agentic_AI/.env"))
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def push_telegram(text: str):
    if not TOKEN or not CHAT_ID:
        print("[TELEGRAM] Credentials not set. Printing message instead:")
        print(text)
        return
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        },
        timeout=10,
    )
    if r.ok:
        print(f"[TELEGRAM] Sent successfully. message_id: {r.json().get('result', {}).get('message_id')}")
    else:
        print(f"[TELEGRAM] Failed: {r.status_code} {r.text[:200]}")

# Split if over 4000 chars
if len(message) <= 4000:
    push_telegram(message)
else:
    for chunk in [message[i:i+4000] for i in range(0, len(message), 4000)]:
        push_telegram(chunk)
```

## Step 7: Print to chat

After pushing, also print the full ranked message to chat so Keonhee can read it in Claude Code without opening Telegram.

## Notes
- No em dashes in the Telegram message (hard rule)
- Use Markdown bold (*text*) for section headers
- Keep each strand line under 120 chars
- If Telegram credentials missing: print to chat only, do not error out
- Impact tier is for Keonhee's morning triage, not for automation decisions
- HIGH items with action_required=True need a human decision before any code changes
