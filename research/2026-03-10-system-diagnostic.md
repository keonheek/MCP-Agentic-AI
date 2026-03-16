# System Diagnostic — 2026-03-10

_Full audit of Keonhee's second brain, automation layer, portfolio, and gaps._

---

## 1. Automation Layer

### Hooks (3 active)
| Hook | Status | Assessment |
|---|---|---|
| pre-write-guard | ✅ Active | Blocks `.env` writes. Solid. |
| rm-rf warn | ✅ Active | Confirms before destructive deletes. Good. |
| post-write-log | ✅ Active | Logs context file writes to decision log. |

**Gap:** No post-tool hook for Bash commands — destructive shell commands (e.g. `rm`, `git reset`) bypass the write guard. A `pre-bash-guard` hook checking for `rm -rf`, `git reset --hard`, `git push --force` would add a safety net.

### Cron Jobs (2 active as of today)
| Job | Schedule | Status |
|---|---|---|
| Daily AI Report | 8:03am daily | ✅ Set this session |
| Weekly Health Check | Monday 9am | ✅ Set this session |

**Critical limitation:** Crons are session-only. They die when VS Code closes and auto-expire after 3 days. You must run `/schedule` each time you open a new session to re-activate them. This is the biggest constraint on true autonomous operation.

**Workaround (not yet built):** A Windows Task Scheduler job that opens VS Code + the project and triggers a Claude session on boot would make this persistent. Effort: ~1 hour.

### Skills (11 active)
| Skill | Last Used | Utilization |
|---|---|---|
| research | Regularly | HIGH |
| apply | This session | HIGH |
| priorities | This session | HIGH |
| session-end | Occasionally | MEDIUM |
| geo | Rarely | LOW |
| financial-analyst | Rarely | LOW |
| data-analyst | Rarely | LOW |
| interview-prep | Once (Kearney) | LOW |
| web-search | Occasionally | MEDIUM |
| code-researcher | Rarely | LOW |
| database-builder | Rarely | LOW |

**Gap — geo:** GEO is a high-leverage skill with zero follow-through. GitHub README is public-facing portfolio material and hasn't been optimized. One session with `/geo:github-readme` on DART MCP Server + FinAgent READMEs would compound for months.

**Gap — missing skill:** No `job-monitor` skill to scan target company career pages (Deloitte Korea, Accenture Korea, BCG, McKinsey) for new AI/consulting postings. Could be built on top of the `web-search` skill with a cron trigger.

### Agents (5 deployed)
| Agent | Model | Active Use |
|---|---|---|
| director-agent | Sonnet | LOW — should be used for multi-step planning |
| coding-agent | Sonnet | MEDIUM |
| writing-agent | Sonnet | MEDIUM |
| notion-agent | Haiku | LOW |
| research-agent | Haiku | MEDIUM |

**Gap — notion-agent:** Notion is connected but underused as a second brain layer. Daily AI reports could be auto-logged to a Notion database (Research Log) in addition to the `research/` folder. The notion-agent can do this in parallel with each daily report.

**Gap — director-agent:** Multi-step tasks (like "apply to Deloitte: research firm, draft cover letter, tailor CV, log decision") should be delegated to the director. Currently it's being skipped and tasks are done piecemeal.

---

## 2. Project Status

| Project | Status | Blocker | Next Action |
|---|---|---|---|
| FinAgent | ✅ Live | None | Add FinAgent v2 router agent |
| Samsung DART App | ✅ Live | None | GEO-optimize README |
| RAG Demo (Railway) | ✅ Live | Path bug fixed | Verify it's actually responding |
| DART MCP Server | Built, not public | No GitHub repo yet | Push to GitHub (30 min) |
| SDC Grader | ✅ Working | None | Full end-to-end test with a real email |
| n8n Integration | ⚠️ Partial | API key added, VS Code not restarted | Restart VS Code, verify MCP loads |
| DART API Connection | ⚠️ Blocked | Needs DART_API_KEY from opendart.fss.or.kr | Register and get key |
| GEO Agency | Not started | No client | Run first free audit via SDC connection |
| LangChain Learning | Not started | Deferred | Start worktree, do one tutorial |

---

## 3. Portfolio Gaps

### What's built vs. what's visible
| Project | Built | GitHub | GEO-Optimized | On CV |
|---|---|---|---|---|
| FinAgent | ✅ | ❌ | ❌ | ✅ |
| Samsung DART App | ✅ | ❌ | ❌ | ✅ |
| RAG Demo | ✅ | ✅ | ❌ | ✅ |
| DART MCP Server | ✅ | ❌ | ❌ | ❌ |
| SDC Grader | ✅ | ❌ | N/A | ✅ (via SDC bullet) |

