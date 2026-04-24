# ERP Demo — GEO Agency

## What this is
Demo ERP for GEO Agency: quote tracker + client log + AI automations (Nate Herk framework). Doubles as portfolio piece for selling ERP builds to Korean SMEs.

## Key files
- `app.py` — Streamlit entry point, st.navigation (5 pages)
- `db.py` — SQLite CRUD + dashboard queries (6 tables)
- `ai_engine.py` — Claude Haiku AI features (follow-ups, speed-to-lead, quote suggest, weekly report)
- `pdf_gen.py` — Quote + invoice PDF generator (Navy+Teal style)
- `seed.py` — 5 demo clients at various pipeline stages

## Pages
1. `pages/dashboard.py` — KPIs, pipeline funnel, activity feed, alerts, weekly report
2. `pages/clients.py` — Client CRUD, interaction log, AI next-action recommender
3. `pages/quotes.py` — Quote builder with dynamic line items, AI suggest, PDF download
4. `pages/invoices.py` — Invoice from accepted quotes, payment tracking, PDF download
5. `pages/automations.py` — Follow-up queue, speed-to-lead, database reactivation

## Tech stack
- Streamlit, SQLite (erp_demo.db), fpdf2, Plotly, Anthropic Haiku API
- Korean UI text throughout

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Keys needed
- `ANTHROPIC_API_KEY` — for AI features (optional, graceful fallback without it)
