# Daily AI Report — 2026-03-13

## Top Developments (past 24-48h)

- **LangGraph v1.1.1 released (Mar 11)** — Type-safe streaming (`version="v2"`) with unified `StreamPart` outputs, type-safe invoke returns `GraphOutput` with `.value` and `.interrupts`. Pydantic/dataclass coercion in v2 mode. Fully backwards-compatible opt-in. ([LangGraph GitHub](https://github.com/langchain-ai/langgraph))

- **GPT-5.4 launched with native computer use + 1M context** — 87.3% success rate on junior IB-style modeling tasks (up from 68.4%). Makes entry-level quant analysis a human-AI collaboration. Directly validates Keonhee's FinAgent positioning.

- **Claude Code v2.1.73** — Added `/claude-api` skill for API/SDK app building, modelOverrides for custom model mapping, session naming, multi-language voice STT. Bug fixes for hangs and OAuth reconnects.

- **MCP roadmap update (Mar 5)** — Priorities: MCP Server Cards (`.well-known` metadata discovery), stateless sessions for load balancer support, SSO auth, gateway patterns. Enterprise MCP adoption accelerating.

- **Microsoft Agent Framework (Q1 2026 GA)** — Merges AutoGen + Semantic Kernel. Async multi-agent chats, OpenTelemetry observability, cross-language Python/.NET, Azure integration, SOC 2 compliance.

---

## Implementable This Week

### 1. LangGraph v1.1 Type-Safe Streaming
- **What:** Opt-in `version="v2"` in `stream()`/`astream()` gives unified `StreamPart` objects with `.type`, `.ns`, `.data` keys. Cleaner than current raw chunk handling.
- **Why it matters:** FinAgent's LangGraph pipeline currently uses v1 streaming — upgrading gives typed outputs, better debugging, and production-grade patterns interviewers expect.
- **Effort:** 1-2 hours — upgrade `langgraph` to `>=1.1.1` in requirements.txt, update `stream()` calls.
- **Project:** FinAgent (`agent/graph.py`, `api.py`)

### 2. Context7 MCP (30 min)
- **What:** Live library documentation injected into Claude Code context — no more outdated LangGraph/Streamlit API guesses.
- **Why it matters:** Saves time every session. Already on todo.md, confirmed as top developer MCP tool.
- **Effort:** 30 min install — add to `.mcp.json`.
- **Project:** All projects (Claude Code quality-of-life)

### 3. MCP Server Cards for DART MCP
- **What:** Add a `.well-known/mcp.json` metadata file to the DART MCP server so it's discoverable by MCP registries and clients.
- **Why it matters:** As MCP adoption grows, discoverability via Server Cards will matter for portfolio visibility. DART MCP is a genuine moat — make it findable.
- **Effort:** 1 hour — write the metadata file, push to GitHub.
- **Project:** DART MCP server (`dart-mcp-server/`)

---

## Portfolio / Narrative Angles

- **GPT-5.4 at 87% on IB tasks** — The standard consulting/finance AI pitch is getting crowded fast. Keonhee's angle needs to be *agentic orchestration* (LangGraph multi-agent pipelines) + *Korean market data* (DART MCP), not just "I use GPT for finance." Sharpen the narrative: "I build the orchestration layer, not just the model calls."

- **Microsoft Agent Framework GA** — Enterprise is standardizing on multi-agent frameworks. Knowing LangGraph + understanding how it compares to AutoGen/Semantic Kernel is now a consulting interview talking point. One paragraph comparison = interview-ready.

- **MCP becoming enterprise infrastructure** — Azure Functions MCP GA, SSO, gateway patterns. Keonhee's DART MCP server is ahead of most student portfolios. GEO angle: publish a blog post or README section titled "Building Production MCP Servers for Korean Financial Data" — high citation potential.

---

## Action Queue

- [ ] Upgrade `langgraph` to `>=1.1.1` in FinAgent `requirements.txt` and update graph.py streaming to `version="v2"`
- [ ] Install Context7 MCP — add to `.mcp.json` (30 min, already on todo)
- [ ] Add `.well-known/mcp.json` Server Card to DART MCP server for registry discoverability
- [ ] Draft 1-paragraph comparison of LangGraph vs Microsoft Agent Framework for interview prep
