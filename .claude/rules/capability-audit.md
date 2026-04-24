# Capability Audit

_Review date: 2026-05-22_

## Purpose

Capabilities flagged here have not been confirmed as actively used. At the review date, apply this rule to each: use it or improve it or archive it. Do not let them accumulate silently.

## Flagged for review (2026-05-22)

### Commands
- `/execute-next` — may overlap with `/loop`. Clarify the distinction: is `/execute-next` single-shot while `/loop` is continuous?
- `/emerge` — overlaps with Step 4 of `skills/life-review`. Check if it adds value standalone.
- `/framework-check` — partially superseded by context7 MCP. Check if it still serves a distinct use case.

### Skills
- `skills/research-pipeline/` — supposed to auto-ingest research into Obsidian after research completes. Verify it actually fires as part of the research flow or if it's a ghost.
- `skills/cli-anything/` — meta-skill. Check if ever invoked.
- `skills/database-builder/` — meta-skill. Check if ever invoked.
- `skills/github-skill-finder/` — meta-skill. Check if ever invoked.
- `skills/skill-creator/` — meta-skill. Check if ever invoked.

## Archived (reference)

| Item | Archived | Reason |
|---|---|---|
| `agents/research-agent.md` | 2026-04-22 | Superseded by `skills/research` + WebSearch/Gemini/Naver MCP stack |
| `agents/notion-agent.md` | 2026-04-22 | Converted to `skills/notion/`. Notion MCP works directly in main session. |
| `agents/improvement-scout.md` | 2026-04-18 | Cost-inefficient: 3x Perplexity calls per run at 6h intervals |