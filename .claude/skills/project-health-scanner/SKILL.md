---
name: project-health-scanner
description: Weekly scan for stale projects. Detects projects with no changes in 7+ days, generates 3 automatable revival tasks per stale project, and adds them to tasks/todo.md for the loop to pick up.
---

# Skill: Project Health Scanner

Detects stale projects and auto-generates revival tasks to feed the loop.

## Trigger phrases
- "scan project health"
- "what's stale"
- "project health check"
- Runs weekly via cron (Sunday alongside wiki-lint)

---

## Steps

### Step 1 — Scan projects/ for last-modified timestamps
For each directory in `projects/`:
- Check the most recently modified file (use git log or file timestamps)
- Flag any project with no changes in the last 7 days as "stale"

Also check external projects:
- FinAgent: `c:/Users/keonh/OneDrive/바탕 화면/FinAgent/`
- Samsung Forecast app

### Step 2 — Generate revival tasks per stale project
For each stale project, generate exactly 3 automatable tasks based on its current state:
- Read the project's `CLAUDE.md` or `README.md` for context
- Pick tasks that are self-contained, executable by Claude, and move the project forward
- Skip tasks requiring human UI action, external logins, or sending messages

### Step 3 — Check for QA-able outputs
If a project has a recent output file (PDF, HTML, PPTX) in its output directory:
- Add a task: "Run QA audit on [project] latest output — [output file path]"

### Step 4 — Append to todo.md
Add new tasks under:
```
## Project Health Revival — [YYYY-MM-DD]

### [Project Name] (stale since [date])
- [ ] [Task 1] — source: projects/[name]/
- [ ] [Task 2] — source: projects/[name]/
- [ ] [Task 3] — source: projects/[name]/
```

If no projects are stale, output: "All projects active — no revival tasks needed."

### Step 5 — Report
Output:
```
## Project Health Scan — [DATE]

Stale (7+ days): [project list]
Active: [project list]
Revival tasks added: [N]
```

---

## Rules
- Never modify project code directly — only generate tasks
- Max 3 revival tasks per project per scan (don't flood todo.md)
- A project is only "stale" if the main code files haven't changed — README-only updates don't count
- Skip projects marked as "PAUSED" or "DEFERRED" in current-priorities.md
