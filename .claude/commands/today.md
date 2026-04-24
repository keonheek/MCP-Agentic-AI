# /today — Daily Briefing

Give Keonhee a clean, scannable daily briefing. Execute these steps:

## Step 1 — Read context
Read these files in parallel:
- `context/current-priorities.md`
- `tasks/todo.md`
- `decisions/log.md` (last 5 entries only)

## Step 1b — Check Obsidian (if connected)
If the `obsidian` MCP server is available, call `get_daily_note()` for today.
If today's note has a Tasks section, include any unchecked items in the briefing.
If vault not connected, skip silently.

## Step 1c — Check Google Calendar
Call `mcp__claude_ai_Google_Calendar__list_events` for today (from 00:00 to 23:59 in Asia/Seoul timezone).
Include any events in the briefing under "### Today's Calendar".
If no events, skip the section silently.

## Step 1d — Check Gmail
Call `mcp__claude_ai_Gmail__search_threads` with query: `"subject:GEO OR subject:SDC OR from:soomgo.com OR from:kmong.com is:unread"`.
If unread threads found, list them under "### Unread Emails" (sender + subject, one line each).
If none, skip silently.

## Step 2 — Check what's new
Read the most recent daily AI report from `research/` (glob `research/*-daily-ai-report.md`, pick latest by filename date).

## Step 3 — Output the briefing

Format exactly as:

```
## Today — [WEEKDAY, DATE]

### Priorities Right Now
[Top 3 items from current-priorities.md, one line each, with status emoji]

### Non-Negotiables Today
[Daily non-negotiables from todo.md]

### Today's Calendar
[Events from Google Calendar — time + title, one line each. Skip if empty.]

### Unread Emails
[Unread Gmail threads matching GEO/SDC/Soomgo/Kmong — sender + subject. Skip if none.]

### This Week — What's Left
[Unchecked items from "This Week" in todo.md, sorted by importance]

### From Yesterday's AI Report
[2-3 bullet points from latest daily report — only implementable items]

### One Thing
[Single most important action Keonhee should do in the next 2 hours]
```

## Rules
- No walls of text. Each item = 1 line max.
- Flag anything 🔴 blocked or stalled >3 days.
- "One Thing" must be actionable right now, not a planning item.
- Do NOT update any files — this is read-only.
