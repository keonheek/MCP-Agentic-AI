# Claude Code Power User Guide

How to maximize Claude Code usage across every dimension: volume, breadth, depth, structure.

---

## 1. /loop — Keeping the Autonomous Loop Fed

### What You Have

Your `/loop` command (`.claude/commands/loop.md`) is a 5-step autonomous executor:
1. Checks `tasks/loop_control.json` (running/paused/stopped)
2. Checks `tasks/discord_inbox.json` for pending tasks
3. Falls back to `tasks/todo.md` — picks ONE unchecked task from "This Week"
4. Executes it
5. Reports to 6 places (todo.md, status.json, Obsidian, Notion, decisions/log.md, discord_outbox)

The cron runs it every 3 minutes. The orchestrator (`tools/orchestrator.py`) can also run it.

**The problem:** The loop starves. Once automatable tasks are done, it idles. `agents/status.json` confirms: "Claude Loop" last ran March 24 with "Backlog fully audited — all auto-executable tasks done."

### How to Fix It

**A. Build a Task Generator Cron**

Create `.claude/commands/generate-tasks.md` — a command that runs every 12 hours and populates `tasks/todo.md` automatically:

```
What it does:
1. Read context/current-priorities.md
2. Scan projects/*/CLAUDE.md for unchecked items
3. Scan research/ reports for unchecked action items
4. Filter: skip anything tagged "human", "manual", "reboot", "UI step", "send message"
5. Deduplicate against existing todo.md entries
6. Append new items under "## Auto-Generated Queue" in tasks/todo.md
7. Mark each with source file path for traceability
```

Wire as cron: `0 */12 * * *` (every 12 hours).

**B. Widen Loop Scope**

Edit `.claude/commands/loop.md` Step 3b, rule 1. Change:
- "Must be in 'This Week' section" → "Must be in 'This Week' or 'BUILDABLE BY CLAUDE' sections"

This immediately unlocks tasks the loop was skipping.

**C. Chain Loops via Output Files**

After completing a task, have the loop write:
```json
// tasks/loop_output.json
{
  "last_completed": "Run GEO audit on target-007.com",
  "artifacts": ["projects/geo-agency/output/audit-target-007.pdf"],
  "suggested_next": "Generate case study from audit-target-007.pdf"
}
```

The next loop invocation reads this file and uses artifacts as input. This turns independent task execution into a pipeline.

Example chain for GEO:
- Iteration 1: Scrape 20 target websites → writes `crm/leads.json`
- Iteration 2: Run GEO audit on next unaudited lead → writes audit PDF
- Iteration 3: Generate case study from audit → writes case study PDF

**D. Discord as Task Injection**

Start: `pythonw tools/discord-bot/bot.py`

From your phone throughout the day, send tasks:
- "research Korean GEO pricing on Soomgo"
- "draft 3 KakaoTalk outreach messages for 세무사"
- "update the GEO README with latest audit count"

Each becomes a `discord_inbox.json` entry the loop picks up within 10 minutes.

---

## 2. Tool Breadth — Using More Tool Types Per Session

### Underused Tools

| Tool | Status | Why It's Underused |
|------|--------|--------------------|
| Gmail MCP | Available | Never wired into any command or cron |
| Google Calendar MCP | Available | Never wired into any command or cron |
| youtube-transcript | Manual only | No automated pipeline reads YouTube |
| context7 | Enabled | Never referenced in commands — use for library docs |
| DART MCP | Disabled | Unique differentiator sitting dormant |
| data-analyst skill | Built | Never in any cron or automated flow |
| financial-analyst skill | Built | Never in any cron or automated flow |

### Tool Combo Patterns

**Combo 1: "Morning Intelligence Pipeline" (5 tools)**

Enhance your `/today` command (`.claude/commands/today.md`) to:
1. Read `context/current-priorities.md` + `tasks/todo.md` (Read tool)
2. Check Google Calendar for today's events (`gcal_list_events`) — surface meetings, deadlines, 제자훈련
3. Check Gmail for unread threads (`search_threads` with query `"subject:GEO OR subject:SDC OR from:soomgo OR from:kmong is:unread"`)
4. Read Obsidian daily note (`get_daily_note`)
5. Output a combined briefing

