# Keonhee's Technical Stack

_Load this file when working on any of Keonhee's Python AI projects._

## Stack overview

| Layer | Technology | Notes |
|---|---|---|
| Agent framework | LangGraph | StateGraph + TypedDict AgentState |
| RAG | Custom VectorDB | OpenAI embeddings + cosine similarity + JSON persistence |
| SQL | Text2SQL | Schema injection → GPT-4o → SQLite |
| Backend | FastAPI | POST endpoints exposing LangGraph pipelines |
| Frontend | Streamlit | Multi-tab: Final Report, SQL Results, RAG Findings |
| LLM | GPT-4o | Generation |
| Embeddings | text-embedding-3-small | Via OpenAI API |
| Language | Python | + numpy, pandas |

## Hard constraints

- **No ChromaDB** — incompatible with Python 3.14 (Pydantic v1 issue). Always use the custom VectorDB pattern.
- **No external VectorDB** — keep it custom: OpenAI embeddings + cosine similarity + JSON file.

## Standard patterns

### Custom VectorDB (always use this)
```python
import numpy as np, json, os
from openai import OpenAI

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_embedding(text, client):
    return client.embeddings.create(input=text, model="text-embedding-3-small").data[0].embedding
```

### LangGraph AgentState
```python
from typing import TypedDict
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    query: str
    # add fields per pipeline

def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("node_name", node_function)
    workflow.set_entry_point("node_name")
    workflow.add_edge("node_name", END)
    return workflow.compile()
```

## Active project paths

- `c:/Users/keonh/OneDrive/바탕 화면/FinAgent/` — deployed LangGraph + RAG + Text2SQL system
- `C:/Users/keonh/Dev/MCP_Agentic_AI/demo/` — RAG demo (FastAPI + Pinecone + Supabase)

## When to spawn coding-agent vs work in-session

- **In-session** — small edits, bug fixes, explaining code, single-file changes
- **Spawn coding-agent** — building a new FastAPI/LangGraph/RAG module from scratch, parallel coding tasks, anything that would pollute the main context with large code blocks
