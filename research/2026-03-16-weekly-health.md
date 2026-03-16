# Weekly Health — 2026-03-16

## Priority Status

| # | Priority | Status | Notes |
|---|----------|--------|-------|
| 1 | Consulting Emulation — Streamlit Cloud Deploy | **STALLED** | App built + Lambda live since 2026-03-13. Deploy is 15 min of human clicks. Blocked 3 days. |
| 2 | SDC Consulting Club | **MOVING** | Grader v2 complete. Saturday interviews done. Sunday screening remaining. |
| 3 | Portfolio — Samsung App visibility | **STALLED** | No movement since 2026-03-13. Push to GitHub + GEO README not started. |
| 4 | AI Building — Ongoing | **MOVING** | Hormozi agent built, NotebookLM (37 sources) set up, Auto-research pattern identified this week. |
| 5 | FinAgent — Production Upgrades | **STALLED** | Supabase restore pending since 2026-03-11 (5 days). Streamlit Cloud reboot not done. |
| 6 | AI CPA Exam | **UNKNOWN** | No tracking signal. Assumed ongoing. |

## Open Tasks (age)

**Immediate / Quick wins (< 1h each):**
- Streamlit Cloud deploy — consulting-emulation (3 days, 15 min human action)
- Slack MCP tokens — fill SLACK_BOT_TOKEN + SLACK_TEAM_ID (5 days pending)
- FinAgent Streamlit reboot — keonhee-finagent.streamlit.app (3 days, 2 min)
- Context7 MCP install (7 days in backlog)

**Blocked on human action:**
- Supabase restore (5 days stalled) — supabase.com/dashboard → Restore project
- GWS CLI auth — Google Cloud project setup needed
- SDC Sunday interviews screening

**Infrastructure / Dev:**
- DART MCP Server Card (`.well-known/mcp.json`) — 7+ days in backlog
- Samsung App → public GitHub + GEO README
- Auto-research skill eval loop (new this week)

**Long-tail (no deadline pressure):**
- LinkedIn About paste (draft ready)
- GitHub PAT renewal (expires Apr 8 — 23 days out, not urgent yet)
- Supabase Postgres checkpointer (blocked by restore above)

## Infrastructure

| Service | Status | Notes |
|---------|--------|-------|
| GitHub MCP | OK | PAT expires Apr 8. 23 days. No action needed yet. |
| Notion MCP | OK | Connected. Active. |
| DART MCP | NEEDS ATTENTION | Server built. DART_API_KEY confirmed in FinAgent .env. Not yet wired to Claude Code `.mcp.json`. |
| Slack MCP | NEEDS ATTENTION | In `.mcp.json` but tokens missing. Non-functional. |
| n8n MCP | NEEDS ATTENTION | In `.mcp.json` but API key missing. Non-functional. |
| NotebookLM | OK | Auth complete. Hormozi (37 sources) + Claude & AI Tools + Consulting Interview notebooks active. |
| AWS Lambda (consulting-emulation) | OK | Live at v7zapdvb10.execute-api.ap-northeast-2.amazonaws.com. Health confirmed. |
| Streamlit — keonhee-finagent | NEEDS ATTENTION | Fixes pushed to GitHub but Streamlit Cloud not rebooted. Running stale code. |
| Streamlit — keonhee-strategy | UNKNOWN | Not checked this week. Assumed live (static app). |
| Streamlit — keonhee-duediligence | NOT DEPLOYED | Code ready. Needs Streamlit Cloud UI deploy. |
| Supabase | NEEDS ATTENTION | Project paused (free tier). Blocking FinAgent checkpointing. |

## This Week's Recommendations

**#1 — Deploy consulting-emulation to Streamlit Cloud (15 min, highest ROI)**
Priority 1 has been blocked for 3 days by a 15-minute human action. This is the highest-impact, lowest-effort item on the board. A live URL at keonhee-duediligence.streamlit.app closes the portfolio visibility gap and completes the BCG-targeted build.
Steps: share.streamlit.io → New app → keonhee3337-art/consulting-emulation → app.py → URL: keonhee-duediligence → secrets: OPENAI_API_KEY + DARTFSS_API_KEY

**#2 — Reboot FinAgent Streamlit + Restore Supabase (10 min total)**
Two quick human actions that unblock live production fixes. FinAgent has 4 security/performance fixes sitting on GitHub but not live. Supabase restore unblocks Postgres checkpointing. Both take under 5 min each.

**#3 — Wire DART MCP to Claude Code `.mcp.json`**
DART MCP server is built and tested (live data confirmed 2026-03-13) but not connected to Claude Code. Adding it to `.mcp.json` gives Claude direct access to Korean financial data mid-conversation — closes the loop on the DART MCP build and makes it actually usable.
