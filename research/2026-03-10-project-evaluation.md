# Project Evaluation & Improvement Plan — 2026-03-10

_Honest code-level assessment of all three projects vs. production best practices._

---

## How to Read This

Each project is scored across 5 dimensions on a 1–5 scale:
- **Architecture** — design quality, separation of concerns
- **Production Readiness** — error handling, scalability, observability
- **Technical Depth** — complexity relative to what's standard in the field
- **Portfolio Signal** — how it reads to a technical hiring manager
- **Correctness** — does it actually do what it claims correctly?

**Benchmark baseline:** What a senior ML engineer at a consulting firm or AI startup would build in a similar timeframe.

---

## Project 1 — FinAgent (LangGraph Multi-Agent)

**Live:** keonhee-finagent.streamlit.app

### What's genuinely good
- Real LangGraph `StateGraph` with `TypedDict` state and conditional edges — not just chained function calls. This is the correct pattern and most tutorials get this wrong.
- Dynamic routing (sql_only / rag_only / both) is a real architectural decision, not just a linear pipeline. The `route_after_sql` conditional edge is correctly implemented.
- Custom VectorDB from scratch is a legitimate differentiator — you understand the mechanism, not just the API.
- Text2SQL with schema-aware prompting and graceful fallback on SQL execution error is solid.
- Clean file separation: graph.py, router_agent.py, sql_agent.py, rag_agent.py, report_agent.py — readable, modular.

### Honest weaknesses vs. industry standard

**1. No checkpointing (biggest gap)**
LangGraph ships with a built-in memory checkpointer (`MemorySaver`) and Postgres checkpointer. Production agents persist state across sessions — if you refresh, the conversation context survives. Your implementation starts fresh on every query. This is the single most visible gap to anyone who knows LangGraph.

**2. Sequential "both" path when parallel is possible**
When `route == "both"`, sql_agent runs first, then rag_agent. These are independent — they don't use each other's outputs. LangGraph's `Send` API enables parallel node execution. A senior engineer would run both in parallel and join before report_agent. This cuts latency in half on the most expensive path.

**3. No streaming**
The UI shows a spinner until the entire 4-agent pipeline completes. Production LangGraph apps stream intermediate outputs: the SQL result appears as soon as sql_agent finishes, the RAG result appears next, and the report streams token-by-token. LangGraph has `astream_events` for this.

**4. Router burns GPT-4o on a 3-class classification**
`run_router_agent` calls GPT-4o at `temperature=0` to produce one of three words. GPT-4o-mini costs 15x less and is perfectly adequate for this. At scale this is a real cost problem.

**5. VectorDB is O(n) on every query**
`query_vector_store` loads the entire JSON file from disk and scores every document on every call. For 20 documents this is fine. For 500+ documents this becomes a bottleneck. Production VectorDB either keeps vectors in memory on startup or uses an ANN index (FAISS, HNSWlib).

**6. No retrieval evaluation**
There's no way to know if the top-3 documents are actually the most relevant for a given query. Production RAG pipelines measure context precision and recall (RAGAS framework). Without this, you can't improve retrieval quality systematically.

**7. No reranking**
After cosine similarity retrieval, a cross-encoder reranker (Cohere Rerank, BGE-reranker) significantly improves precision. Most production RAG systems use two-stage retrieval: fast ANN search → rerank with a cross-encoder.

**Scores:**
| Dimension | Score | Notes |
|---|---|---|
| Architecture | 4/5 | LangGraph pattern is correct and clean |
| Production Readiness | 2/5 | No checkpointing, no streaming, no observability |
| Technical Depth | 3.5/5 | Custom VectorDB is genuine depth; routing is real |
| Portfolio Signal | 4/5 | Strongest project — multi-agent + Text2SQL is rare |
| Correctness | 4/5 | Works correctly; SQL error handling is solid |

**Overall: 3.5/5** — Strong foundation, clear production gaps.

---

## Project 2 — Enterprise RAG Demo (FastAPI + Pinecone + Supabase)

**Live:** web-production-e3a16.up.railway.app

### What's genuinely good
- Production infrastructure stack is correct: Pinecone for vectors, Supabase for conversation persistence, Railway for hosting. This is what a startup would use.
- FastAPI with proper Pydantic request/response models, CORS, health endpoint — clean API design.
- Graceful fallback: Supabase fails → in-memory. Good defensive programming.
- Frontend is polished — source cards with relevance scores, session turn counter, animated pipeline visualization. This communicates what's happening to a non-technical viewer.
- Clean 3-file backend: rag.py, db.py, main.py — each does one thing.

### Honest weaknesses vs. industry standard

**1. Pure semantic search only (no hybrid)**
`search()` does a single dense vector lookup. Production RAG uses hybrid search: BM25 (keyword) + dense semantic, then merge results. Dense search misses exact keyword matches (company names, financial metrics, ticker symbols). For financial queries like "DART 2023 Samsung operating profit", BM25 would outperform pure semantic.

