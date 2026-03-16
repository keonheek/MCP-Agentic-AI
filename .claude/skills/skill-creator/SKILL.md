# Skill Creator

Create, test, evaluate, and improve Claude Code skills through an iterative development process.

Source: https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator

Updated 2026-03-11: Added scoring rubric, benchmarking criteria, and Keonhee-specific quality checks.

## When to use

Trigger phrases:
- "create a skill for X"
- "build a skill that does X"
- "make a new skill"
- "skill create"
- "improve the X skill"
- "evaluate the X skill"

---

## Modes

### CREATE — Build a new skill from scratch

1. **Capture intent** — Ask: what should the skill do? When does it trigger? What's the expected output? Are test cases needed?
2. **Check for existing skills** — Scan `.claude/skills/` — don't create a duplicate if a skill already covers the use case
3. **Interview** — Ask about edge cases, input/output format, success criteria, dependencies. Do this before writing.
4. **Write SKILL.md** — Create `.claude/skills/<skill-name>/SKILL.md`. Keep under 500 lines. Include:
   - Name, description (in frontmatter if it needs to appear in skill list)
   - Trigger phrases
   - Step-by-step instructions with the WHY behind each requirement
   - Output format
   - Notes / gotchas
5. **Test** — Run 2-3 realistic prompts against the skill. Compare against a baseline (no skill).
6. **Evaluate** — Grade outputs on correctness and quality. Ask user for feedback.
7. **Finalize** — Save to `.claude/skills/<skill-name>/SKILL.md`.

### EVAL — Test an existing skill

1. Read the skill file.
2. Generate 3-5 test prompts that should trigger it.
3. Run each prompt and capture output.
4. Grade each output using the rubric below.
5. Report: pass rate, common failure patterns, recommendations.

### IMPROVE — Refine a skill based on feedback

1. Read the skill file and any test results.
2. Identify the root cause of failures — don't overfit to specific examples.
3. Rewrite the relevant sections with better instructions.
4. Re-run tests to confirm improvement.
5. Save updated skill.

### BENCHMARK — Compare skill vs baseline

1. Run 5 prompts with the skill active.
2. Run the same 5 prompts without the skill.
3. Score both sets using rubric.
4. Report delta: % improvement, areas of regression if any.

---

## Scoring rubric (use for EVAL and BENCHMARK)

| Criterion | Weight | What to check |
|-----------|--------|---------------|
| Trigger accuracy | 20% | Does it fire on the right phrases? Does it NOT fire on unrelated requests? |
| Output correctness | 30% | Is the output accurate and relevant to Keonhee's context? |
| Format adherence | 20% | Does it follow the specified output format (bullets, tables, etc.)? |
| Efficiency | 15% | Does it avoid unnecessary steps, API calls, or verbosity? |
| Context-awareness | 15% | Does it use context files (me.md, work.md) appropriately? |

**Pass threshold:** 80% average. Below 80% → trigger IMPROVE mode.

---

## Key principles

- Instructions should explain the **why**, not just the what.
- Avoid overusing ALWAYS/NEVER caps directives — clear reasoning is better.
- Skills should generalize across many contexts, not just specific test cases.
- Keep SKILL.md under 500 lines — if it's longer, split into sub-skills.
- Add a `Updated YYYY-MM-DD:` line when making changes — tracks what changed and when.
- Platform note: On Claude Code, full subagent and browser workflow is available.

---

## Keonhee-specific quality checks

Before finalizing any skill:
- [ ] Does it reference the right context files? (me.md, work.md, current-priorities.md)
- [ ] Does it know about the consulting pivot? (McKinsey, BCG, Deloitte, Accenture targets)
- [ ] Does it know Keonhee's stack? (LangGraph, RAG, FastAPI, Streamlit, DART MCP)
- [ ] Does it avoid Gemini? (blocked in Korea — use Perplexity API instead)
- [ ] Does it follow the communication style? (no emojis, no filler, bullets over paragraphs)

---

## Output

New or updated skill saved to `.claude/skills/<skill-name>/SKILL.md`. Confirm path and key behaviors to user.
