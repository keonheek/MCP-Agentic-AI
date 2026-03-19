---
name: gsd
description: Spec-driven development with built-in verification for substantial projects. Use when the user wants to plan a project, scope a feature, or build something structured. Workflow: Discuss -> Plan -> Execute -> Verify. Based on glittercowboy's GSD system (MIT license). NOT for quick questions or simple tasks.
---

# GSD (Get Shit Done)

Spec-driven development that turns vague ideas into verified, working implementations.

**Original:** [glittercowboy/get-shit-done](https://github.com/glittercowboy/get-shit-done) — Lex Christopherson (@glittercowboy), MIT License
**Adapted for:** Claude Code (replaces OpenClaw session spawning with Claude Code Task() subagents)

## When to Use

Trigger when user says:
- "Let's plan [project]"
- "I want to build [something]"
- "GSD mode"
- "Spec-driven"
- Any substantial project needing structure

**NOT for:** Quick questions, simple edits, single-file fixes.

## Core Philosophy

> "The complexity is in the system, not in your workflow."

1. **Plans ARE prompts** — executable instructions, not documents to interpret
2. **Verification built-in** — every task has acceptance criteria
3. **Fresh context per task** — subagents prevent context rot
4. **Solo developer + AI** — no enterprise theater

## Workflow

```
1. DISCUSS   Capture decisions before planning
2. PLAN      Research -> create verified task specs
3. EXECUTE   Work through tasks with deviation rules
4. VERIFY    Confirm deliverables actually work
```

---

## Phase 1: DISCUSS

Ask about the goal. Identify gray areas by domain:
- Visual features -> layout, interactions, empty states
- APIs -> response format, error handling
- Content -> structure, tone, depth

Document decisions in `{project}/.gsd/CONTEXT.md`:

```markdown
# Context: [Project/Phase Name]

## Decisions (Locked)
- [User decision 1]

## Agent Discretion (Freedom Areas)
- [Area where agent can choose]

## Deferred (Out of Scope)
- [Not doing this now]
```

Rule: Never assume. Always ask.

---

## Phase 2: PLAN

### Research (optional but recommended)
Spawn a subagent to investigate technical approach, pitfalls, best practices.
Save to: `{project}/.gsd/RESEARCH.md`

### Task XML Structure

Each plan = 2-3 tasks max (context efficiency).

```xml
<task type="auto">
  <name>Task N: Action-oriented name</name>
  <files>src/path/file.py, src/other/file.py</files>
  <action>
    What to do, what to avoid and WHY.
    Be specific. No guessing.
  </action>
  <verify>Command or check to prove completion</verify>
  <done>Measurable acceptance criteria</done>
</task>
```

Task types:
- `type="auto"` — agent executes autonomously
- `type="checkpoint:verify"` — user must verify
- `type="checkpoint:decision"` — user must choose

### Plan Verification Checklist
- [ ] Tasks are specific and actionable
- [ ] Each task has verify + done criteria
- [ ] Scope matches CONTEXT.md decisions
- [ ] No enterprise bloat

Save plans to: `{project}/.gsd/plans/{phase}-{N}-PLAN.md`

---

## Phase 3: EXECUTE

### Deviation Rules (apply automatically, track for summary)

| Rule | Trigger | Action | Permission |
|------|---------|--------|------------|
| Bug | Broken behavior, errors, security | Fix -> verify -> track | Auto |
| Missing Critical | Missing validation, auth, error handling | Add -> verify -> track | Auto |
| Blocking | Prevents completion (missing deps, wrong types) | Fix blocker -> track | Auto |
| Architectural | New schema, breaking API change | STOP -> ask user | Ask |

**Architectural stop format:**
```
ARCHITECTURAL DECISION NEEDED

Current task: [task name]
Discovery: [what prompted this]
Proposed change: [modification]
Why needed: [rationale]
Alternatives: [other approaches]

Proceed? (yes / different approach / defer)
```

### Fresh Context Pattern
For multi-task execution, use Claude Code `Task()` subagents:
- Each subagent gets fresh context window
- Main context stays lean for user interaction
- Prevents quality degradation over long sessions

### After Each Task
1. Verify done criteria met
2. Commit changes (optional, user preference)
3. Record in STATE.md
4. Move to next task

---

## Phase 4: VERIFY

### Automated
- Run verify commands from each task
- Check files exist, tests pass

### User Acceptance
Walk through testable deliverables one at a time. Get yes/no or issue description.
If issues found -> create fix plan and re-execute. Don't debug manually.

---

## File Structure

```
{project}/
+-- .gsd/
    +-- PROJECT.md       # Vision, always loaded
    +-- STATE.md         # Current position, decisions, blockers
    +-- CONTEXT.md       # User decisions from discuss phase
    +-- RESEARCH.md      # Domain research (optional)
    +-- plans/
        +-- 01-01-PLAN.md
        +-- 01-01-SUMMARY.md
```

### STATE.md Template
```markdown
# Project State

## Current Position
Phase: [N]
Plan: [N of M]
Status: [planning | executing | verifying | blocked]

## Decisions Made
- [Decision] -- [rationale]

## Blockers
- [Blocker if any]

## Deviations Applied
- [Rule N] [Description] -- [resolution]
```

---

## Quick Mode

Trigger: "Quick: [task description]"

For small tasks: skip research + discussion, create 1-3 task plan, execute, verify, commit.

---

## Anti-Patterns (Banned)

- Story points, sprint ceremonies, human time estimates
- RACI matrices, stakeholder syncs
- Vague tasks without verify/done criteria
- Filler language ("Let me...", "I'd be happy to...")
