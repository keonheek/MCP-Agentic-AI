# Changelog — 2026-03-11

All changes made during this session. Listed in order of completion.

---

## Skills — Evaluation, Improvement, Benchmarking

### Summary table

| Skill | Before | After | Key changes |
|-------|--------|-------|-------------|
| Chat Log Summarizer | C+ | B+ | Auto-persist to decisions/log.md + memory updates |
| Code Researcher | B | A- | Web search integration, version compatibility, stack reference, Korean path aware |
| Database Builder | C | B | Supabase support, SQL schema gen, existing schemas documented |
| Financial Analyst | B+ | A- | Consulting case mode, QuantumBlack/BCG prep framing, benchmarking |
| GEO | B | A- | Consulting-specific GEO (McKinsey, BCG visibility), consulting keywords added |
| Interview Prep | C+ | A | **Major overhaul** — consulting pivot, case framework, STAR stories, 4 target company profiles |
| NotebookLM | B | B+ | Research skill integration, learning path, suggested notebooks |
| Research | A- | A | Deduplication check, consulting query templates, YouTube escalation path |
| Skill Creator | B | B+ | Scoring rubric (5 criteria), Keonhee-specific quality checklist |
| Web Search | C+ | B+ | Search strategy by query type, escalation table, Korean job board references |
| Data Analyst | B | B+ | Advanced SQL patterns (window functions), consulting case framing, QuantumBlack prep |

---

## Best Practices Benchmarked Against

Evaluated against:
1. **Anthropic's skill-creator guidelines** — explain the WHY, under 500 lines, testable
2. **Anthropic's knowledge-work-plugins** — financial-analyst and data-analyst adapted from official source
3. **Consulting firm interview standards** — McKinsey QuantumBlack technical assessment, BCG potential model, Deloitte Korea process
4. **Industry standard for AI agent skills** — context-awareness, output format discipline, escalation logic

Key benchmark findings:
- Previous skills lacked **context-awareness** — they didn't know Keonhee's projects, stack, or targets
- Previous skills had **no escalation logic** — when to use each skill vs. another wasn't clear
- **Interview Prep** was the most outdated — still targeting Kearney (declined). Completely rebuilt for consulting
- **Research** and **Web Search** had no clear escalation path between them — now defined

---

## Job Target Update

**Previous targets:** Upstage, Kakao, Naver, Samsung SAIC (AI-native companies)

**New primary targets (consulting AI practices):**
- McKinsey QuantumBlack — 72% fit
- BCG Gamma — 70% fit
- Deloitte Korea AI & Analytics — 80% fit (highest fit)
- Accenture Song / AI — 78% fit

**Why the pivot:** Business Administration + agentic AI technical skills is rare at student level. That combination is exactly what consulting AI practices need. AI-native companies want ML engineers; consulting AI practices want the business-AI bridge.

**Upstage retained** as Tier 2 — cover letter already drafted.

---

## Competency Gaps Identified (per consulting target)

| Gap | Affects | Fix |
|-----|---------|-----|
| No SQL window functions (LAG, RANK, PARTITION BY) | McKinsey QuantumBlack, BCG Gamma | Mode Analytics SQL tutorial — ~6 hours |
| No cloud platform experience (AWS/Azure) | All 4 | One AWS Free Tier project, or Azure AI-900 cert for Accenture |
| No case interview practice | BCG Gamma (hardest case process) | 10+ practice cases via `/interview-prep` "full case" mode |
| No enterprise tool experience (RPA, Power Platform) | Deloitte Korea | 2-hour UiPath walkthrough — just enough for talking points |

---

## Files Created or Updated

### Skills (all updated)
- `.claude/skills/interview-prep/SKILL.md` — complete rewrite
- `.claude/skills/geo/SKILL.md` — consulting GEO angle added
- `.claude/skills/research/SKILL.md` — deduplication, templates, escalation
- `.claude/skills/web-search/SKILL.md` — search strategy table, escalation logic
- `.claude/skills/database-builder/SKILL.md` — Supabase, SQLite schemas
- `.claude/skills/financial-analyst/SKILL.md` — consulting case mode
- `.claude/skills/data-analyst/SKILL.md` — window functions, consulting framing
- `.claude/skills/chat-log-summarizer/SKILL.md` — auto-persistence
- `.claude/skills/code-researcher/SKILL.md` — stack reference, version checks
- `.claude/skills/skill-creator/SKILL.md` — scoring rubric, quality checklist
- `.claude/skills/notebooklm/SKILL.md` — research integration, learning path

### Commands
- `.claude/commands/apply.md` — consulting-specific cover letter logic per company type

### Projects
- `projects/next-ai-role/README.md` — complete rewrite. Consulting targets, fit analysis (%), gaps, how to close gaps
- `context/current-priorities.md` — updated Priority 1 to reflect consulting pivot + fit percentages

### Cover Letters
- `projects/next-ai-role/cover-letter-upstage.md` — ✅ ready to send (joinstage@upstage.ai)

