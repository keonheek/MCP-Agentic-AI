---
description: Weekly M2 blindspot scan, email summary via Gmail MCP
---

# /m2-blindspot

Run `python agents/m2_blindspot/m2.py` first to refresh `agents/m2_blindspot/data/blindspot_TODAY.json`. If that fails, continue with available inputs.

Execute WebSearches for all 5 strands and synthesize a 5-strand blindspot report. Each strand: 2-5 findings + 1 action item.

**Strands:**
1. Competitive moves: new Korean AI agency entrants, pricing changes, case studies
2. Stack obsolescence: Anthropic / OpenAI / Upstage / Google / LangChain releases this week
3. Regulation drift: PIPA / 식약처 / AI Basic Act updates
4. Positioning gaps: "best Korean AI agency" queries on ChatGPT / Perplexity / Claude / Gemini
5. Internal drift: decisions reversed without log entry, lessons violated, build-vs-ship pattern

Rules:
- NO em dashes
- Be brutal. M2 surfaces uncomfortable truths.
- Each finding cites a source URL
- Korean + English mix natural

Send via Gmail MCP:
- To: `keonhee3337@gmail.com`
- Subject: `[M2 Weekly] YYYY-MM-DD Blindspot Report`
- Body: full 5-strand report inline (no Google Doc creation in cloud, simpler)

If Gmail MCP unavailable, print summary to session output.
