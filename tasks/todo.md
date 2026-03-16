# Todo

_Active tasks only. Stale items removed. Updated 2026-03-13._

---

## From daily report (2026-03-16)

- [ ] **Activate Slack MCP** — SLACK_BOT_TOKEN + SLACK_TEAM_ID → `.mcp.json` → restart VS Code (30 min)
- [ ] **Install Context7 MCP** — add to `.mcp.json` (30 min, no auth needed)
- [ ] **Auto-research skill eval** — pick one underperforming skill, build binary test suite, run optimization loop (2-3h)

## From daily report (2026-03-14)

- [x] ~~**Slack MCP**~~ — Added to `.mcp.json` (2026-03-14). Needs tokens: SLACK_BOT_TOKEN + SLACK_TEAM_ID. See setup steps in session summary.
- [x] ~~**LangGraph 1.1.2 upgrade**~~ — Done (2026-03-14). `langgraph>=1.1.2` pinned in FinAgent requirements.txt.
- [ ] **Slack tokens** — Fill in `.mcp.json`: SLACK_BOT_TOKEN (`xoxb-...`) + SLACK_TEAM_ID (`T...`) → restart VS Code to activate
- [ ] **Claude fine-grained tool streaming** — N/A for FinAgent (uses OpenAI SDK). Revisit if Claude added as alternate model.
- [ ] **Context7 MCP** — Install: add to `.mcp.json` (30 min, live library docs in Claude Code)
- [ ] **DART MCP Server Card** — Add `.well-known/mcp.json` metadata for registry discoverability

## SDC Grader v2 — ✅ COMPLETE (2026-03-14)

- [x] ~~All applicants graded + sorted by score~~
- [x] ~~3/14 (토) interviews screened~~
- [ ] **3/15 (일) interviews** — Sunday screening remaining

## Blocked — needs human action

- [ ] **NotebookLM auth** — run `python -m notebooklm auth login` once (Chromium opens → sign in to Google)
- [ ] **GWS CLI auth** — manual flow: create Google Cloud project → enable APIs → create OAuth credentials → run `gws auth login`. Full guide in `references/sops/nodejs-setup.md` or GWS CLI agent output.
- [ ] **LinkedIn About** — paste from `projects/next-ai-role/linkedin-about.md` (5 min, consulting-framed bilingual)
- [ ] **GitHub PAT renewal** — expires Apr 8 2026. Renew at github.com/settings/tokens.
- [ ] **Supabase project restore** — supabase.com/dashboard/project/bnsimxodkdnfxspwntro → "Restore project" (free tier paused after inactivity)

## Job Applications — PAUSED (resume when timing is right)

_Korean companies use 자기소개서 (자소서), not cover letters. Drafts in `projects/next-ai-role/cover-letter-*.md` are 초안 — map to each portal's actual prompts when ready._

- [ ] **Deloitte Korea AI** — 95% fit ceiling (highest). Drafts ready. Wait for portal open.
- [ ] **Accenture Song/AI** — 93% fit. Deadline ~Apr 2026. Monitor portal.
- [ ] **McKinsey QuantumBlack** — 90% fit. Check mckinsey.com/careers/kr for Korea availability.
- [ ] **Upstage** — 92% fit. Rolling. joinstage@upstage.ai when ready.
- ~~BCG Gamma~~ — Now BCGX, portal closed, senior only. Removed.

## Portfolio visibility

- [x] ~~Push FinAgent to public GitHub~~ — done (2026-03-11, README GEO-optimized)
- [x] ~~GEO-optimize FinAgent README~~ — done (dynamic routing architecture accurate)
- [x] ~~GEO-optimize DART MCP README~~ — done
- [x] ~~GEO-optimize GitHub profile README~~ — done
- [x] ~~Push consulting-emulation to public GitHub~~ — done (2026-03-12). Live at github.com/keonhee3337-art/consulting-emulation. 22 files.
- [ ] **Push Samsung App to public GitHub** + run `/geo:github-readme`

## Skills gap closure

- [ ] SQL window functions: LAG, RANK, PARTITION BY — Mode Analytics tutorial + `references/consulting/sql-practice.md`
- [x] ~~AWS: deploy FinAgent to Lambda + API Gateway~~ — done (2026-03-13). Live: v7zapdvb10.execute-api.ap-northeast-2.amazonaws.com. Stack: finagent-prod.
- [ ] Case interviews: 10+ practice cases via `/interview-prep` "full case" mode (critical for BCG)
- [ ] PySpark basics: 2-hour crash course (just enough for McKinsey QB talking points) — guide in `references/consulting/mckinsey-qb-interview-prep.md`

