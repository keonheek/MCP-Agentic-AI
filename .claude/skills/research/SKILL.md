---
name: research
description: Research a topic using free WebSearch+WebFetch by default, a multi-hop deep research loop when the question warrants it, or generate a Gemini 3.1 Pro Deep Research prompt for Keonhee to paste externally. Perplexity is no longer the default — reserved only when WebSearch results are demonstrably insufficient.
---

# Skill: Research

Three modes. Pick by question depth.

Updated 2026-04-14: WebSearch is now the default. Perplexity is no longer invoked from terminal research. Gemini 3.1 Pro Deep Research is the external deep-research path.

## Trigger phrases
- "research X" / "investigate X" / "look into X" / "find out about X"
- "deep research on X" → Mode 3 or Gemini handoff
- "I need a full report on X" → Mode 3

---

## Mode selection — JUDGE BY REQUEST SHAPE

Claude picks the mode. Do not auto-upgrade. Err toward the lighter mode.

| Request shape | Use | Output | File saved? |
|---|---|---|---|
| "Find the site for X" / "what's the URL" / "list the X" / any flat lookup | **Mode 0: Lookup** | Flat list, URLs only, no descriptions unless asked | No |
| "What is X" / 1-3 facts / single angle | **Mode 1: Quick WebSearch** | Bullets + sources | No |
| "Research X" / needs synthesis across 5-10 sources | **Mode 2: WebSearch + WebFetch synthesis** | Summary + sources | Yes |
| "Deep research X" / "full report on X" / multi-hop 5+ sub-questions | **Mode 3: Deep Research Loop** or Gemini handoff | Structured report | Yes |

### Judgment rubric (in order)

**Keonhee may forget to say "deep" or "full report" even when he wants one.** Don't rely on keywords alone — judge by topic stakes.

1. **Request shape check** — is this a list/URL/fact lookup? → Mode 0. Stop here.
2. **Stakes check** — what does this research feed into?
   - **High-stakes** (client decision, offer design, pricing, pivot, market entry, investment, hiring, interview prep for specific company, major purchase, strategic choice): lean Mode 3 even without "deep"
   - **Medium-stakes** (skill learning, tool evaluation, general trend check, content input): Mode 2
   - **Low-stakes** (curiosity, background context, quick fact): Mode 1
3. **Keyword override** — user explicitly says "deep" / "full report" / "exhaustive" → Mode 3 regardless of stakes
4. **Ambiguity check** — if request is vague on depth AND stakes are unclear (could be either side), **ask one short question before running**:
   - "Quick lookup or do you want me to dig deeper? (quick = bullets now, deep = full report to `research/`)"
   - Ask only when genuinely ambiguous. Don't ask on obvious lookups or obvious reports.
5. **Prior work check** — search `research/` first. If a recent (<7d) report exists, reuse it instead of re-running.
6. **Output trimming** — about to write columns/sections/summaries the user didn't ask for? Cut them.

**Stakes examples (calibration):**
- "find me consulting club sites" → low stakes → Mode 0
- "what's LangGraph" → low stakes → Mode 1
- "look into Deloitte AI Korea internship" → high stakes (job decision) → Mode 2 without asking, maybe Mode 3 if he mentions applying
- "should I target 세무사 or 변호사" → high stakes → ask, then likely Mode 3
- "tell me about the Korean SME AI market" → ambiguous stakes → ask
- "pricing for GEO audits in Korea" → high stakes (pricing decision) → Mode 2/3 without asking

**Anti-patterns to avoid:**
- Auto-upgrading a lookup into a report because the topic feels "interesting"
- Saving a file for a flat list
- Adding columns (est. year, focus, alumni) the user didn't ask for
- Re-searching URLs already verified in the same session
- Writing executive summaries for 5-item lists

## Mode 0: Lookup (new)

For URL/fact/list requests. Minimal cost.

1. Run 1-3 targeted WebSearches
2. Return a flat list — URLs only unless descriptions were asked for
3. No file save. No sources section unless user asks.
4. No executive summary.
5. If the list is already in `research/` from a prior session, reuse it.

---

## Mode 1: Quick WebSearch

Use for 1-3 fact lookups. Just run WebSearch, return bullets + sources. No file saved.

## Mode 2: WebSearch + WebFetch Synthesis (default)

1. **Check for existing report** — scan `research/` for similar (<7 days old). Ask before re-running.
2. **Load context** — `context/me.md`, `context/work.md`, `context/current-priorities.md`, `context/goals.md`
3. **Frame the question** — what does this research serve?
4. **Run 2-4 WebSearch queries** — specific, not generic
5. **WebFetch top 3-5 results** for full content
6. **Synthesize** — tie findings to Keonhee's context
7. **Save report** to `research/YYYY-MM-DD-[topic-slug].md` with sources
8. **Chat summary** — 3-5 bullets, most relevant first, link to saved file