**Combo 2: "Research-to-Knowledge Pipeline" (4 tools)**

When any research completes:
1. Research skill generates report to `research/` (Perplexity API)
2. Obsidian skill ingests it (`/wiki-ingest` on the report file)
3. If YouTube URLs found, youtube-transcript extracts them, adds key findings to wiki
4. Notion agent updates the relevant project page with a summary

Create `.claude/commands/research-pipeline.md` to chain these steps.

**Combo 3: "Client Delivery Pipeline" (6 tools)**

When a GEO audit completes:
1. `before_after.py` generates evidence (Perplexity + Anthropic APIs)
2. `geo_report_pdf.py` generates the PDF
3. QA agent audits the PDF (4-dimension MECE loop)
4. `geo_deliverables.py` assembles the implementation kit
5. Gmail MCP creates a draft email with the PDF
6. Obsidian appends delivery to today's daily note
7. Notion updates the CRM lead status

**Combo 4: "Context7 + Coding Agent"**

When a framework update is detected (from daily AI report):
1. context7 `resolve-library-id` + `query-docs` fetches current documentation
2. Coding agent reviews your existing code for breaking changes
3. Research skill checks for migration guides
4. Output a migration plan

### Enabling Disabled Tools

**DART MCP:** Move the `dart` entry from `_disabled` to the main `mcpServers` object in `.mcp.json`.

**Gmail + Calendar:** Already available as hosted MCP tools (`mcp__claude_ai_Gmail__*`, `mcp__claude_ai_Google_Calendar__*`). No setup needed — just call them.

---

## 3. Subagent Spawning Patterns

### When to Use Parallel vs Sequential

**Parallel** (no data dependency between tasks):
```
Agent(research-agent: "Research 세무법인 엑스퍼트")
Agent(writing-agent: "Draft pitch using GEO offer stack from current-priorities.md")
Agent(coding-agent: "Run geo_report_pdf.py on target URL")
```
All three launch simultaneously in one message. Results come back independently.

**Sequential** (output of one feeds the next):
```
Step 1: Agent(research-agent: "Research competitor pricing") → returns research/pricing.md
Step 2: [Main session reads research/pricing.md, extracts key findings]
Step 3: Agent(writing-agent: "Read research/pricing.md and draft a pricing comparison")
```

### Rules of Thumb

| Scenario | Pattern |
|----------|---------|
| Different projects, no shared files | Parallel |
| Research + writing on same topic | Sequential |
| Multiple GEO audits on different sites | Parallel |
| Code change + QA review of that change | Sequential |
| Notion update + Obsidian update | Parallel |
| Generate content + autoresearch score it | Sequential |

### isolation: "worktree" for Agents

Add `isolation: "worktree"` to agent frontmatter when the agent modifies code files. This gives it its own git worktree — no conflicts with other agents or your main session.

**Use for:**
- coding-agent (modifies project code)
- Any agent running Mode 2 autoresearch (git commit/reset cycle)

**Don't use for:**
- research-agent (writes to separate `research/` folder)
- notion-agent (writes to Notion, not git)
- writing-agent (writes to `drafts/`)

### Agent-to-Agent Handoff

Sub-agents cannot spawn other sub-agents. The main session orchestrates:

```
1. Main session → Agent A (writes output to known path)
2. Agent A returns: "Output saved to research/2026-04-12-analysis.md"
3. Main session reads the output, extracts what Agent B needs
4. Main session → Agent B: "Read research/2026-04-12-analysis.md and use it to draft..."
```

The director-agent already does this decomposition. Phrase tasks to make independence explicit:
> "Goal: Prepare for client meeting. Subtask 1 (research-agent, parallel): Research target website. Subtask 2 (writing-agent, parallel): Draft pitch from current-priorities.md. Subtask 3 (coding-agent, parallel): Run audit script on target URL."

