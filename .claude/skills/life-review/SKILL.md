---
name: life-review
description: Holistic life + business progress scanner. Runs a sequential 5-step scan (goals vs. reality, weekly health, decision log, Obsidian, emerge), generates a structured report, then enters an auto-fix loop for anything Claude can resolve autonomously. Trigger: /life-review
---

# Life Review Skill

You are running a holistic life + business review for Keonhee. This skill has two phases: sequential scan, then auto-fix loop.

---

## Phase 1: Sequential Scan

Run each step in order. Each step builds context for the next.

### Step 1: Goals vs. Reality
Read these files in parallel:
- `context/goals.md`
- `context/current-priorities.md`
- `tasks/todo.md`
- `decisions/log.md` (last 20 lines)

For each Q2 2026 goal in goals.md, find evidence of progress (or lack of it) in current-priorities and todo.md. Be specific: cite actual checkboxes, dates, status markers.

Output:
```
### Goals vs. Reality
| Goal | Evidence of Progress | Status |
|------|---------------------|--------|
| [goal] | [what todo/priorities show] | On track / Stalled / Not started |
```

### Step 2: Weekly Health Check
Identify:
- Tasks in todo.md unchecked for 7+ days (staleness flag)
- Items marked URGENT or with deadlines in the past
- Infrastructure issues: expired API keys, pending reboots, broken links
- Check MEMORY.md Pending section for overdue items

Output:
```
### Health Flags
- [x] URGENT: [item] — [why urgent]
- [ ] Stale (7+ days): [item]
- [ ] Infrastructure: [item]
```

### Step 3: Decision Log Review
Read `decisions/log.md`.

For each decision in the last 30 days:
- Did it lead to action? (check todo.md and priorities for follow-through)
- Was it reversed or contradicted by a later decision?
- Any decisions with no follow-through → flag as "decision without action"

Output:
```
### Decision Follow-through
- [decision] → [action taken / no action]
```

### Step 4: Obsidian Scan
Search Obsidian daily notes from the past 7 days using `mcp__obsidian__get_recent_notes` or `mcp__obsidian__search_notes`.

Look for:
- Recurring themes or frustrations
- Things mentioned but not in todo.md or priorities
- Energy patterns (what days had momentum, what stalled)

Output:
```
### Obsidian Patterns (past 7 days)
- [pattern or signal]
```

### Step 5: Emerge — Surface Buried Ideas
Search these files for items tagged IDEA, MAYBE, EXPLORE, or deferred 14+ days:
- `tasks/todo.md`
- `decisions/log.md`
- `context/current-priorities.md`

Cluster by theme: business, technical, learning, personal.

Output:
```
### Buried Ideas
- Business: [idea]
- Technical: [idea]
- Learning: [idea]
```

---

## Compile Report

After all 5 steps, write the full review:

```markdown
# Life Review — [DATE]

## Business
[Goals vs. Reality table]
[Health flags relevant to business]
[Any decisions without follow-through]

## Personal
- 학업: [signal from Obsidian or todo]
- 제자훈련: [status — check todo for 기도, 성경읽기, 과제 checkboxes]
- 과외: [active commitment — any scheduling signals]
- Other: [anything from Obsidian patterns]

## Keep / Start / Stop
- KEEP: [what's working — evidence-based]
- START: [what's missing that would have highest impact]
- STOP: [what's wasting time or creating noise]

## Buried Ideas Worth Acting On
[top 2-3 from emerge step]

## This Week's #1 Priority
[One sentence — the single highest-leverage action]

---

## Phase 2: Auto-Fix Log
[filled in during Phase 2]
```

---

## Phase 2: Auto-Fix Loop

After writing the report, enter a fix loop. For each fixable issue found in Phase 1:

**What Claude can fix autonomously:**
- Update stale dates in `context/current-priorities.md` (e.g., "Last updated: 2026-03-XX" → today's date)
- Mark clearly completed items in `tasks/todo.md` (only if strong evidence from decisions log or priorities)
- Remove strikethrough completed items from pending lists
- Fix broken file references in any context file
- Archive decisions older than 60 days from `decisions/log.md` to keep it readable
- Add missing items from Obsidian notes to `tasks/todo.md`
- Sync `context/current-priorities.md` status markers (🔴/🟡/🟢) if evidence is clear

**Loop rules:**
- Max 5 iterations
- After each fix, check if more fixable issues remain
- Stop when no more auto-fixable issues, or at iteration 5
- Log every change made in the "Phase 2: Auto-Fix Log" section of the report

**What requires human judgment (flag, don't fix):**
- Should this goal be dropped?
- Is this business still worth pursuing?
- Should this task be deleted vs. deferred?
- Any change to strategy or priorities

For each human-judgment item, add to the report:
```
## Needs Your Input
- [question] — [why it needs you, not Claude]
```

---

## Final Step

Append the completed report to today's Obsidian daily note using `mcp__obsidian__append_to_note`:
```
## Life Review — [TIME]
[summary: top finding + #1 priority + count of auto-fixes applied]
Full report saved to: research/YYYY-MM-DD-life-review.md
```

Save the full report to `research/YYYY-MM-DD-life-review.md`.
