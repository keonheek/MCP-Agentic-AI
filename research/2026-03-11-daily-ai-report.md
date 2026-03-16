# Daily AI Report — 2026-03-11

_Automated daily intelligence sweep. Stack filter: Python, LangGraph, RAG, MCP, Claude API, OpenAI API, FastAPI._

---

## Top Developments (Past 24-48h)

- **LangGraph v1.1 released (March 10)** — Type-safe streaming via `version="v2"` parameter in `stream()` / `astream()`. Returns unified `StreamPart` output with `type`, `ns`, `data` keys per chunk. Type-safe invoke now returns `GraphOutput` with `.value` and `.interrupts`. Pydantic/dataclass coercion built-in. Checkpointing fixes: time travel no longer reuses stale `RESUME` values, subgraphs restore correct parent checkpoints. [Source: LangChain changelog]

- **SECURITY — LangGraph BaseCache vulnerability (CVSS 8.1, March 3)** — Deserialization of untrusted data allows remote code execution via BaseCache. Patched in latest release. **Update immediately.** `pip install --upgrade langgraph` [Source: ZDI-26-135]

- **checkpointpostgres v3.0.0 released** — LangGraph's Postgres checkpointer now supports Python 3.14 (dropped 3.9). Production-grade persistent state for LangGraph agents. [Source: LangGraph GitHub releases]

- **OpenAI deprecating Assistants API mid-2026 in favor of MCP** — MCP becoming the cross-platform standard for tool/agent integrations. Enterprise adoption accelerating. No new MCP servers of note this week — ecosystem focus is on security hardening and enterprise patterns rather than new servers. [Source: Verdent AI MCP guide]

- **RAG 2026 consensus:** "Standard RAG is dead" narrative solidifying. Production systems now expected to have: hybrid search (BM25 + dense), cross-encoder reranking, iterative/agentic retrieval loops, graph-enhanced retrieval. Single-pass cosine similarity retrieval is considered tutorial-level. [Source: NeuraMonks, StackAI, dev.to]

---

## Implementable This Week

### 1. LangGraph v1.1 Streaming — FinAgent `[Priority: HIGH]`
**What:** The new `version="v2"` streaming API is exactly the streaming upgrade identified in the improvement plan (Step 9), now with a clean unified interface.
**How:** In `app.py`, replace `graph.invoke(...)` with `graph.astream(..., version="v2")` and yield `StreamPart` objects. Streamlit supports `st.write_stream()` for token-by-token display.
**Why it matters:** Closes the biggest UX gap in FinAgent. Pipeline results appear as they complete (SQL result shows first, then RAG, then report) instead of blank spinner for 8+ seconds.
**Effort:** 3-4 hours
**Project:** FinAgent

```python
# Before
result = graph.invoke(state)

# After (v1.1)
async for part in graph.astream(state, version="v2"):
    if part.type == "values":
        yield part.data  # stream to Streamlit
```

### 2. Security patch — update LangGraph immediately `[Priority: URGENT]`
**What:** CVE-level vulnerability in BaseCache. Update now.
**How:** `pip install --upgrade langgraph` in FinAgent and RAG Demo environments.
**Effort:** 5 minutes

### 3. Postgres Checkpointer for FinAgent `[Priority: MEDIUM]`
**What:** `checkpointpostgres v3.0.0` is production-ready and Python 3.14 compatible. Use Supabase's Postgres (already have credentials) as the checkpointer backend.
**Why it matters:** Multi-turn conversation memory survives session restarts. The same Supabase instance used by RAG Demo can host LangGraph checkpoints.
**Effort:** 4-6 hours (Step 4 from improvement plan, now easier with v3.0.0)
**Project:** FinAgent

### 4. Context7 MCP — add to second brain `[Priority: LOW-MEDIUM]`
**What:** MCP server that fetches live documentation for any library. Instead of training cutoff docs, agents get current API docs.
**Why it matters:** When asking Claude Code about LangGraph or FastAPI patterns, it would retrieve actual current docs rather than potentially stale knowledge.
**How:** Add to `.mcp.json` via npx — check mcpmarket.com for install command.
**Effort:** 30 minutes

---

## Portfolio / Narrative Angles

- **LangGraph v1.1 streaming** gives a concrete answer to the interview question "what would you improve about your system?" — "I'm upgrading FinAgent to v1.1's type-safe streaming so intermediate results surface in real-time rather than waiting for the full pipeline."

- **OpenAI deprecating Assistants API for MCP** validates the DART MCP server project. The narrative is now: "I built a custom MCP server for Korean financial data before MCP became the enterprise standard." That's a forward-looking portfolio signal.

- **"Standard RAG is dead"** narrative means the RAG Demo's single-pass cosine retrieval is increasingly obvious as a gap. Adding hybrid search (Step 7 from improvement plan) before any consulting interviews is now more urgent.

---

## Action Queue

- [x] Read this report
- [ ] `pip install --upgrade langgraph` in FinAgent + RAG Demo (URGENT — security)
- [ ] Implement LangGraph v1.1 streaming in FinAgent app.py (HIGH — 3-4 hours)
- [ ] Wire checkpointpostgres v3.0.0 to Supabase for FinAgent (MEDIUM — 4-6 hours)
- [ ] Check Context7 MCP install on mcpmarket.com (LOW — 30 min)

---

_Sources: LangChain changelog, GitHub langchain-ai/langgraph releases, ZDI-26-135, Verdent AI MCP guide, NeuraMonks, StackAI advanced RAG, dev.to RAG blueprint, MCP registry_