**Critical gap:** FinAgent and Samsung DART App are live and deployed but have no public GitHub repos. Any recruiter or AI system searching for Keonhee's work will only find the RAG demo. Two repos + GEO-optimized READMEs would triple the portfolio footprint.

### LinkedIn
- About section: drafted in `projects/next-ai-role/linkedin-about.md`, not yet posted.
- Not GEO-optimized. Currently invisible to AI systems searching for Korean AI developers.

---

## 4. Infrastructure Health

| Service | Status | Action Needed |
|---|---|---|
| Railway (RAG Demo) | Likely live | Verify URL responds |
| Streamlit — FinAgent | ✅ Live | None |
| Streamlit — Samsung | ✅ Live | None |
| Pinecone (kearney-demo index) | ✅ Active | None |
| Supabase | ✅ Active | None |
| GitHub PAT 'superagent' | ⚠️ Expires Apr 8 2026 | Renew before Apr 8 |
| DART API key | ❌ Missing | Register at opendart.fss.or.kr |
| n8n MCP | ⚠️ Key added, not confirmed | Restart VS Code |

---

## 5. Learning Gaps

Based on current priorities (AI consulting roles) vs. current skills:

| Gap | Why It Matters | Effort |
|---|---|---|
| LangChain | Referenced in consulting interviews; haven't built with it | Low — 1 day |
| GraphRAG / Hybrid RAG | Differentiator vs. basic RAG; BCG/Deloitte use this | Medium — 2 days |
| Evaluation / LLM testing (RAGAS, deepeval) | Shows production mindset | Medium |
| Agent memory patterns | Long-running agents need memory; only have session-level now | Medium |
| Tool calling / function calling depth | Claude + tool use in production | Low |

**Highest leverage:** GraphRAG. Adding it to FinAgent v2 as a retrieval layer + explaining the architecture in interviews would immediately elevate Keonhee above other AI-capable student candidates.

---

## 6. Autonomous Operation — What's Possible vs. What's Not

### What works right now (while VS Code is open)
- Daily AI reports fire at 8:03am
- Weekly health check fires Monday 9am
- All hook events fire automatically on tool use
- `/loop` skill can run any command on a continuous interval

### What requires human presence
- VS Code must be open for crons to fire
- Research requires Perplexity API call (runs fine, just needs the session)
- Any web browsing, email, or external action

### True autonomy path (not yet built)
1. **Windows Task Scheduler** — boot VS Code at 8am daily, open this project
2. **Startup hook** — on session open, automatically re-run `/schedule` to restore crons
3. **Notion as async output** — all reports auto-logged to Notion so Keonhee reads results on phone without opening VS Code

This 3-step setup would make the daily AI report truly autonomous. Estimated build time: 2-3 hours.

---

## 7. Top Recommendations (Ranked by Impact)

1. **Push FinAgent + DART App to public GitHub + run GEO on READMEs** — Highest portfolio leverage. Currently invisible to search. Takes 2 hours.

2. **Build `job-monitor` skill** — Cron that checks Deloitte/Accenture/BCG/McKinsey Korea careers pages for AI roles. Fires the `apply` workflow automatically when a new posting appears. Never miss an opening.

3. **Post LinkedIn About** — It's already drafted. Paste it in. 5 minutes of work with months of compound exposure.

4. **Wire Notion as report output** — Daily AI reports should go to Notion automatically. Gives async access from phone without opening VS Code.

5. **Windows Task Scheduler for true autonomy** — Start VS Code at 8am, trigger session startup hook to re-schedule crons. Makes the daily report truly autonomous.

6. **Build GraphRAG layer for FinAgent v2** — Immediately differentiates from basic RAG. Direct answer to Kearney's "tech stack fit" rejection reason.

7. **DART API key** — 30-minute registration. Unlocks a complete custom MCP server for Korean financial data — a genuinely rare portfolio piece at student level.

---

## Summary

The system is well-architected but underutilized. Skills and agents are built but not regularly deployed. The biggest gaps are portfolio visibility (nothing on GitHub except RAG demo), missing autonomy glue (crons die when VS Code closes), and one easily-fixable blocker (DART API key). The daily AI report cron and weekly health check are now active — they'll surface actionable intelligence automatically each morning.
