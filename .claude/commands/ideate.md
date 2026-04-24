# /ideate — Process Architect

When Keonhee describes a real-world event or project state, generate 5 automation blueprints — loops and pipelines that can be built and wired live. Not one-off tasks: recurring processes that keep running.

## Arguments
`$ARGUMENTS` — natural language describing what just happened or what project is in focus. Examples:
- `I just messaged 3 leads on KakaoTalk about GEO audits`
- `SDC OT is done, 10 members assigned to branches`
- `SME Diagnostic AI is ready to test`
- `geo-agency` (project name only — infer state from files)

If no arguments → ask "What's the situation or project you want to ideate on?"

## Step 1 — Parse the situation

Extract from `$ARGUMENTS`:
- **Event**: What just happened? (contacted leads, finished build, deployed app, assigned members, etc.)
- **Project**: Which project does this relate to? Fuzzy-match to a folder in `projects/`:
  - "geo", "GEO", "geo agency" → `projects/geo-agency/`
  - "sme", "SME", "diagnostic" → `projects/sme-diagnostic-ai/`
  - "lead", "lead intel" → `projects/lead-intelligence/`
  - "consulting", "due diligence" → `projects/consulting-emulation/`
  - "SDC", "sdc" → `projects/sdc/`
- **New state**: What is now true that wasn't before? (leads in pipeline, members onboarded, app live, etc.)

If project is ambiguous, ask before continuing.

## Step 2 — Read state (all in parallel)

- `$PROJECT_DIR/CLAUDE.md` (if exists)
- `$PROJECT_DIR/README.md` (if exists)
- `context/current-priorities.md`
- `tasks/todo.md`
- `decisions/log.md` (last 10 entries)
- Glob `$PROJECT_DIR/**/*.py` — note file inventory, do NOT read contents yet
- Memory files at `C:\Users\keonh\.claude\projects\c--Users-keonh-OneDrive-------MCP-Agentic-AI\memory\` — scan for anything related to this project or event type

From this, extract:
- What's already built (files, features, deployed URLs)
- What's blocked (human action needed)
- Current priority level (from current-priorities.md emoji)
- Any loops already running (check decisions/log.md for orchestrator entries)
- Any relevant external context (KakaoTalk leads, SDC members, client contacts, etc.)

## Step 3 — Generate 5 process blueprints

Each blueprint is a **loop or pipeline** — something that runs repeatedly or chains multiple automated steps. Think: "what recurring process does this new state unlock?"

### Blueprint categories — must span at least 3:
- **Lead nurturing loop** — monitor responses, generate follow-ups, flag stale leads
- **Content generation pipeline** — create text, images, templates, landing pages from project data
- **Monitoring/alerting loop** — watch for changes (new leads, errors, competitor moves) and react
- **Outreach automation** — generate personalized messages, build contact lists, prep response templates
- **Data collection loop** — scrape, aggregate, or poll sources on a schedule
- **Quality improvement loop** — autoresearch pattern: generate → score → improve → repeat
- **Cross-sell/upsell pipeline** — detect signals from one project, feed opportunity into another
- **Reporting loop** — periodic summaries, dashboards, metrics digests
- **Client delivery pipeline** — automate deliverable generation (PDFs, decks, audit reports)
- **External integration** — wire KakaoTalk API, n8n workflow, webhook receiver, calendar automation

### Blueprint format:

```
### Loop [N]: [Name]
**Category:** [from list above]
**Trigger:** [what starts this loop — schedule / event / manual kick-off]
**Cycle:** What happens each iteration:
  1. [Step] — [tool/skill used]
  2. [Step] — [tool/skill used]
  3. ...
**Frequency:** [every 3 min / daily 8am / on-demand / event-driven]
**Tools needed:**
  - Claude Code: [skills, subagents, MCP tools, commands]
  - External (if any): [KakaoTalk API, n8n, webhook, Notion automation, etc.]
**What it produces:** [concrete output per cycle — file, draft, report, alert, etc.]
**Wire-up command:** [exact command to make it live — orchestrator, CronCreate, or setup steps]
**Setup effort:** quick (< 30 min, wire now) | medium (1-2 hrs) | heavy (needs external API setup)
```

### Constraints:
- At least 1 blueprint must be **quick setup** — can be wired live in this session with no external dependencies
- At least 1 must involve **an external tool** (n8n, API, webhook, KakaoTalk, Notion automation)
- At least 1 must use the **existing orchestrator/cron system** (`tools/orchestrator.py` or CronCreate)
- Never design loops that send real messages without human approval — draft + queue is fine
- For external tools not yet configured, include setup steps as part of the blueprint
- If a loop would cost money per iteration (API calls, cloud compute), flag the estimated cost

## Step 4 — Categorize by readiness

After the 5 blueprints, output two lists:

```
### Ready to wire NOW
[Blueprints with "quick" setup — list by number + one-line description]

### Needs setup first
[Blueprints with "medium" or "heavy" setup — list by number + what's needed before wiring]
```

## Step 5 — Full output format

```
## Process Ideation — [Project] | [YYYY-MM-DD]

**Event:** [what just happened]
**New state:** [what's now true]
**Project status:** [priority emoji + status from current-priorities.md]
**Loops already running:** [any active orchestrator jobs from decisions/log.md, or "none"]

---

[Loop 1]
[Loop 2]
[Loop 3]
[Loop 4]
[Loop 5]

---

### Ready to wire NOW
[list]

### Needs setup first
[list with what's needed]

---

Pick a number (1-5) to build and wire live, or say "queue [N]" to add it to todo.md instead.
```

## Step 6 — On selection: Build + Wire + Test

When user picks a number (e.g., "3" or "wire 3"):

1. **Build** — Create any scripts, config files, or templates the loop needs:
   - Python polling scripts → `tools/` or `projects/$PROJECT/`
   - Response templates → `projects/$PROJECT/templates/`
   - n8n workflow configs → describe the nodes and connections
   - Prompt templates for recurring Claude calls → `.claude/prompts/`

2. **Wire** — Set up the actual automation:
   - Claude Code native loop → run `python tools/orchestrator.py --name "[name]" --command "[cmd]" --interval [seconds]` in background
   - Cron-based → use CronCreate with appropriate schedule and prompt
   - External tool → create the config/script and tell user the ONE manual step needed (e.g., "paste this webhook URL into n8n node X")

3. **Test** — Run one iteration manually to verify it works. Report what it produced.

4. **Log** — Append to `decisions/log.md`:
   `[DATE] DECISION: Wired loop "[loop name]" for [project] | REASONING: [what it does + why] | CONTEXT: /ideate`

5. **Update todo** — Add any ongoing monitoring or maintenance tasks to `tasks/todo.md` under "This Week".

6. **Report** exactly:
   ```
   ✓ Wired: [loop name]
     What it does: [1-2 sentences]
     Runs: [frequency]
     First run output: [what it produced]
     Files created: [list]
     One manual step (if any): [what user needs to do]
   ```

## Hard limits
- Never send real messages to real people — draft + queue only
- Never delete files without explicit instruction
- Never push to GitHub without reading the file first
- Never mark complete if errored — log the error instead
- Flag any loop that would cost money per iteration before building
- External tool setup requiring paid plans → flag cost and ask before proceeding
- If loop needs an API key not in `.env` → tell user what key to add, don't block
