# /schedule

Set up or review recurring automated tasks for Keonhee's second brain.

## What to do

1. List all currently active cron jobs using CronList
2. Ask which schedule to set up if not specified, or set up all defaults if user says "all":

### Default Schedules

**Daily AI Report** (`0 8 * * *` — 8am daily)
Prompt: Run the daily AI intelligence report. Read `.claude/commands/daily-ai-report-prompt.md` for the full instructions and execute them.

**Weekly System Health** (`0 9 * * 1` — Monday 9am)
Prompt: Run the weekly system health check. Read `.claude/commands/weekly-health-prompt.md` and execute.

**Priority Review** (`0 10 * * 5` — Friday 10am)
Prompt: Read `context/current-priorities.md` and `tasks/todo.md`. For each priority, assess whether it moved this week. Flag anything stalled for 7+ days. Output a concise status update and suggest the one action that would unblock the most stalled item.

3. After creating each job, confirm job ID and schedule to user.
4. Warn user: cron jobs only fire while Claude Code (VS Code) is open and idle. They auto-expire after 3 days — user must run `/schedule` again to renew.

## Notes
- Use CronCreate for each job
- Store job IDs in memory so they can be deleted with CronDelete if needed
- Do not duplicate jobs — check CronList first
