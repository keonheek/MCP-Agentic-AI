Read these files: `context/current-priorities.md`, `decisions/log.md` (last 5 entries), `tasks/todo.md`, and scan for any files modified today.

Then do ALL of the following:

**1. Write session summary to `templates/session-summary.md`:**

# Session Summary
**Date:** [today's date]
**Session focus:** [1-line description of what the session covered]

## What Got Built
| Item | Type | Status |
|------|------|--------|
[one row per completed task]

## Decisions Made
| Decision | Reasoning |
|----------|-----------|
[one row per meaningful decision]

## Human-in-Loop Queue
[bullet list of things blocked on human action — most urgent first]

## Next Session — Top 3
1. [highest priority incomplete task]
2. [second]
3. [third]

## System State Snapshot
[skills count, agents, MCP servers, key tools]

---

**2. Append new decisions to `decisions/log.md`:**
For each decision made this session that isn't already logged, append:
`[YYYY-MM-DD] DECISION: ... | REASONING: ... | CONTEXT: ...`

**3. Update memory if needed:**
If any corrections, new patterns, or stable preferences emerged this session, update `C:\Users\keonh\.claude\projects\c--Users-keonh-OneDrive-------MCP-Agentic-AI\memory\MEMORY.md`.

**4. Update `tasks/todo.md`:**
Mark completed items. Add any new blockers discovered. Remove stale items.

Keep everything scannable — bullets over paragraphs. No filler.