---

## 4. Scheduled Tasks (Crons)

### Current Crons (renew weekly — they expire after 7 days)

| # | Schedule | What | Purpose |
|---|----------|------|---------|
| 1 | `*/10 * * * *` | `/loop` | Autonomous task executor (changed from */3) |
| 2 | `0 8 * * *` | Daily AI report | Morning intelligence |
| 3 | `0 9 * * 1` | Weekly health check | Monday system scan |
| 4 | `0 10 * * 5` | Priority review | Friday priority sync |
| 5 | `17 */3 * * *` | Priority sync | Obsidian <> priorities.md |

### New Crons to Add

| # | Schedule | What | Purpose |
|---|----------|------|---------|
| 6 | `0 */12 * * *` | Task Generator | Scan projects + research for automatable tasks, feed todo.md |
| 7 | `30 20 * * 0` | Obsidian Wiki Lint | Clean orphan pages, fix broken links, update index |
| 8 | `0 */4 * * *` | GEO Score Monitor | Check if delivered audits improved target visibility |
| 9 | `0 7 * * *` | Calendar Planner | Check today's events, flag 제자훈련 deadlines, write to Obsidian |

### How Crons Work

- **Only fire when VS Code is open AND idle** (not processing a user message)
- **Auto-expire after 7 days** — run `/schedule` every Monday to renew
- **Do not overlap** — if the loop cron fires while the previous invocation is still running, it queues

### Context Clogging Mitigation

1. **Pause during focused work.** Before a deep session, set `tasks/loop_control.json` to `{"mode": "paused"}`. Set back to `"running"` when done.
2. **Don't run cron loop AND orchestrator simultaneously.** Pick one. Crons are simpler; the orchestrator (`tools/orchestrator.py`) gives more control (max-runs, timeout).
3. **Changed loop from `*/3` to `*/10`.** 3 minutes was too aggressive — tasks take 1-5 minutes, so the loop could overlap with itself.

### Maximizing Cron Coverage

Your VS Code is open ~8-16 hours/day = 50-67% fire rate. To maximize:
- Keep VS Code open when laptop is on, even if not coding
- Stagger cron times (already done: :17, :30, :00, :43 offsets)
- For critical flows, use the orchestrator instead: `pythonw tools/orchestrator.py --name "Loop" --command "/loop" --interval 600 --max-runs 50`

---

## 5. Autoresearch + QA Loops

### Mode 1: Content Loop (text quality)

```
generate(input) → score with Haiku (cheap) → if avg >= threshold: done → else: improve → repeat
```

Config: `MAX_ITERATIONS=8`, `SCORE_THRESHOLD=7.5`, Haiku scores, Sonnet generates. Cost: ~$0.03/run.

**New targets to apply Mode 1 on:**

| Artifact | Dimensions | Threshold | Why |
|----------|-----------|-----------|-----|
| GEO outreach messages | personalization, urgency, specificity, tone | 8.0 | Client-facing, high stakes |
| Daily AI reports | relevance, actionability, specificity | 7.0 | Internal, lower bar |
| LinkedIn/blog posts | citability, specificity, authority, keyword_density | 8.0 | Public, GEO-optimized |
| KakaoTalk templates | brevity, hook_strength, personalization | 8.5 | 150-char preview limit |

### Mode 2: Karpathy Loop (measurable metrics)

```
hypothesis → edit ONE file → run eval → git commit if better, reset if worse → repeat forever
```

Requires: one scalar metric, automated eval (<5 min), one editable file.

**Experiments to set up:**

**Experiment A: GEO Outreach Hook Optimization**
- `program.md`: "Maximize response rate. Metric: Haiku-scored quality (urgency, personalization, believability, CTA clarity). Higher is better."
- Editable file: `projects/geo-agency/outreach/hook_template.md`
- Eval script: Python file that scores the hook using Haiku, outputs single number
- Run 20-50 iterations overnight → data-optimized outreach message

