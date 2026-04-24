# SME AI Platform

AI automation services for Korean small businesses and startups.

## Services
- **GEO Audit** — AI visibility score (ChatGPT, Perplexity, Claude citability)
- **Customer Follow-Up** — Personalized KakaoTalk messages from customer CSV (coming soon)
- **AI Inquiry Responder** — Draft responses from FAQ context (coming soon)

## Stack
- **Frontend:** Reflex (Python → React)
- **Backend:** FastAPI + Uvicorn
- **Database:** Supabase (PostgreSQL + pgvector + Auth)
- **Deployment:** Railway (backend) + Reflex Cloud (frontend)
- **Payments:** Toss Payments / PortOne
- **Email:** Resend

## Running Locally

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set environment variables
Copy `.env.example` to `.env` and fill in:
```
PERPLEXITY_API_KEY=...
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...
```

### 3. Run backend
```bash
uvicorn backend.main:app --reload --port 8000
```

### 4. Run frontend (separate terminal)
```bash
cd frontend && reflex run
```

Frontend runs at http://localhost:3000
Backend API at http://localhost:8000
API docs at http://localhost:8000/docs

## Supabase Setup
1. Create project at supabase.com
2. Run `deploy/schema.sql` in the SQL Editor
3. Copy URL + service_role key to `.env`

## Deploy to Railway
1. Push to GitHub
2. Connect repo to Railway
3. Set env vars in Railway dashboard
4. Deploy — Railway auto-detects `railway.toml`
