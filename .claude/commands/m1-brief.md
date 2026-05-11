---
description: Synthesize weekly M1 orientation brief and email via Gmail MCP
---

# /m1-brief

Run `python agents/m1_orientation/m1.py` first to refresh `agents/m1_orientation/data/brief_TODAY.json`. If that fails (missing Obsidian path in cloud), continue with whatever inputs are available: todo.md, lessons.md, current-priorities.md, decisions/log.md, git log of last 7 days.

Synthesize a **5-bullet weekly brief**:

1. **Ship this week** - 1 to 3 specific actions from todo.md matched to top priority blockers in current-priorities.md
2. **Slipping** - decisions open more than 3 days, todos stalled more than 5 days, projects with no commits in the last 7 days
3. **Pattern check** - check lessons.md for repeating patterns. Quote the lesson if it fires.
4. **Drift signal** - compare last 7 days git commits to current-priorities. Call out mismatches.
5. **One blunt question** - the question being avoided.

Rules:
- NO em dashes. Use commas, colons, periods, parentheses.
- NO motivational filler.
- If slipping, say it plainly.
- Mix Korean and English naturally.
- Brief under 2000 characters.

Then send via Gmail MCP (the Gmail connector wired to this trigger):
- To: `keonhee3337@gmail.com`
- Subject: `[M1 Weekly] YYYY-MM-DD Orientation Brief`
- Body: the 5-bullet brief in plain text

If Gmail MCP unavailable, print brief to session output as fallback.
