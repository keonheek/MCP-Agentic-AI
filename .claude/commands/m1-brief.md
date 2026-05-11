---
description: Synthesize today's M1 morning brief from collected data and post to Discord
---

# /m1-brief

Read `agents/m1_orientation/data/brief_<today's date>.json`.

The file contains raw inputs: todo.md, lessons.md, current-priorities.md, decisions/log.md, git logs for main repo and subprojects, and last 3 Obsidian daily notes.

Synthesize a **5-bullet morning brief** using this exact structure:

1. **Ship today** - 1 to 2 specific actions from todo.md matched to top priority blockers in current-priorities.md
2. **Slipping** - decisions open more than 3 days, todos stalled more than 5 days, projects with no commits in the last 7 days
3. **Pattern check** - check lessons.md for repeating patterns in today's planned work. Quote the lesson if it fires.
4. **Drift signal** - compare last 7 days git commits to current-priorities. Call out mismatches specifically.
5. **One blunt question** - the question being avoided. Surface from open decisions, Obsidian tone, or stalled items.

Rules:
- NO em dashes anywhere in the brief text. Use commas, colons, periods, or parentheses.
- NO motivational filler. No "great work," no encouragement unless genuinely warranted.
- If slipping, say it plainly.
- Mix Korean and English naturally.
- Total brief must be under 1500 characters.

After synthesizing, post to Telegram using `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` from the root `.env`. Use this snippet via a quick shell command:

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

brief_text = """*M1 Morning Brief: <date>*\n<brief text>"""
# Split if over 4000 chars
if len(brief_text) <= 4000:
    push(brief_text)
else:
    for chunk in [brief_text[i:i+4000] for i in range(0, len(brief_text), 4000)]:
        push(chunk)
```

If `TELEGRAM_BOT_TOKEN` or `TELEGRAM_CHAT_ID` is not set, print the brief to chat instead.