## GEO Agency (when time permits)

- [ ] Identify 1 SDC connection with an online business
- [ ] Run free GEO audit — use `/geo:project-description` on their content
- [ ] Produce 1-2 page PDF: current AI citation vs. optimized. Show before/after in ChatGPT.
- [ ] Plan: `projects/geo-agency/README.md`

## Consulting Emulation Project — Fast Track (BCG deadline)

Do in order. 27h total / 7 days at 4h/day. Full plan: `projects/consulting-emulation/README.md`

- [x] ~~**Step 2.3** — Valuation Agent: DCF + Comparable Company Analysis~~ — done (2026-03-12). `projects/consulting-emulation/agents/valuation_agent.py`. Tested on Samsung, SK Hynix, LG.
- [x] ~~**Step 2.4** — RAGAS evaluation pipeline~~ — done (2026-03-12). `projects/consulting-emulation/eval/ragas_benchmark.py`. 15 Q&A benchmark, 4 metrics, per-question JSON output.
- [x] ~~**Step 1.1** — DART API live integration~~ — done (2026-03-12). `projects/consulting-emulation/data/dart_pipeline.py`. DART_API_KEY ✅ confirmed in FinAgent .env.
- [x] ~~**Step 1.2** — Hybrid search: BM25 + dense embeddings + RRF re-ranking~~ — done (2026-03-12). `projects/consulting-emulation/data/hybrid_search.py`. Install: `pip install rank-bm25`.
- [x] ~~**Step 3.1** — python-pptx auto slide deck generation~~ — done (2026-03-12). `projects/consulting-emulation/output/pptx_generator.py`. Test deck generated at `output/test_deck.pptx`. Install: `pip install python-pptx`.
- [x] ~~**Step 3.4** — AWS Lambda + API Gateway deploy~~ — done (2026-03-12). `projects/consulting-emulation/deploy/`. Run `./deploy.sh --guided` once AWS CLI + SAM CLI configured.
- [x] ~~**Streamlit UI** — app.py rewrite~~ — done (2026-03-13). Inter font, 4 Plotly charts, KPI row, two-column layout, renamed to "M&A Due Diligence Suite".
- [ ] **Streamlit Cloud deploy** — share.streamlit.io → New app → keonhee3337-art/consulting-emulation → app.py → URL: keonhee-duediligence → add secrets OPENAI_API_KEY + DARTFSS_API_KEY
- [x] ~~**AWS deploy** — done (2026-03-13). Live at `https://v7zapdvb10.execute-api.ap-northeast-2.amazonaws.com/`. Stack: finagent-prod (ap-northeast-2). Health: `/health` confirmed.~~

## Firm-Specific Ceiling Closers (do before interviews)

- [x] ~~**All firms** — XGBoost financial distress model~~ — done (2026-03-12). `projects/consulting-emulation/models/distress_model.py`. Run: `python models/distress_model.py`.
- [ ] **Deloitte** — AWS Cloud Practitioner cert (1 week) + publish RAGAS benchmark blog post (3h)
- [ ] **Accenture** — React/Next.js frontend deploy on Vercel (10h)
- [ ] **McKinsey QB** — Upload FinAgent artifacts to HuggingFace (4h) + PySpark basics crash course (2h)
- [ ] **BCG Gamma** — Enter Dacon or Kaggle data competition (rolling) — ranked performance = objective signal
- [ ] **Upstage** — Fine-tune small model on Korean financial text with LoRA (1-2 days) + email SKKU AI/NLP professor re: research collab

## Backlog (FinAgent upgrades)

- [x] ~~FinAgent: 4 critical security/performance fixes~~ — done (2026-03-12): SQL read-only mode, OpenAI singletons, vector store cache, graph cache. Pushed to GitHub 2026-03-13.
- [ ] **FinAgent: Reboot Streamlit Cloud** — keonhee-finagent.streamlit.app → Manage app → Reboot (fixes already pushed to GitHub)
- [ ] FinAgent: Supabase Postgres checkpointer — restore project first, then test `db.bnsimxodkdnfxspwntro.supabase.co:5432`
- [ ] FinAgent: RAGAS evaluation pipeline (Step 8)
- [ ] FinAgent: Parallel SQL+RAG via LangGraph Send API (Step 5)

## Low priority / deferred

- [ ] Samsung App: push to public GitHub + GEO-optimize README
- [ ] PitchFi Agent — 2-4 week MVP (FinAgent + DART MCP). Build after consulting applications submitted.
- [ ] Context7 MCP — live library docs in Claude Code (30 min)
- [ ] LangChain learning project
