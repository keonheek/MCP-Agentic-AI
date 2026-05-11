---
description: Read last night's evolution JSON and push Telegram morning summary. Run at 7am KST.
---

# /evolve-report

Read the evolution data from last night and push a Telegram morning summary.

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

## Step 2: Build Telegram message

Format the message exactly as:

```
*Evolution overnight (YYYY-MM-DD)*

While you slept, N improvements landed:

[Speed-to-Lead] <summary from strands.speed_to_lead.summary>
[Automation Workflows] <summary from strands.automation_workflows.summary>
[SaaS Integrations] <summary from strands.saas_integrations.summary>
[PIPA Tier P] <summary from strands.pipa_tier_p.summary>
[GEO/SEO Blog] <summary from strands.geo_seo_blog.summary>
[Service V] <summary from strands.service_v.summary>

Full diff: `git log --since=yesterday --oneline`
Today's M2 directive still standing: 1 cold IG DM before 10am.
```

For any strand where `flag_for_report: true`, append [FLAG] after the summary line.
For any strand where `tests_passed: false`, note: "(tests failed, not committed)".
For any strand where `skipped: true`, show: "SKIPPED - already ran".
For strands with errors, show: "ERROR - check evolution log".

## Step 3: Push to Telegram

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

## Step 4: Print to chat

After pushing, also print the full message to chat so Keonhee can read it in Claude Code without opening Telegram.

## Notes
- No em dashes in the Telegram message (rule)
- Use Markdown bold (*text*) for section headers
- Keep each strand line under 120 chars
- If Telegram credentials missing: print to chat only, do not error out