**2. No reranking**
Same gap as FinAgent. Top-4 by cosine score, no cross-encoder pass.

**3. No query preprocessing**
If someone asks "what about last year's numbers?" the query goes directly to Pinecone without resolving the reference. A `query_rewriter` node that resolves pronouns and references using conversation history would improve multi-turn quality significantly.

**4. CORS allows all origins**
`allow_origins=["*"]` is fine for a demo. In production this is a security issue — the API is callable from any origin. Should be locked to the frontend domain.

**5. Session lost on page refresh**
`sessionId` lives in JavaScript memory. When the user refreshes, a new UUID is generated and history is lost despite being in Supabase. The session ID should be persisted to localStorage.

**6. No streaming**
Full response before any UI update. For a demo this matters — users see a blank loading spinner for several seconds. Streaming would make the demo feel dramatically faster.

**7. No evaluation or observability**
No logging of latency, no tracking of which queries return low-confidence results, no ability to monitor retrieval quality over time.

**Scores:**
| Dimension | Score | Notes |
|---|---|---|
| Architecture | 4/5 | Clean separation, correct stack choices |
| Production Readiness | 2.5/5 | CORS, session persistence, no streaming |
| Technical Depth | 3/5 | Standard RAG with production infra |
| Portfolio Signal | 3.5/5 | Good but the stack (Pinecone + Supabase) is what everyone uses |
| Correctness | 4.5/5 | Works cleanly, fallback logic is good |

**Overall: 3.5/5** — Cleaner code than most tutorials; missing the retrieval quality layer.

---

## Project 3 — Samsung DART Financial App

**Live:** keonhee-strategy.streamlit.app

_Note: Only the forecasting scripts are visible locally (`advanced_forecast.py`, `stock_prediction.py`). The deployed app's RAG + shock simulator code isn't in the visible directory. Evaluating based on CV description + visible scripts._

### Visible code: `advanced_forecast.py`

This is Prophet + yfinance — a standard time series forecast. The code is clean but this is tutorial-level. Prophet is documented with this exact use case (stock prices) in its official docs. It doesn't demonstrate AI engineering — it demonstrates following a tutorial.

### The deployed app (from CV description)

"DART-FSS → SQLite → RAG → GPT-4o + macroeconomic shock simulator (USD/KRW, SOX Index → operating profit impact, Plotly waterfall charts)"

This is genuinely more interesting than the visible scripts. The DART data ingestion pipeline + domain-specific RAG + scenario modeling is a stronger signal.

### Honest weaknesses vs. industry standard

**1. Static data snapshot**
DART financial data is ingested once and stored in SQLite. Samsung's actual financials update quarterly. A production financial intelligence tool would have a scheduled DART refresh (weekly or quarterly trigger). This is a meaningful gap — the "live" claim in the demo is misleading for analysts.

**2. No confidence scoring on shock simulator outputs**
The macroeconomic shock simulator produces impact numbers, but with no confidence intervals or scenario probabilities. A sell-side analyst would immediately ask "what's the standard error on this?" The Plotly waterfall chart is good visually but lacks error bars.

**3. Prophet is the wrong model for financial forecasting in a portfolio context**
Prophet is a trend + seasonality decomposition model, not a financial forecasting model. For stock prices, Prophet is explicitly not recommended (the series has no seasonality patterns it can learn). ARIMA, LSTM, or a simple momentum baseline would be more defensible. This becomes a liability in an interview if a quant asks about the model choice.

**4. Single-company scope**
Samsung only. A competitor comparison (Samsung vs. TSMC vs. Intel) would be far more useful as a consulting tool and more impressive as a portfolio piece.

**5. No backtesting**
The Prophet forecast has no out-of-sample validation. You can't know if it would have predicted the 2023 Samsung revenue decline. Any serious forecasting tool shows backtesting results.

**Scores:**
| Dimension | Score | Notes |
|---|---|---|
| Architecture | 3/5 | DART → SQLite → RAG is solid; Prophet is weak |
| Production Readiness | 2/5 | Static data, no refresh, no backtesting |
| Technical Depth | 3/5 | DART ingestion is domain-specific depth; forecast is tutorial |
| Portfolio Signal | 3/5 | Interesting domain; model choices are questionable |
| Correctness | 3.5/5 | Works; Prophet is correct code, wrong tool |

**Overall: 3/5** — Most room for improvement. Interesting domain but the technical execution is thinnest here.

---

## Cross-Project Gaps (All Three)

| Gap | All three | Impact |
|---|---|---|
| No evaluation framework (RAGAS/deepeval) | ✅ | Can't prove retrieval quality |
| No streaming | ✅ | Poor UX in demos |
| No observability (LangSmith, logging) | ✅ | Can't debug production issues |
| No reranking | ✅ | Retrieval quality ceiling is lower |
| No tests | ✅ | No unit or integration tests anywhere |
| Static data | ✅ | Nothing updates automatically |

---

## Honest Overall Assessment