**Experiment B: SME Problem Structurer Prompt**
- `program.md`: "Maximize diagnostic accuracy on 5 test cases. Metric: Haiku-scored quality."
- Editable file: problem structurer prompt file
- Eval: Run diagnostic on 5 fixed inputs, score each, average

### Chaining Autoresearch → QA

For business deliverables, chain both systems:

```
1. Generate output (script or coding-agent)
2. Autoresearch Mode 1 on text content (improve quality, cheap)
3. Regenerate output with improved content
4. QA agent on regenerated output (check structure, layout, completeness, polish)
5. If QA fails → QA agent fixes generator code → loops up to 5 iterations
```

Create `.claude/commands/full-qa-pipeline.md` to orchestrate this sequence.

---

## 6. Worktrees for Parallel Projects

### Concept

Each worktree = separate folder = separate VS Code window = separate Claude session = zero context contamination.

### Current State

```
MCP_Agentic AI/                    ← master (admin, SDC, system)
MCP_Agentic_AI_geo-agency/         ← worktree/geo-agency (GEO work)
.claude/worktrees/strange-goldwasser/  ← Claude-managed (auto)
```

### Create Missing Worktrees

```bash
cd "C:/Users/keonh/Dev/MCP_Agentic_AI"
git worktree add "../MCP_Agentic_AI_sme" -b worktree/sme-diagnostic
git worktree add "../MCP_Agentic_AI_erp" -b worktree/erp-demo
```

Result: 4 parallel workspaces.

### Open Each in Separate VS Code Window

```bash
code "c:/Users/keonh/OneDrive/바탕 화면/MCP_Agentic_AI_geo-agency"
code "c:/Users/keonh/OneDrive/바탕 화면/MCP_Agentic_AI_sme"
code "c:/Users/keonh/OneDrive/바탕 화면/MCP_Agentic_AI_erp"
```

Each window has its own Claude Code instance. You can work on GEO in one, SME in another, ERP in a third — simultaneously.

### Project-Specific CLAUDE.md

Each worktree should have a lean root CLAUDE.md that only loads that project's context:

```markdown
# GEO Agency Workspace
@projects/geo-agency/CLAUDE.md
@context/current-priorities.md
```

This prevents context bloat from loading all 5 context files + all docs references.

### Visualize Worktrees

**Option A: Quick command**

Create `.claude/commands/worktrees.md`:
```
Run `git worktree list` and for each worktree show:
- Path and branch
- Last commit date (git log -1 --format="%ar" for each)
- Whether the worktree folder exists
```

**Option B: Extend the dashboard**

Add a worktree section to `tools/agent-dashboard/app.py` that runs `git worktree list` and displays branch + last commit time alongside the existing agent status cards.

### Merging Back

When a feature in a worktree is complete:
```bash
cd "C:/Users/keonh/Dev/MCP_Agentic_AI"
git merge worktree/geo-agency
```

### Key Rules

- Do NOT `cd` between worktrees in the same terminal — open separate windows
- `EnterWorktree` / `ExitWorktree` tools handle Claude-managed worktrees; for manual worktrees, just open the folder
- Renew GitHub PAT before any push operations

---

## 7. Self-Amplifying Skills & Agents

Skills and agents that generate MORE Claude Code activity by creating work that feeds back into the system.

### New Skill: "daily-content-machine"

**Purpose:** Generate one piece of public content per day from existing project data.

**What it does:**
1. Read `context/current-priorities.md` for active business focus
2. Pick content type (rotate: Naver Blog, LinkedIn, KakaoTalk template, GitHub README, case study)
3. Read relevant project files for source material
4. Generate content using autoresearch Mode 1 (score/improve until 8.0+)
5. Save draft to `drafts/YYYY-MM-DD-[type]-[slug].md`
6. Add "Review and publish [type]" to `tasks/todo.md` (human-action item)
7. Append to Obsidian daily note

Wire as cron: `0 9 * * *` (9am, after 8am AI report informs the topic).

