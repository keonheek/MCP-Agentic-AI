# /generate-tasks — Automatic Task Generator

Runs every 12 hours via cron. Scans projects and research for automatable tasks and feeds them into `tasks/todo.md` so the loop never starves.

## Steps

### Step 1 — Read current state
Read in parallel:
- `context/current-priorities.md`
- `tasks/todo.md` (to avoid duplicates)

### Step 2 — Scan projects for unchecked items
Glob `projects/*/CLAUDE.md` and read each file.
- Extract any unchecked `- [ ]` items
- Skip items tagged with: "human", "manual", "reboot", "UI step", "send message", "paste", "DM", "KakaoTalk", "Instagram", "phone"
- These are human-action items — do not add them

### Step 3 — Scan research reports for action items
Glob `research/*.md`, read the 3 most recent files.
- Extract any bullet points marked as "action", "next step", or "implement"
- Skip anything requiring human judgment, external accounts, or UI interaction

### Step 4 — Deduplicate
Compare candidates against existing `tasks/todo.md` entries (fuzzy match on key words).
Remove any item already in todo.md (checked or unchecked).

### Step 5 — Append to todo.md
If new automatable tasks found, append under a section:

```
## Auto-Generated Queue — [YYYY-MM-DD HH:MM]

- [ ] [Task description] — source: [file path]
- [ ] [Task description] — source: [file path]
```

If no new tasks found, do nothing (no file write, no output).

### Step 6 — Silent finish
Do not output anything to chat unless running manually. This is a background cron — silence is correct behavior.

## Rules
- Max 5 new tasks per run — don't flood the queue
- Each task must be self-contained and executable by Claude alone
- Never add tasks that require browser auth, UI interaction, or sending messages to real people
- Source path must be included for every task (traceability)
