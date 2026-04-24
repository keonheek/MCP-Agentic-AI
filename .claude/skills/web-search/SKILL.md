# Skill: Web Search

Search the web directly from Claude Code — no manual tab-switching. Returns bullet-point summaries with sources.

Updated 2026-03-11: Added multi-query mode, context-awareness, and clear escalation rules.

## Trigger phrases
- "search for X"
- "look up X"
- "find recent info on X"
- "what's the latest on X"
- "quick search on X"

---

## How to use

Just ask naturally:
- "Search for Deloitte Korea AI internship 2026 application process"
- "Look up what McKinsey QuantumBlack does"
- "Find recent news on LangGraph updates"
- "What's the latest on Korean AI Framework Act enforcement?"

---

## What Claude does

1. **Run 1-2 targeted WebSearch queries** — specific enough to get useful results
2. **Filter for recency and relevance** — flag if results are more than 6 months old
3. **Return bullet-point summary** — most useful finding first
4. **Include source links** — for anything worth reading in full

---

## Search strategy by query type

| Query type | Strategy |
|------------|----------|
| Company research | "[Company] + internship/role + 2026" + "[Company] AI practice overview" |
| Tech docs | "[library name] [version] [specific feature]" + check official docs URL directly |
| Korean market | Add "Korea" + "2026" + try Korean terms (삼성, 카카오) if results are thin |
| News/trends | Add "site:techcrunch.com OR site:venturebeat.com" for tech news |

---

## Output format

- Bullet points — no paragraphs
- Lead with the most useful finding
- Sources listed at the bottom as: `[Source name](URL)`
- Flag: "Results may be outdated" if relevant

---

## Escalation logic

| Situation | Do this |
|-----------|---------|
| Any lookup, any query count | Use WebSearch + WebFetch — free, no escalation needed |
| Deep multi-hop research (5+ sub-questions, gap analysis) | Use /research Mode 3 (deep research loop, free) OR generate a Gemini 3.1 Pro Deep Research prompt for Keonhee to paste |
| YouTube video content needed | Escalate to /notebooklm skill |
| Korean-language source needed | Use Korean search terms; note if translation needed |
| Terminal-side autoresearch/benchmark research (NOT project scripts) | Use WebSearch — do not call Perplexity |

**Note:** Project scripts (`projects/sme-diagnostic-ai/agents/autoresearch.py`, `benchmark_research.py`) keep using Perplexity. The WebSearch-only rule applies to ad-hoc research requests in the Claude Code terminal.

---

## Notes
- Gemini Deep Research (3.1 Pro) is the preferred deep-research path — Claude generates the prompt, Keonhee pastes it into Gemini
- WebSearch is free and unlimited from Claude Code — no credit cost, no quota
- Do not fabricate URLs — only cite links from actual search results
- For job role lookups: also check LinkedIn Jobs, Saramin (Korean job board), and Himalayas