**Why this multiplies usage:** Each invocation triggers autoresearch (8+ iterations), writes to 3 systems (drafts/, todo.md, Obsidian), and creates a human review task that may trigger further edits.

### New Skill: "project-health-scanner"

**Purpose:** Detect stale projects and auto-generate revival tasks.

**What it does:**
1. Scan `projects/` for last-modified timestamps
2. For any project with no changes in 7+ days, generate a "revive plan": 3 concrete automatable tasks
3. Quick Perplexity search for current best practices per project
4. Write plans to `projects/[name]/revive-plan-YYYY-MM-DD.md`
5. Add automatable tasks to `tasks/todo.md`
6. If project has a QA-able output in `tools/qa-registry.json`, trigger qa-agent on most recent output

**Why this multiplies usage:** Stale projects automatically generate work → loop picks it up → more Claude activity. Self-healing system.

### New Agent: "codebase-gardener" (Haiku)

**Purpose:** Low-priority cleanup that runs when nothing else is available.

Add to `.claude/agents/codebase-gardener.md`:
- Model: haiku (cheap, runs frequently)
- Each invocation picks ONE task:
  - Find `TODO` comments in code → convert to `tasks/todo.md` entries
  - Check for hardcoded paths that should be in `.env`
  - Find duplicate code across projects
  - Update stale README files (compare claims vs actual structure)
- Output: short report + the fix applied (if safe) or a todo.md entry (if needs review)

Wire via loop: add "Run codebase gardener" as a recurring low-priority task.

### New Skill: "session-maximizer"

**Purpose:** At session start, surface the most relevant tools for the current task.

**What it does:**
1. Read the user's first message
2. Cross-reference against full tool inventory (skills, agents, commands, MCP tools)
3. Suggest: "For this task, use [skill X] for research, [agent Y] for execution, [MCP tool Z] for data, [command W] to verify."

Combats the "dormant capabilities" problem by actively surfacing relevant tools every session.

---

## Quick Wins (5 min each)

1. **Renew crons.** Run `/schedule` to re-create all crons. They expired 7+ days ago.
2. **Change loop interval.** `*/3` → `*/10` in schedule command.
3. **Start Discord bot.** `pythonw tools/discord-bot/bot.py` — inject tasks from phone.
4. **Test Gmail MCP.** "Search my Gmail for threads about GEO from last 7 days."
5. **Test Calendar MCP.** "List my Google Calendar events for this week."
6. **Update loop_control.json.** Verify mode is `"running"`, update timestamp to today.

## Power Plays (30+ min, 10x multiplier)

| # | Play | Time | Impact |
|---|------|------|--------|
| 1 | Build Task Generator Cron | 45 min | Loop never starves again |
| 2 | Wire Research-to-Knowledge Pipeline | 60 min | Reports auto-ingested to Obsidian + Notion |
| 3 | Mode 2 on GEO outreach hook | 30 min | Data-optimized outreach message |
| 4 | 3 Production Worktrees + Dashboard | 45 min | Parallel Claude sessions |
| 5 | daily-content-machine skill + cron | 60 min | Auto-generated daily content |
| 6 | Enable DART MCP + financial lead scoring | 30 min | Data-driven prospect identification |

---

## Context Clogging & Hallucination Mitigation

| Risk | Mitigation |
|------|-----------|
| Long sessions degrade quality | `/clear` after 20+ messages. One session = one task. |
| Loop competes with manual work | Pause loop_control.json during focused sessions |
| Large outputs bloat context | Route through subagents — main session stays lean |
| Multiple tasks per loop invocation | Never. 1-task-per-invocation rule is correct. |
| Cron overlap | Changed from */3 to */10. Don't run cron + orchestrator simultaneously. |
| Stale memories cause wrong recommendations | Verify file paths and function names from memory before acting on them |
| Model cost spirals | Opus for planning only. Sonnet for execution. Haiku for scoring/CRUD/research. |
| GitHub operations fail silently | Renew PAT (expired Apr 8) before any git push or worktree ops |
