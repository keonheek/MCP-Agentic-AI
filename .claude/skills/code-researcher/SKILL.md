# Skill: Code Researcher

Find, evaluate, and explain code approaches for agentic AI projects — with real examples from docs, repos, and the web.

Updated 2026-03-11: Added web search integration, version compatibility checks, and consulting-framing mode.

## Trigger phrases
- "find code for X"
- "what's the best way to build X"
- "how do I implement X in [tool/framework]"
- "compare approaches for X"
- "show me an example of X using LangChain / Claude API / LangGraph / FastAPI"
- "scaffold a project that does X"

---

## How to use

Be specific about what you're building:
- "Find code for building a multi-step LangGraph agent with conditional routing"
- "What's the best way to connect Claude to a Notion database via MCP"
- "Show me how to stream responses with the Claude API using Python"
- "Compare LangChain vs LangGraph for an agentic workflow"
- "How do I implement PostgreSQL checkpointing in LangGraph?"

---

## What Claude does

1. **Check existing files first** — scan the workspace for existing implementations before searching externally
2. **Search for current implementations** — use WebSearch or WebFetch for official docs, recent GitHub issues, and real examples
3. **Return a clean, working code snippet** with explanation
4. **Flag version compatibility** — specify which versions the code works with (especially LangGraph, LangChain — these change fast)
5. **Evaluate tradeoffs** if multiple approaches exist
6. **Add a "gotchas" section** for anything that's bitten developers before

---

## Output format

**What it does:** [one-line description]

```python
# clean, minimal, working code
# with inline comments where non-obvious
```

**Key things to know:**
- Version: works with [package==version]
- Gotchas: [common issues]
- Dependencies: [what needs to be installed]

**Tradeoffs** (if comparing approaches):
| Approach | Pro | Con | Use when |
|----------|-----|-----|----------|
| A | ... | ... | ... |
| B | ... | ... | ... |

---

## Keonhee's stack reference (check these first before searching)

- **LangGraph** — primary agent orchestration. Use `langgraph>=1.1.0`. Key patterns: `StateGraph`, `add_node`, `add_edge`, `add_conditional_edges`, `graph.stream(stream_mode="values")`, `MemorySaver` checkpointer.
- **Claude API** — `anthropic` Python SDK. Prefer tool_use for structured outputs. Streaming via `client.messages.stream()`.
- **OpenAI API** — `openai` Python SDK. Embeddings: `text-embedding-3-small` (1536 dims). Chat: `gpt-4o`.
- **FastAPI** — backend for RAG demo and FinAgent API. Use `async def` for LLM calls. CORS middleware for Streamlit integration.
- **Streamlit** — frontend. Use `@st.cache_resource` for expensive objects (graph, model). `st.session_state` for per-user state.
- **Pinecone** — RAG demo vector DB (index: kearney-demo, 1536 dims, cosine, AWS us-east-1)
- **SQLite + sqlite3** — FinAgent financial data. Standard Python, no ORM.
- **MCP** — custom DART server at `c:/Users/keonh/OneDrive/바탕 화면/dart-mcp-server/server.py`

---

## Special modes

- **"explain this like I need to present it"** → adds a plain-English explanation suitable for a consulting interview or pitch (no jargon)
- **"scaffold a project"** → generates a full directory structure with starter files
- **"what changed in [version X]"** → looks up changelog and highlights breaking changes relevant to Keonhee's stack

---

## Notes
- Always specify Python version compatibility — Keonhee is on Python 3.14; some packages (ChromaDB) don't support it
- If the official docs conflict with what actually works, note that explicitly
- For LangGraph specifically: the API changed significantly between 0.x and 1.x — always confirm version
- Prefer minimal examples over comprehensive ones — Keonhee can extend, but complexity is hard to debug
