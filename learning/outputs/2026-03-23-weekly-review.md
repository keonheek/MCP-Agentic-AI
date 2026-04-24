# Weekly Review — Week of 2026-03-17 to 2026-03-23

_Date: 2026-03-23 | Type: Sunday synthesis | Time: ~20 min_

## What Was Built This Week (cross-track synthesis)

This was a heavy build week — less structured learning, more applied implementation across all 5 tracks simultaneously.

### AI Engineering (Track 1)
- **SME Diagnostic AI** — LangGraph 4-node pipeline: problem_structurer → benchmark_research → autoresearch_loop → deck_generator. Autoresearch pattern (generate → Haiku score → improve, max 8 iterations, threshold 7.5) implemented and working.
- **Lead Intelligence** — DART screener → AI readiness scorer → GEO audit → outreach email generator. ThreadPoolExecutor timeout pattern for unreliable external APIs (45s per company).
- **GEO Agency** — before_after.py with dynamic Claude model selection via Models API. WeasyPrint HTML/CSS PDF with fpdf2 fallback pattern.
- **MCP** — Obsidian MCP server built (10 tools: list, read, create, update, append, search, tag search, recent notes, vault structure, daily note).
- **Key pattern learned:** `try: import weasyprint; return _weasyprint_fn() except (ImportError, Exception): return _fpdf2_fn()` — graceful degradation for optional dependencies.

### SQL (Track 2)
- Applied in consulting-emulation project: SQLite queries for financial data retrieval
- Text2SQL pattern in FinAgent — natural language → SQL via LLM
- **Formal study not started yet** — SQLBolt Week 1 (aggregations) still in queue

### Data Engineering (Track 3)
- pandas used extensively: `.groupby()`, `.merge()`, financial ratio calculations across Lead Intelligence and consulting-emulation
- ThreadPoolExecutor for parallel API calls with timeout — practical data pipeline pattern
- **Formal study not started yet** — pandas advanced (.pipe(), .assign()) still in queue

### ML / Deep Learning (Track 4)
- XGBoost distress model trained on synthetic data, scored on real Korean company data (consulting-emulation)
- Embeddings: OpenAI text-embedding-ada-002 used in FinAgent RAG pipeline
- **Formal study not started yet** — bias/variance refresher still in queue

### Finance / Quant (Track 5)
- DART API: financial statements for 5+ Korean companies (삼성전기, 솔브레인, 현대모비스, LG이노텍, DB하이텍)
- DCF valuation logic in consulting-emulation
- Financial ratios: P/E, ROE, operating margin, debt-to-equity — used in Lead Intelligence AI readiness scorer
- **Formal study not started yet** — NPV/IRR Python implementation still in queue

---

## Key Patterns Mastered This Week

1. **Autoresearch loop** — generate → cheap model score → improve → repeat. Threshold-based exit. Applicable to any iterative content generation task.
2. **ThreadPoolExecutor timeout** — wraps any blocking I/O call with a hard timeout. Essential for unreliable external APIs.
3. **Graceful dependency degradation** — try premium library, except all errors, fall back to simpler implementation.
4. **Dynamic model selection** — `client.models.list()` → prefer haiku → sonnet → opus. Keeps costs minimal without hardcoding.
5. **LangGraph state threading** — AgentState TypedDict fields must be explicitly passed through every node. Missing one field = silent bug.

---

## Did It Click?
- [x] AI Engineering patterns — yes, all implemented in production code
- [ ] SQL formal study — not started, add to next week's non-negotiables
- [ ] Data Engineering formal study — not started
- [ ] ML formal study — not started
- [ ] Finance formal study — not started

## Next Week Focus
Formal study tracks need to start. Build week is done — next week: 1 lesson per track, saved to learning/outputs/.
- Monday: AI Engineering — RAGAS benchmark concepts
- Tuesday: SQL — SQLBolt aggregations (GROUP BY, HAVING, COUNT, SUM, AVG)
- Wednesday: Data Engineering — pandas advanced (.pipe(), .assign(), .query())
- Thursday: ML — bias/variance, train/val/test split, cross-validation
- Friday: Finance — NPV/IRR in Python with Korean company data
