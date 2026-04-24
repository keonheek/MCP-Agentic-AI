# /execute-next — Autonomous Task Executor

Pick the highest-priority uncompleted task from `tasks/todo.md` and execute it autonomously. No human input needed.

## Step 1 — Read state
Read in parallel:
- `tasks/todo.md`
- `context/current-priorities.md`
- `decisions/log.md` (last 3 entries — avoid repeating recent work)

## Step 2 — Pick ONE task
Selection rules (in order):
1. Must be in "This Week" section and unchecked `[ ]`
2. Must NOT require human action (skip anything tagged "human action needed", "reboot", "manual", "UI step", "send message")
3. Must NOT be blocked by something else that's also unchecked
4. Prefer tasks matching current priorities (🔴 first, then 🟡)
5. Prefer tasks that are self-contained (no external dependencies)

If no executable task found → report why and stop. Do not invent tasks.

## Step 3 — Execute
Execute the task using whatever tools are needed:
- Code tasks → write/edit files, push to GitHub
- Research tasks → run the research skill, save to research/
- Notion tasks → use Notion MCP tools
- Obsidian tasks → use obsidian MCP tools
- Documentation tasks → write markdown files

## Step 4 — Mark complete
After execution:
1. Change `[ ]` to `[x]` in `tasks/todo.md` for the completed task
2. Append to `decisions/log.md`: `[DATE] DECISION: Executed task "[task name]" autonomously | REASONING: [what was done] | CONTEXT: /execute-next cron`

## Step 5 — Report
Output exactly:
```
✓ Executed: [task name]
  What I did: [1-2 sentences]
  Files changed: [list]
  Next up: [what the next /execute-next call would pick]
```

## Hard limits
- Never delete files without explicit prior instruction
- Never send messages (KakaoTalk, email, Slack) — these are human actions
- Never push to GitHub without reading the file first
- Never mark a task complete if it errored — log the error instead
- If unsure whether a task requires human judgment → skip it, pick the next one
- Max 1 task per invocation — do not batch