### Research (from background agents)
- `research/2026-03-11-ai-job-openings.md` — Upstage, Kakao, Naver, Samsung SAIC analysis
- `research/2026-03-11-product-opportunity.md` — PitchFi Agent recommendation (Opportunity #3)

---

## GWS CLI Status

- Installed: `@googleworkspace/cli@0.11.1`
- Binary installer pattern (Rust binary)
- Runs from home dir: `node C:/Users/keonh/AppData/Roaming/npm/node_modules/@googleworkspace/cli/run-gws.js`
- Korean path in MCP Agentic AI dir causes encoding issues — run from `C:/Users/keonh/`
- Auth needed: `gws auth setup` then `gws auth login` (requires Google Cloud project — one-time setup)

---

## NotebookLM Status

- Installed: `notebooklm-py` + `playwright`
- Auth needed (one-time): `python -m notebooklm auth login` (Chromium opens, sign in to Google)
- Skill created at `.claude/skills/notebooklm/SKILL.md`

---

## Pending (still needs human action)

- [ ] **NotebookLM auth** — run `python -m notebooklm auth login` once
- [ ] **GWS CLI auth** — run `gws auth setup` then `gws auth login` (from home dir, not Korean-path dir)
- [ ] **Push FinAgent to public GitHub** — needed before any consulting application (portfolio link)
- [ ] **Apply to Deloitte Korea AI** — `/apply Deloitte Korea AI` — highest fit (80%)
- [ ] **Apply to Accenture Song/AI** — deadline risk: Jun 2026 cohort, apply by Apr
- [ ] **SQL window functions** — Mode Analytics tutorial before McKinsey/BCG applications
- [ ] **Supabase direct connection** — try `db.bnsimxodkdnfxspwntro.supabase.co:5432` (direct, not pooler)

---

## Session 2 — Continued Work (2026-03-11)

### Files Created

| File | Purpose |
|------|---------|
| `references/consulting/sql-practice.md` | SQL window function exercises for McKinsey QB prep. Consulting-context exercises: profitability analysis, cohort retention, market share shift. ROW_NUMBER/RANK/DENSE_RANK, LAG/LEAD, running totals, NTILE, CTE patterns. |
| `references/consulting/aws-quickstart.md` | AWS gap closure guide. Step-by-step: deploy FinAgent FastAPI to Lambda + API Gateway. Includes key AWS concepts to know cold, 1-week learning path, interview talking point. Also covers Azure AI-900 for Accenture. |
| `references/consulting/deloitte-korea-interview-prep.md` | Full Deloitte Korea AI & Analytics interview prep in Korean. Behavioral Q&A (자기소개, 왜 Deloitte, 어려운 기술 문제, 팀 프로젝트 경험, AI 한계). Technical Q&A (pandas, SQL, ML metrics). AI implementation case framework. Application checklist. |
| `projects/next-ai-role/cover-letter-samsung-sds.md` | Samsung SDS AI Solution 인턴 커버레터. Leads with FinAgent + DART knowledge (Korean market specific). SKKU connection highlighted. |
| `references/consulting/bcg-gamma-interview-prep.md` | BCG Gamma full interview prep: case format comparison (BCG vs McKinsey), interviewer-led format, 2 full case examples (AI implementation + market sizing), behavioral Q&A in Korean, quantitative prep, practice schedule. |
| `references/consulting/mckinsey-qb-interview-prep.md` | McKinsey QB interview prep: technical gap table, PySpark crash course, PSG explanation, candidate-led case template, STAR stories in English, technical Python/ML questions. |
| `references/consulting/accenture-interview-prep.md` | Accenture Song/AI interview prep: STAR stories in Korean, GenAI implementation case, Azure AI-900 guide, April 2026 deadline flagged. |
| `projects/next-ai-role/cover-letter-lgcns.md` | LG CNS AI 인턴 커버레터. Leads with FinAgent architecture + DART MCP (LG계열사 데이터 연결 각도). |

### Files Updated

| File | Change |
|------|--------|
| `projects/next-ai-role/README.md` | Tier 1: all 4 status → "Cover letter ready". Tier 2: LG CNS → "Cover letter ready". BCG → "NOW OPEN". Accenture → "Apply by Apr 2026". Cover letters section now lists 7 letters. |
| `tasks/todo.md` | SQL practice + AWS quickstart refs added. Azure AI-900 ref updated. |
| `.claude/skills/interview-prep/SKILL.md` | Reference Files table added at bottom — links to all 7 `references/consulting/` files |
| `decisions/log.md` | 2 new decisions appended: gap closure strategy + company-specific prep rationale |
| `memory/MEMORY.md` | Job Target Pivot section updated: BCG "NOW OPEN" flagged, consulting prep refs noted |

### Files Archived (cleanup)

| From | Reason |
|------|--------|
| `projects/next-ai-role/cover-letters/kakao-brain.md` | Pre-pivot, wrong last name ("Lee" should be "Kim"), Kakao no longer a target |
| `projects/next-ai-role/cover-letters/upstage.md` | Superseded by root-level `cover-letter-upstage.md` |
| `projects/next-ai-role/context/me.md`, `work.md`, `readme.md` | Stale pointer-only files (just said "Reading context/X") |

### Pending (updated)

- Human action required items unchanged — see "Pending" section above
- **Accenture April deadline is the most time-sensitive action after BCG**
- Bug found in archived Kakao letter: last name was "Keonhee Lee" — should be "Keonhee Kim". All current cover letters use correct name.
