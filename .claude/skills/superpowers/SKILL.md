---
name: superpowers
description: Enforced brainstorm-then-plan-then-execute loop. Use whenever a task touches 3+ files or needs architectural decisions. Produces persistent PLAN.md + progress.md + verification.md. Blocks skipping phases — brainstorm must complete before plan, plan before execute. Use GSD instead for 5+ file projects needing full CONTEXT.md scope lock.
---

# Superpowers

Enforced planning depth for anything touching 3+ files. Phases are gates — you cannot skip forward.

## When to Use

- Task touches 3+ files
- Architectural decision involved
- Replacing plain `/plan` or plan mode

**Use GSD instead when:** 5+ files, multi-phase build, or you need XML task structure + CONTEXT.md scope lock.

---

## Phases (sequential, no skipping)

```
BRAINSTORM  →  PLAN  →  EXECUTE
```

Artifacts live at `.superpowers/{project-slug}/`:
- `PLAN.md` — locked scope after PLAN phase
- `progress.md` — live task tracking
- `verification.md` — done criteria + results

---

## Phase 1: BRAINSTORM

**Goal:** Surface all unknowns before touching code.

Ask these questions before writing anything. All must be answered before proceeding.

**Mandatory questions (always ask):**
1. What is the exact outcome? (Not the feature — the user-visible result)
2. What are the hard constraints? (Files that cannot change, APIs that must stay compatible, deadlines)
3. What does done look like? (How will we verify this works?)

**Domain questions (ask the relevant ones):**
- API / backend: error states, auth, response contract
- UI: empty states, loading states, mobile behavior
- Data pipeline: input format, failure modes, idempotency
- Agent / AI: prompt contract, tool schema, failure fallback

**Rule:** Never assume. If the answer isn't in the conversation, ask. Brainstorm is complete only when all mandatory questions are answered.

Write a brainstorm summary to `.superpowers/{slug}/brainstorm.md`:

```markdown
# Brainstorm: [Task Name]

## Outcome
[Exact user-visible result]

## Constraints
- [Hard constraint 1]

## Done Criteria
- [Measurable criteria]

## Open Questions Resolved
- Q: [question] → A: [answer]

## Deferred (out of scope)
- [Not doing this now]
```

---

## Phase 2: PLAN

**Input:** `brainstorm.md` (must exist)
**Output:** `PLAN.md` (locked scope)

Structure:

```markdown
# Plan: [Task Name]

## Scope (locked)
[What is and isn't included — reference brainstorm decisions]

## Tasks

### Task 1: [Action-oriented name]
**Files:** path/to/file.py, path/to/other.py
**Action:** [Specific what to do and what to avoid, with WHY]
**Verify:** [Command or check that proves this task is done]
**Done:** [Measurable acceptance criteria]

### Task 2: ...
```

Rules:
- 2-4 tasks max. If more are needed, split into phases.
- Every task must have `Verify` and `Done`.
- Scope section is locked after user confirms.

Initialize `progress.md`:

```markdown
# Progress: [Task Name]

| Task | Status | Notes |
|------|--------|-------|
| Task 1 | pending | |
| Task 2 | pending | |
```

Initialize `verification.md`:

```markdown
# Verification: [Task Name]

| Task | Done Criteria | Result |
|------|--------------|--------|
| Task 1 | [criteria] | pending |
```

**Gate:** Show PLAN.md to user. Get explicit confirmation before executing. Do not start Phase 3 without a "yes" or "looks good" or equivalent.

---

## Phase 3: EXECUTE

**Input:** Confirmed `PLAN.md`

Work through tasks in order. After each task:
1. Run the `Verify` command
2. Update `progress.md` status to `done`
3. Record result in `verification.md`

### Deviation Rules

| Rule | Trigger | Action |
|------|---------|--------|
| Bug | Broken behavior or error | Fix → verify → note in progress.md |
| Missing Critical | Missing auth, validation, error handling | Add → verify → note |
| Blocking | Missing dep, wrong type | Fix blocker → note |
| Architectural | New schema, breaking API change | STOP → ask user |

**Architectural stop format:**
```
SCOPE CHANGE NEEDED

Current task: [task name]
Discovery: [what was found]
Proposed change: [modification]
Why: [rationale]

Proceed? yes / different approach / defer
```

After all tasks complete: show `verification.md` summary. Mark session done.

---

## Artifact Location

```
.superpowers/
  {project-slug}/
    brainstorm.md
    PLAN.md
    progress.md
    verification.md
```

Slug = kebab-case task name. E.g., "Add FastAPI auth endpoint" → `add-fastapi-auth-endpoint`.

---

## Anti-Patterns

- Skipping brainstorm ("I already know what to do") — not allowed
- Starting execute before user confirms PLAN.md — not allowed
- Tasks without Verify + Done criteria — not allowed
- More than 4 tasks in one plan — split into phases instead