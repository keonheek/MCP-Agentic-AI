# Environment

## API Keys
Keys live in `.env` (gitignored — never commit).

| Key | Used by |
|-----|---------|
| `PERPLEXITY_API_KEY` | research skill, research-agent |
| `OPENAI_API_KEY` | RAG demo (embeddings + GPT-4o), FinAgent |
| `ANTHROPIC_API_KEY` | before_after.py (GEO agency), SME Diagnostic |
| `PINECONE_API_KEY` | Pinecone vector DB. Index: `kearney-demo` (1536 dims, cosine, AWS us-east-1) |
| `SUPABASE_API_KEY` | Supabase conversation history DB |
| `SUPABASE_URL` | `https://bnsimxodkdnfxspwntro.supabase.co` |
| `DARTFSS_API_KEY` | DART financial API (Lead Intelligence, consulting-emulation) |

## Projects (this repo)
Active workstreams in `projects/`. Each has a `README.md`.

| Project | Status |
|---------|--------|
| `projects/geo-agency/` | Active — first client pipeline |
| `projects/sme-diagnostic-ai/` | Built — needs live test + Streamlit deploy |
| `projects/lead-intelligence/` | Built — needs live test + Streamlit deploy |
| `projects/consulting-emulation/` | Deployed at keonhee-duediligence.streamlit.app |
| `projects/next-ai-role/` | Paused — resume at graduation 2027 |
| `projects/sdc/` | Active — SDC 학회 ops |
| `projects/langchain-learning/` | Planning stage |
| `projects/n8n-integration/` | Deferred until 3+ clients |

## External Projects
| Project | Location | URL |
|---------|----------|-----|
| FinAgent | `c:/Users/keonh/OneDrive/바탕 화면/FinAgent/` | keonhee-finagent.streamlit.app |
| Samsung Forecast | `c:/Users/keonh/OneDrive/바탕 화면/ai_project/06_Samsung_Forecast/` | keonhee-strategy.streamlit.app |
| RAG Demo | `demo/backend/` | local + ngrok |
| DART MCP | `c:/Users/keonh/OneDrive/바탕 화면/dart-mcp-server/` | local server |

## AWS
- Account ID: 582381607320 | Region: ap-northeast-2 (Seoul)
- Lambda API: `https://v7zapdvb10.execute-api.ap-northeast-2.amazonaws.com/`
- S3: `finagent-deploy-582381607320`

## GitHub
- PAT: token `superagent`, expires Apr 8 2026 — renew at github.com/settings/tokens
