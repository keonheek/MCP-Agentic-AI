# Weekly System Health Check — Automated Prompt

_This file is read by the `/schedule` cron job. Fires every Monday 9am._

## Instructions

Run a full system health audit autonomously. Do not ask for input.

### Check 1 — Priority Movement
Read `context/current-priorities.md` and `decisions/log.md`. For each priority, assess if it moved since last Monday. Flag anything stalled.

### Check 2 — Task Queue
Read `tasks/todo.md`. Remove completed items. Identify anything that's been sitting for 7+ days.

### Check 3 — Projects Status
For each project in `projects/`:
- Is there a README? Is it current?
- Any open blockers?
- Any deployments that could go down (Railway, Streamlit)?

### Check 4 — Infrastructure
- DART API key: still pending? Flag if so.
- n8n: is it connected? Check `.mcp.json`
- GitHub PAT: check expiry (expires Apr 8 2026 — flag when < 14 days out)
- Railway (RAG Demo): still live?
- Streamlit apps: keonhee-finagent.streamlit.app, keonhee-strategy.streamlit.app

### Check 5 — AI Skill Gaps
Based on this week's daily AI reports in `research/`, identify:
- Any new tool or framework that Keonhee hasn't yet added to his stack
- Skills or agents that should be built

### Output

Write a weekly health report to `research/YYYY-MM-DD-weekly-health.md`:
```
# Weekly Health — [DATE]

## Priority Status
[each priority: MOVING / STALLED / BLOCKED]

## Open Tasks
[list with age]

## Infrastructure
[each service: OK / NEEDS ATTENTION]

## This Week's Recommendations
[top 3 actions, ranked by impact]
```

Then say: "Weekly health check complete — [N] issues flagged."
