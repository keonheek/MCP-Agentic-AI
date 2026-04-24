# Lead Intelligence

## What this is
Korean manufacturer screener + AI readiness scorer + GEO audit + outreach email generator. Exports to Excel.

## Key files
- `app.py` — Streamlit UI
- `geo_audit.py` — GEO audit engine. `audit_single_company()` works without DART.
- `notebooklm_run.py` — NotebookLM integration

## Status
Built (commit 12eb3b4). Needs Streamlit Cloud reboot at keonhee-leadintelligence.streamlit.app.

## Stack
- Python, Streamlit, dart-fss, Perplexity API, Anthropic API (Haiku)
- Keys: DARTFSS_API_KEY + PERPLEXITY_API_KEY + ANTHROPIC_API_KEY

## Critical quirks
- SAMPLE_COMPANIES = 5 (was 20 — crashes on cold start)
- `extract_fs()` wrapped in ThreadPoolExecutor(timeout=45) — no native timeout
- `@st.cache_data` broken for complex pipeline tuples — use `st.session_state`

## Run
```bash
streamlit run app.py
```