These projects are in the **top 10-15% of student AI portfolios** — they are deployed, they use the right frameworks, they demonstrate understanding of the underlying mechanisms (custom VectorDB, conditional routing, DART ingestion). Most student projects are Jupyter notebooks with no deployment.

The gap vs. a **senior ML engineer** at a consulting firm: primarily in production concerns (evaluation, observability, streaming, data freshness) and advanced retrieval (hybrid search, reranking). The architecture is sound; the polish is missing.

The gap vs. **other competitive student candidates at Deloitte/McKinsey/BCG AI roles**: you're ahead on depth (custom VectorDB, LangGraph, MCP) but behind on GitHub visibility and test coverage.

---

## Step-by-Step Improvement Plan

Sequenced by impact-per-hour. Each step has an honest time estimate.

---

### TIER 1 — High impact, low effort (do these first)

**Step 1 — Add LangSmith tracing to FinAgent** `[2-3 hours]`
LangSmith is LangChain's observability platform. Adding it is 3 lines of code. It gives you a trace of every agent call — tokens used, latency, inputs/outputs — which you can screenshot for interviews. Interviewers ask "how do you debug a multi-agent system?" and you can show them.
```python
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "..."
```
This adds exactly zero complexity to the code and makes the project look dramatically more production-aware.

**Step 2 — Fix session persistence in RAG Demo** `[1 hour]`
Persist `sessionId` to `localStorage`. One line of JS. Supabase already stores the history — you're just not using it across refreshes. This closes a visible demo gap.

**Step 3 — Push FinAgent + Samsung App to GitHub with proper READMEs** `[3-4 hours]`
Currently invisible to anyone who searches for your work. READMEs should include: architecture diagram (ASCII is fine), tech stack, how to run, what problems it solves. Then run `/geo:github-readme` on each.

---

### TIER 2 — Real technical improvements (1 week total)

**Step 4 — Add LangGraph checkpointing to FinAgent** `[4-6 hours]`
```python
from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()
workflow.compile(checkpointer=checkpointer)
```
With a thread_id per user session, the agent now remembers previous queries. Multi-turn conversation works correctly. This is the single biggest LangGraph gap.

**Step 5 — Parallel SQL + RAG execution in FinAgent** `[3-4 hours]`
Use LangGraph's `Send` API to fan out sql_agent and rag_agent simultaneously when `route == "both"`. Reduces pipeline latency from ~8s to ~4s on combined queries. Clean architecture change with visible performance benefit.

**Step 6 — Swap router from GPT-4o to GPT-4o-mini** `[30 minutes]`
One line change in router_agent.py. 15x cost reduction on routing with no quality loss. Shows cost-conscious engineering mindset.

**Step 7 — Add hybrid search to RAG Demo** `[1 day]`
Add BM25 (keyword) retrieval alongside Pinecone dense retrieval, then merge results with a weighted score. Library: `rank_bm25`. This is a standard production pattern and clearly differentiates from basic RAG.

---

### TIER 3 — Advanced (makes the portfolio genuinely senior-level)

**Step 8 — RAGAS evaluation pipeline** `[2 days]`
Build a test set of 20 question-answer pairs for FinAgent. Run RAGAS metrics (faithfulness, answer relevance, context precision). Publish the scores. No other student candidate will have benchmarked their own RAG system. This is the most differentiating thing you can add.

**Step 9 — Streaming responses** `[1 day per project]`
FastAPI supports streaming via `StreamingResponse`. LangGraph supports `astream_events`. The UI change is small (append tokens as they arrive). Demo becomes visually 10x more impressive.

**Step 10 — Live DART data refresh for Samsung App** `[1-2 days]`
Add a scheduled refresh (APScheduler) that re-ingests DART data quarterly. The app then truthfully claims to use live data. Replace Prophet with a simpler but more defensible baseline (rolling average + confidence interval) or LSTM if you want to learn it.

**Step 11 — Cross-encoder reranking in both RAG systems** `[1 day]`
Add Cohere Rerank or a local BGE-reranker as a second retrieval pass. Measurably improves answer quality on ambiguous queries. Pairs well with the RAGAS evaluation — you can show before/after scores.

---

## Full Timeline Summary

| Phase | Steps | Time | Outcome |
|---|---|---|---|
| Week 1 | Steps 1–3 | ~8 hours | Observability on, GitHub visible, session fixed |
| Week 2 | Steps 4–6 | ~10 hours | Checkpointing, parallel agents, cost optimization |
| Week 3 | Step 7 | ~8 hours | Hybrid search in RAG Demo |
| Weeks 4–5 | Steps 8–9 | ~3 days | RAGAS evaluation + streaming |
| Weeks 6–8 | Steps 10–11 | ~3 days | Live data + reranking |

**To go from current state to genuinely senior-level portfolio: ~4-6 weeks of part-time work (2-3 hours/day).**

The two highest-ROI steps for interview impact specifically:
1. LangSmith tracing (2 hours, makes you look production-aware)
2. RAGAS evaluation scores (2 days, makes you the only candidate who measured their own system)