## Mode 3: Deep Research Loop (sub-agent delegated)

Free equivalent of Perplexity sonar-deep-research / Gemini Deep Research. Use when the question has multiple sub-dimensions and needs gap-filling.

**How it runs:** decompose in main session, then delegate Rounds 1+2 to a `general-purpose` sub-agent so the search context burn is isolated. Main session only ingests the distilled synthesis — not raw search transcripts.

**Loop:**

1. **Decompose** — main session breaks question into 5-8 sub-questions. Print them so Keonhee can correct scope.
2. **Delegate to sub-agent** — spawn `general-purpose` agent with sub-questions + instructions to run Round 1 (breadth) and Round 2 (gap fills), return a distilled synthesis + source list.
3. **Sub-agent Round 1** — for each sub-question, run 1 WebSearch, WebFetch top 2 results, write partials, mark `[GAP: ...]`.
4. **Sub-agent Round 2** — targeted searches on each gap.
5. **Sub-agent return** — structured synthesis + full source URLs + open questions. No raw transcripts.
6. **Main session writes** the final report to `research/YYYY-MM-DD-[topic-slug]-deep.md`.
7. **Chat summary** — executive summary bullets + link.

**Budget inside sub-agent:** soft cap ~40 WebSearch calls, ~30 WebFetches per run. Raise when topic warrants. Still $0 external API cost — this is Claude-native tooling, so cost is token consumption + Claude usage limits, isolated to the sub-agent context.

**When Mode 3 isn't enough → Gemini handoff.**

---

## Gemini 3.1 Pro Deep Research Handoff

Use when: question needs 30+ sources, genuinely exhaustive coverage, or cross-domain synthesis where Claude's in-terminal loop would take too long.

**Claude's job:** generate a prompt, give it to Keonhee. Do NOT run anything. Keonhee pastes into Gemini 3.1 Pro Deep Research.

**Prompt template:**

```
# Deep Research Request

## Topic
[One-sentence topic statement]

## Context (why this research matters)
[2-3 sentences on Keonhee's situation — pulled from context files. E.g., "I'm a SKKU business student building an AI agency targeting Korean SMEs. I need to understand X to decide Y."]

## Core questions
1. [Sub-question 1]
2. [Sub-question 2]
3. [Sub-question 3]
4. [Sub-question 4]
5. [Sub-question 5]

## What I already know (don't repeat)
- [Known fact 1]
- [Known fact 2]

## What I specifically need
- [Concrete deliverable 1 — e.g., "Market size estimate with 3+ data sources"]
- [Concrete deliverable 2 — e.g., "Competitor list with pricing"]
- [Concrete deliverable 3]

## Source preferences
- Prioritize: [primary sources, 2024-2026 data, Korean sources if topic is Korea-specific]
- Deprioritize: [marketing blogs, LLM-generated content farms]

## Output format
- Executive summary (5 bullets)
- One section per core question, with citations
- Open questions / uncertainties
- Source list

## Language
[English / Korean / bilingual]
```

**After handoff:** Claude says "Paste this into Gemini 3.1 Pro Deep Research. When you have the result, drop it in and I'll integrate it into `research/` and tie it back to current priorities."

---

## Output format (Modes 2 & 3, chat)

- 3-5 bullet points, most relevant first
- Flag anything tied to current priorities
- One line: "Full report saved to research/[filename].md"

---

## Research query templates

**Consulting firm prep:**
- "[Firm] QuantumBlack / BCG Gamma / Deloitte AI Korea 2026 internship"
- "[Firm] AI practice recent projects Korean market"

**Product opportunity:**
- "[Market] Korean AI startup opportunities 2026"
- "[Problem space] Korean regulation compliance AI tools"

**Technical:**
- "[Framework] [version] new features breaking changes 2026"

---

## Escalation paths

| Situation | Use |
|---|---|
| YouTube tutorial/lecture | `/notebooklm` |
| 1-2 fact check | `web-search` skill |
| Multi-hop + exhaustive + 30+ sources | Gemini 3.1 Pro handoff |
| Project script (SME Diagnostic, benchmark_research) | Keep Perplexity — untouched |

---

## Notes
- **Perplexity is NOT used for terminal research anymore.** Only project scripts still call it.
- Always load context first — research should be tailored, not generic
- Save reports even for quick requests — builds knowledge base over time
- Korean companies: try Korean queries if English results are thin
- Deduplicate: check `research/` before running
