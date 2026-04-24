# SME Diagnostic AI

## What this is
LangGraph 4-node pipeline that diagnoses Korean SME business problems and generates a PowerPoint deck with benchmarks and recommendations.

## Key files
- `app.py` — Streamlit UI with follow-up chat + PDF/txt/md upload
- `graph.py` — LangGraph pipeline definition
- `agents/problem_structurer.py` — Node 1: claude-sonnet-4-6, structures problem
- `agents/benchmark_research.py` — Node 2: Perplexity sonar-pro, industry benchmarks
- `agents/autoresearch.py` — Node 3: Haiku scorer, max 8 iter, threshold 7.5
- `output/deck_generator.py` — Node 4: python-pptx, 12 slides

## Status
Built. Needs live test + Streamlit Cloud deploy (keonhee-sme-diagnostic).

## Stack
- Python, LangGraph, Streamlit, python-pptx
- Keys: ANTHROPIC_API_KEY + PERPLEXITY_API_KEY

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Personalization fields
revenue, employees, industry, founded_year — wired through all 4 nodes.
