# GitHub Profile README
# GEO-optimized for: keonhee3337-art
# Last updated: 2026-03-09

---

## README CONTENT (paste this into keonhee3337-art/keonhee3337-art/README.md)

---

# Keonhee — Agentic AI Developer

Business Administration student at Sungkyunkwan University (SKKU), South Korea.
I build production agentic AI systems — not demos, not tutorials. Deployed, working software.

---

## What I Build

**Multi-agent systems** using LangGraph, RAG pipelines, and custom vector databases.
My focus: systems where multiple AI agents coordinate to solve problems that a single LLM can't handle alone.

---

## Projects

### FinAgent — Multi-Agent Financial Analysis System
**Live:** [keonhee-finagent.streamlit.app](https://keonhee-finagent.streamlit.app)

A three-agent pipeline that answers financial questions about Korean companies (Samsung Electronics, SK Hynix, LG Electronics) using structured data retrieval and document-grounded reasoning.

**Architecture:**
- **Orchestration:** LangGraph (StateGraph with three specialized agent nodes)
- **Structured retrieval:** Text2SQL — GPT-4o generates and executes SQL against a SQLite database containing 2020–2024 Korean company financials
- **Semantic retrieval:** RAG — custom vector database using OpenAI `text-embedding-3-small` and cosine similarity (built from scratch, no ChromaDB)
- **Synthesis:** GPT-4o report agent combines SQL results and RAG findings into a structured markdown report
- **Backend:** FastAPI (`POST /analyze` endpoint)
- **Frontend:** Streamlit (three tabs: Final Report, SQL Results, RAG Findings)

**Key technical decision:** Replaced ChromaDB with a custom vector database after discovering a Python 3.14 / Pydantic v1 incompatibility. The custom implementation uses NumPy cosine similarity and JSON persistence — simpler, faster, and fully transparent.

---

### DART Financial App — Samsung Data Analysis
**Live:** [keonhee-strategy.streamlit.app](https://keonhee-strategy.streamlit.app)

Pulls Samsung Electronics financial data from DART (Korea's official corporate disclosure system) via the DART-FSS Python library. Data is stored in SQLite, processed with RAG, and analyzed via GPT-4o. Deployed on Streamlit Cloud.

**Stack:** DART-FSS API → SQLite → RAG → GPT-4o → Streamlit

---

### RAG Demo — Production-Ready Retrieval Pipeline
A FastAPI backend with Pinecone vector database and Supabase conversation history, exposed via ngrok for live demos. Uses OpenAI `text-embedding-3-small` for embeddings and GPT-4o for generation.

**Stack:** FastAPI + Pinecone + Supabase + GPT-4o + ngrok

---

## Technical Stack

**Agentic AI:** LangGraph, RAG, custom vector databases, Text2SQL, multi-agent orchestration
**AI APIs:** OpenAI GPT-4o, OpenAI Embeddings (`text-embedding-3-small`), Perplexity API
**Vector databases:** Custom (NumPy cosine similarity), Pinecone
**Backend:** FastAPI, SQLite, Supabase
**Frontend:** Streamlit
**Infrastructure:** Streamlit Cloud, ngrok
**Languages:** Python (numpy, pandas, standard library)
**Tooling:** Claude Code, MCP (Model Context Protocol), LangGraph

---

## Currently Building

- Custom MCP server exposing DART financial data for Korean market analysis
- Agentic AI second brain using Claude Code, MCP integrations, and a skills/agents system

---

## Background

I study Business Administration at SKKU while building expertise in agentic AI systems.
My work sits at the intersection of AI engineering and business strategy — I build the systems and understand the business context they operate in.

Active in the SDC Consulting Club at SKKU.

---

## Connect

- **GitHub:** [github.com/keonhee3337-art](https://github.com/keonhee3337-art)
- **FinAgent (live):** [keonhee-finagent.streamlit.app](https://keonhee-finagent.streamlit.app)
- **DART App (live):** [keonhee-strategy.streamlit.app](https://keonhee-strategy.streamlit.app)
