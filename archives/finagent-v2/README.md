# FinAgent v2 — Dynamic Multi-Agent Routing

**Status:** ✅ ALREADY BUILT AND DEPLOYED. This is the live FinAgent.

**Note:** This was scoped as "v2" but the dynamic routing was implemented and deployed as the live app. `c:/Users/keonh/OneDrive/바탕 화면/FinAgent/agent/graph.py` is the actual implementation. See that file for the real code.

**What was built:**
- `router_agent.py` — GPT-4o classifier (sql_only | rag_only | both)
- `graph.py` — StateGraph with conditional edges, route_query() and route_after_sql() edge functions
- `AgentState` TypedDict with `route` field
- Live at keonhee-finagent.streamlit.app

This README is a planning document from before implementation. The actual code supersedes this spec.

---

## What changes

### v1 (current)
```
query → SQL Agent → RAG Agent → Report Agent → output
```
Every query hits all three agents regardless of what's asked.

### v2 (target)
```
query → Router Agent → SQL Agent only        → Report Agent
                     → RAG Agent only        → Report Agent
                     → SQL + RAG (both)      → Report Agent
```
The Router classifies the query first, then dispatches accordingly.

---

## Router logic

The Router node uses GPT-4o with a classification prompt:

```python
ROUTER_PROMPT = """
Classify this financial query into one of three types:
- "sql_only": needs structured data (numbers, dates, comparisons between companies)
- "rag_only": needs conceptual/narrative context (market trends, strategy, qualitative)
- "both": needs both structured data AND narrative context

Query: {query}

Return only: sql_only | rag_only | both
"""
```

---

## LangGraph implementation

### AgentState (expanded)
```python
class AgentState(TypedDict):
    query: str
    route: str          # "sql_only" | "rag_only" | "both"
    sql_result: str
    rag_result: str
    report: str
```

### Graph with conditional edges
```python
def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("router", run_router)
    workflow.add_node("sql_agent", run_sql_agent)
    workflow.add_node("rag_agent", run_rag_agent)
    workflow.add_node("report_agent", run_report_agent)

    workflow.set_entry_point("router")

    # Conditional routing
    workflow.add_conditional_edges(
        "router",
        route_decision,  # returns next node name
        {
            "sql_only": "sql_agent",
            "rag_only": "rag_agent",
            "both": "sql_agent",  # sql runs first, then rag
        }
    )

    workflow.add_edge("sql_agent", "report_agent")   # sql_only path
    workflow.add_edge("rag_agent", "report_agent")   # rag_only path
    # "both" path: sql → rag → report (needs intermediate edge)

    workflow.add_edge("report_agent", END)
    return workflow.compile()

def route_decision(state: AgentState) -> str:
    return state["route"]
```

---

## Interview story

**Before:** "FinAgent runs three agents in sequence."
**After:** "FinAgent v2 classifies the query first — a router agent decides whether to invoke the SQL agent, the RAG agent, or both, based on what the question actually needs. That's the difference between a pipeline and an agent that makes decisions."

This is the concrete "agent decision-making" example that was missing from v1.

---

## Files to create

```
FinAgent/agent/
├── graph.py          ← add router node + conditional edges
├── router_agent.py   ← new: GPT-4o classifier
└── (sql, rag, report agents unchanged)
```

---

## Build order

1. Write `router_agent.py` — classification prompt + GPT-4o call
2. Update `graph.py` — add router node, conditional edges
3. Update `AgentState` — add `route` field
4. Test with 3 query types (numerical, qualitative, mixed)
5. Update Streamlit UI — show which route was taken in the output
6. Update README and redeploy to Streamlit Cloud
