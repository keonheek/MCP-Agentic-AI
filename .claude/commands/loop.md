# /loop — Autonomous Task Loop

Execute the next task autonomously. Check Discord inbox first, then fall back to `tasks/todo.md`.

## Step 1 — Check loop control

Read `tasks/loop_control.json`.
- If `mode == "paused"` → print `[loop] Paused. Send !resume in Discord to continue.` and stop.
- If `mode == "stopped"` → print `[loop] Stopped. Run /schedule in Claude Code to restart.` and stop.
- If `mode == "running"` → continue.

## Step 2 — Check Discord inbox (priority)

Read `tasks/discord_inbox.json`. Find the first task where `status == "pending"`.

**If a pending inbox task exists:**
1. Mark it `picked_up` in the file (atomic write: write to `.tmp`, then `os.replace()`)
2. Note: `source = "discord"`, `task_id = task.id`, `channel_id = task.channel_id`
3. Treat `task.content` as a natural-language instruction and execute it (Step 3)

**If no pending inbox task → go to Step 3b.**

## Step 3a — Execute Discord task

Apply the same hard limits as `/execute-next`:
- No file deletes without prior explicit instruction
- No sending messages (KakaoTalk, email, Slack) — human actions
- No pushing to GitHub without reading the file first
- No marking complete if errored

**If the task is ambiguous or requires human judgment:**
- Do NOT execute it
- Mark the inbox task `error`
- Write to `tasks/discord_outbox.json`:
  ```json
  {
    "id": "<task_id>",
    "channel_id": <channel_id>,
    "reply": "Skipped: '<task content>' requires human judgment or is unsafe to run autonomously. Run it manually in Claude Code.",
    "completed_at": "<ISO timestamp>",
    "delivered": false
  }
  ```
- Stop.

**If the task is safe and clear → execute it using whatever tools are needed.**

After execution, go to Step 4.

## Step 3b — Execute from todo.md (autonomous mode)

Read in parallel:
- `tasks/todo.md`
- `context/current-priorities.md`
- `decisions/log.md` (last 3 entries)

Pick ONE task using these rules (in order):
1. Must be in "This Week" section and unchecked `[ ]`
2. Must NOT require human action (skip anything tagged "human action needed", "reboot", "manual", "UI step", "send message")
3. Must NOT be blocked by something else that's also unchecked
4. Prefer tasks matching current priorities (🔴 first, then 🟡)
5. Prefer tasks that are self-contained

If no executable task found → print `[loop] No executable task found. All tasks require human action or are blocked.` and stop.

Set `source = "todo"`.

Execute the task. After execution, go to Step 4.

## Step 4 — Reporting sequence (always run after successful execution)

Run all of the following in order:

### 4a. tasks/todo.md
- If task came from todo.md: mark `[ ]` → `[x]`
- If task came from Discord inbox: append to `tasks/todo.md` under `## Discord Tasks` section (create section if missing) and mark it `[x]`

### 4b. agents/status.json
Run: `python agents/update_status.py "Claude Loop" "done" "<task name (max 60 chars)>"`

### 4c. Obsidian daily note
Use `mcp__obsidian__append_to_note` to append to today's daily note (format: `YYYY-MM-DD`):
```
- [HH:MM] <task name> — <1-line summary of what was done>
```
If the note doesn't exist yet, use `mcp__obsidian__get_daily_note` first.

### 4d. Notion project page
Use `mcp__claude_ai_Notion__notion-update-page` to append to the notes field of the relevant project page.
- Match task to project: GEO → geo-agency page, SME → sme-diagnostic-ai page, Lead Intel → lead-intelligence page, etc.
- Do NOT create new top-level pages. Update the existing project page's content block.
- If no clear project match, update the most relevant one.

### 4e. decisions/log.md
Append: `[YYYY-MM-DD] DECISION: Executed task "<task name>" autonomously | REASONING: <1 sentence what was done> | CONTEXT: /loop cron`

### 4f. Discord outbox (only if source == "discord")
Write to `tasks/discord_outbox.json` (atomic write):
```json
{
  "id": "<task_id>",
  "channel_id": <channel_id>,
  "reply": "Done: <task name>. <1-2 sentence summary>. Next up: <what the next /loop call would pick>.",
  "completed_at": "<ISO timestamp>",
  "delivered": false
}
```
Mark the inbox task `done`.

## Step 5 — Output

Print exactly:
```
✓ Executed: <task name>
  Source: discord | todo
  What I did: <1-2 sentences>
  Files changed: <list or "none">
  Next up: <what the next /loop call would pick>
```

## Hard limits
- Never delete files without explicit prior instruction
- Never send messages (KakaoTalk, email, Slack, Discord direct) — these are human actions
- Never push to GitHub without reading the file first
- Never mark a task complete if it errored — log the error to discord_outbox if Discord-triggered, or print clearly if from todo
- If unsure whether a task requires human judgment → skip it
- Max 1 task per invocation — do not batch
- Never modify `tasks/discord_inbox.json` or `tasks/discord_outbox.json` except via atomic write (`.tmp` → `os.replace()`)