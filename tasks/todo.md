# Todo

_Restructured 2026-03-19. Priorities driven by BCGX feedback: close the work experience gap._

---

## Daily Non-Negotiables

- AI CPA exam study (30-60 min)
- SDC 학회 responsibilities (as they come)
- One action toward GEO service launch

---

## This Week (March 19-25)

- [ ] **Reboot all 4 Streamlit apps** (20 min total, human action)
  - [ ] keonhee-leadintelligence.streamlit.app (commit 12eb3b4)
  - [ ] keonhee-finagent.streamlit.app (commit 7346b58)
  - [ ] keonhee-strategy.streamlit.app (beautifulsoup4 fix)
  - [ ] keonhee-duediligence.streamlit.app (fastapi removed)
- [ ] **SDC OT Wednesday** — assign 10 members to IM/PR/EDU branches + select team leads
- [ ] **Share Notion SDC workspace** with all members
- [ ] **Live test SME Diagnostic AI** — `streamlit run app.py`, verify follow-up chat + PDF upload + deck download
- [ ] **Live test Lead Intelligence** — `streamlit run app.py`, verify 5-company DART run completes in <5 min
- [ ] **Build GEO audit PDF report generator** — `projects/geo-agency/geo_report_pdf.py` (fpdf2, 2-page PDF)
- [ ] **Build single-company audit mode** — add `audit_single_company()` to `geo_audit.py`
- [ ] **Build before/after proof generator** — `projects/geo-agency/before_after.py`
- [ ] **Build GEO Agency Streamlit app** — `projects/geo-agency/app.py`
- [ ] **LinkedIn About** — paste from `projects/next-ai-role/linkedin-about.md` (5 min)

## Next Week (March 26 - April 1)

- [ ] **Identify first free audit target** — SDC connection or personal contact with an online business
- [ ] **Run first free GEO audit** — single-company mode + PDF report (2-3h)
- [ ] **Renew GitHub PAT** — expires Apr 8 2026 (github.com/settings/tokens)
- [ ] **Delete default pages** from SDC Notion workspace ("Getting Started" + "To Do List")

## April Goals

- [ ] **Deliver free audit + collect feedback** — present PDF to business owner
- [ ] **First paid GEO audit** — 500K KRW target
- [ ] **Write case study (Korean)** — before/after AI citations, client reaction
- [ ] **Post case study to LinkedIn** — bilingual (Korean + English)
- [ ] **AI CPA exam** — maintain daily study rhythm

## Monthly Cadence (May onwards)

- 2-4 paid GEO audits/month (500K-1M KRW each)
- 1 case study/month on LinkedIn
- Upsell: monthly retainer at 1.5M KRW for ongoing optimization
- Government subsidy angle: "AI 기반 디지털 마케팅" for voucher eligibility

---

## SDC 학회

- [x] ~~Confirm 회식 venue~~ — done (2026-03-16)
- [x] ~~KakaoTalk OT message sent~~ — done (2026-03-16)
- [x] ~~SDC Grader v2~~ — COMPLETE (2026-03-14)
- [ ] **After OT:** Assign 10 members to IM/PR/EDU branches + select team leads
- [ ] **Share Notion SDC workspace** with all members

## Portfolio — COMPLETE (maintenance only)

- [x] ~~FinAgent README GEO-optimized~~
- [x] ~~DART MCP README GEO-optimized~~
- [x] ~~GitHub profile README updated~~
- [x] ~~Consulting-emulation README GEO-optimized~~
- [x] ~~AI-project README GEO-optimized~~
- [x] ~~Samsung Forecast README GEO-optimized~~
- [x] ~~SME Diagnostic AI + Lead Intelligence pushed to GitHub~~

## New Projects — BUILT (need live test + deploy)

- [x] ~~SME Diagnostic AI~~ — built (commit dd94cda). Follow-up chat, PDF upload, deck markdown fix.
- [x] ~~Lead Intelligence~~ — built (commit 12eb3b4). 45s timeout, 5 companies, cache fix.
- [ ] **Project A: Streamlit Cloud deploy** — keonhee-sme-diagnostic. Secrets: ANTHROPIC_API_KEY + PERPLEXITY_API_KEY
- [ ] **Project B: Streamlit Cloud reboot** — keonhee-leadintelligence (commit 12eb3b4)

## Job Applications — PAUSED

_BCGX insider: "come back at graduation in '27, I'll help you strategize." Focus on building work experience now._

- [ ] Deloitte Korea AI — 95% fit. Wait for portal.
- [ ] Accenture Song/AI — 93% fit. Monitor portal.
- [ ] McKinsey QuantumBlack — 90% fit. Check when ready.
- [ ] Upstage — 92% fit. Rolling.

## Backlog (do when time permits)

- [ ] FinAgent: Supabase Postgres checkpointer
- [ ] FinAgent: RAGAS evaluation (needs user permission — costs ~15 OpenAI calls)
- [ ] SQL window functions practice
- [ ] Case interview practice (10+ cases via /interview-prep)
- [ ] Context7 MCP install
- [ ] n8n install — DEFERRED until 3+ active clients need workflow automation
- [ ] PitchFi Agent — build after GEO agency is generating revenue
