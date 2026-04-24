# /schedule

Set up or review recurring automated tasks for Keonhee's second brain.

## What to do

1. List all currently active cron jobs using CronList
2. Ask which schedule to set up if not specified, or set up all defaults if user says "all":

### Default Schedules

**Autonomous Loop** (`*/3 * * * *` — every 3 minutes)
Prompt: Read `.claude/commands/loop.md` and execute it. Check `tasks/discord_inbox.json` for pending tasks first, then pick the next task from `tasks/todo.md`. Follow all rules in the command file.

**Daily AI Report** (`0 8 * * *` — 8am daily)
Prompt: Run the daily AI intelligence report. Read `.claude/commands/daily-ai-report-prompt.md` for the full instructions and execute them.

**Weekly System Health** (`0 9 * * 1` — Monday 9am)
Prompt: Run the weekly system health check. Read `.claude/commands/weekly-health-prompt.md` and execute.

**Priority Review** (`0 10 * * 5` — Friday 10am)
Prompt: Read `context/current-priorities.md` and `tasks/todo.md`. For each priority, assess whether it moved this week. Flag anything stalled for 7+ days. Output a concise status update and suggest the one action that would unblock the most stalled item.

**Priority Sync** (`17 */3 * * *` — every 3 hours at :17)
Prompt: Read `context/current-priorities.md` and Obsidian `Context/Current Priorities.md`. Compare timestamps. Update the stale copy. Append sync confirmation to today's Obsidian daily note (`Daily Notes/YYYY-MM-DD.md`).

**Improvement Scout** (`43 */6 * * *` — every 6 hours at :43)
Prompt: Run the improvement scout agent. Read `.claude/agents/improvement-scout.md` for full instructions. Execute the 5-step process: read state, scan projects, research one improvement via Perplexity, save report to `research/YYYY-MM-DD-improvement-scout.md`, append summary to today's Obsidian daily note.

**Instagram Daily Feed** (`0 9 * * *` — 9am daily)
Prompt: Run the Instagram daily feed pipeline. Read `.claude/commands/instagram-daily-feed.md` and execute all 7 steps. Requires Playwright MCP to be connected.

3. After creating each job, confirm job ID and schedule to user.
4. Warn user: cron jobs only fire while Claude Code (VS Code) is open and idle. They auto-expire after 7 days — user must run `/schedule` again to renew. The Autonomous Loop job expires fastest — check it weekly.

## Notes
- Use CronCreate for each job
- Store job IDs in memory so they can be deleted with CronDelete if needed
- Do not duplicate jobs — check CronList first
