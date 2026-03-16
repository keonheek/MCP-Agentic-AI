---
name: research
description: Use when asked to research a topic, find recent information, or do deep investigation on something. Calls the Perplexity API (sonar model) with live web search and saves a full report to the research/ folder. Use this (not the research sub-agent) when quality matters more than cost.
---

# Skill: Research

Deep, context-aware research using Perplexity's sonar model with live web search. Goes beyond a quick web search — synthesizes multiple queries, filters for relevance to Keonhee's context, and saves a full report.

Updated 2026-03-11: Added deduplication check, YouTube escalation path, and consulting-specific research guidance.

## Trigger phrases
- "research X"
- "do deep research on X"
- "investigate X"
- "find out everything about X"
- "I need a research report on X"
- "look into X for me"

---

## What Claude does

1. **Check for existing report** — scan `research/` for a similar report first. If a recent one exists (< 7 days), ask before running again.
2. **Load context** — read `context/me.md`, `context/work.md`, `context/current-priorities.md`, `context/goals.md`
3. **Frame the question** — what does this research serve? (job prep, product opportunity, skill gap, etc.)
4. **Formulate 2-3 targeted queries** — specific, not generic. For consulting prep: include company name + "AI practice" + "2026"
5. **Read `.env`** — get `PERPLEXITY_API_KEY`
6. **Call Perplexity API** via Bash for each query:

```bash
PERPLEXITY_API_KEY=$(grep PERPLEXITY_API_KEY .env | cut -d'=' -f2)
curl -s "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sonar",
    "messages": [{"role": "user", "content": "YOUR_QUERY_HERE"}]
  }'
```

7. **Synthesize results** — combine findings, prioritize what's relevant to Keonhee's context, include sources
8. **Save full report** to `research/YYYY-MM-DD-[topic-slug].md` — include all sources, full detail
9. **Present summary in chat** — bullets only, key findings, link to saved report

---

## Output format (in chat)

- 3-5 bullet points, most relevant findings first
- Flag anything directly tied to current priorities (jobs, portfolio, product)
- One line: "Full report saved to research/[filename].md"

---

## Research query templates by use case

**Consulting firm prep:**
- "[Firm] QuantumBlack / BCG Gamma / Deloitte AI Korea 2026 internship application process"
- "[Firm] AI practice recent projects Korean market"
- "[Firm] intern interview process technical assessment 2026"

**Product opportunity:**
- "[Market] Korean AI startup opportunities 2026"
- "[Problem space] Korean regulation compliance AI tools"

**Technical:**
- "[Framework] [version] new features breaking changes 2026"
- "[Tool] best practices production deployment Python"

---

## Escalation paths

- **YouTube tutorial or lecture** → don't use research skill → use `/notebooklm` instead
- **Quick 1-2 fact check** → don't use research skill → use `web-search` instead
- **Cost matters more than quality** → use `research-agent` sub-agent (runs on Haiku, cheaper)

---

## Notes
- Always load context first — research should be tailored, not generic
- Save the report even for quick requests — it builds the knowledge base over time
- Check for duplicate reports before running — Perplexity API has a cost per call
- For Korean company research: try Korean-language queries if English results are thin (e.g., "딜로이트 AI 인턴십 2026")
