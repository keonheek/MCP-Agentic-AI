# Next AI Role

_Started: 2026-03-09. Kearney declined._
_Updated: 2026-03-11. Pivoted target from pure AI companies to AI consulting practices._

## Goal

Land an AI-technical role where building AI systems is core — not a side tool. Business Administration + agentic AI technical skills is a rare combination at student level. That's the angle.

Kearney feedback: "tech stack fit." They wanted enterprise consulting tools. Keonhee's actual strength: designing and shipping agentic AI systems end-to-end. Consulting firms with AI practices need exactly that.

---

## Target Role Profile

**What to look for:**
- AI analyst intern / AI developer intern / data science intern at consulting firm's AI practice
- Company that deploys AI to clients (not just advising about AI)
- Korean market preferred — timezone, language, network advantage
- Tech overlap with: Python, LangGraph, RAG, SQL, LLM API, FastAPI, Streamlit

**Avoid:**
- Pure ERP/SAP consulting (Kearney's fit issue — different skill set)
- Pure ML research roles (deep learning theory, publications)
- Roles requiring 3+ years experience

---

## Tier 1 — Primary Targets (Apply Now)

| Company | Practice | Why it fits | Deadline | Status |
|---------|----------|-------------|----------|--------|
| **McKinsey QuantumBlack** | AI analytics arm of McKinsey | Python/ML + structured problem-solving. Rare candidate: business + AI technical at student level. | Rolling | Cover letter ready |
| **BCG Gamma** | BCG's data science + AI unit | LangGraph/RAG + strategy thinking. BCG uses potential model — fit + problem-solving over credentials. | **NOW OPEN** | Cover letter ready |
| **Deloitte Korea AI & Analytics** | Big4 AI implementation | Technical AI + Korean enterprise market knowledge. Interviews in Korean — language advantage. | Rolling | Cover letter ready |
| **Accenture Song / AI** | GenAI + digital transformation | Global AI & Data Program Jun–Aug 2026. Full-stack AI + client delivery model. | Apply by Apr 2026 | Cover letter ready |

## Tier 2 — Apply in Parallel

| Company | Role type | Why it fits | Status |
|---------|-----------|-------------|--------|
| **Upstage** | AI Agent Engineer Intern | Pre-IPO Korean AI company. Agentic AI focus — direct fit. Rolling hire. Email: joinstage@upstage.ai | **Cover letter ready** |
| **Samsung SDS** | AI Solution intern | Enterprise AI for Korean companies. SKKU connection. | Not applied |
| **LG CNS** | AI intern | Large AI/data team, Korean company. | Cover letter ready |
| **Strategy& (PwC) Korea** | AI strategy intern | More strategy than technical — if others are slow. | Not applied |

## Tier 3 — Opportunistic

| Company | Notes | Status |
|---------|-------|--------|
| **Naver Cloud HyperCLOVA X** | March–June 2026 cycle. Check recruit.navercloudcorp.com — may still be open | Check immediately |
| **Wrtn Technologies** | Korean AI startup ($100M ARR). High growth, technical culture. | Not applied |
| **Roland Berger Korea** | Smaller consulting firm, less competition. | Not applied |

---

## Competency Fit Analysis (2026-03-11)

### McKinsey QuantumBlack — 72% fit

**Strengths:**
- Python proficiency (built FinAgent end-to-end)
- Data analysis pipeline experience (Text2SQL, SQLite, pandas)
- Structured problem-solving demonstrated (LangGraph routing logic, VectorDB design decision)
- Business Administration background — can translate technical to business

**Gaps (28%):**
- No ML model training experience (QuantumBlack does ML engineering)
- No cloud platform experience (AWS/GCP/Azure) — QuantumBlack uses cloud-native
- No client-facing project experience
- SQL depth: functional but not advanced (window functions, CTEs — study these)

**How to close gaps:**
- AWS Free Tier: complete one hands-on project (deploy FinAgent or RAG demo to EC2/Lambda)
- SQL: complete Mode Analytics SQL tutorial (advanced section) — 4-6 hours
- No fix for client experience: compensate with SDC consulting club narrative

---

### BCG Gamma — 70% fit

**Strengths:**
- Agentic AI systems (LangGraph multi-agent) — BCG Gamma builds exactly these for clients
- RAG pipeline (real implementation, not theoretical)
- Business + AI combination (rare at student level, BCG potential model rewards this)
- Korean market knowledge (DART, financial data, regulatory context)

**Gaps (30%):**
- No ML model training (BCG Gamma does ML engineering for clients)
- No case interview practice (BCG has one of the hardest case processes)
- No production cloud deployment (Streamlit is demos, not production)

**How to close gaps:**
- Case interview: Practice 10+ cases before applying. Use `/interview-prep` with "full case" mode.
- Cloud: Same as QuantumBlack — one AWS project
- ML: Read one well-explained ML implementation paper (Attention Is All You Need is fine)

---

### Deloitte Korea AI & Analytics — 80% fit

**Strengths:**
- AI implementation experience (FinAgent, RAG demo, SDC grader — all production-grade)
- Korean language (interviews in Korean — advantage over non-Korean candidates)
- Business Administration (Deloitte values business context alongside technical)
- SKKU credibility in Korean enterprise market
- Client simulation experience: SDC grader = automated client deliverable

**Gaps (20%):**
- No RPA/enterprise tools experience (Deloitte does a lot of UiPath, Power Platform)
- Limited cloud exposure
- No Big4 internship or prior corporate experience

**How to close gaps:**
- RPA: 2-hour UiPath trial walkthrough to understand the category (not full mastery)
- Cloud: AWS Free Tier one project — same as above, worth doing regardless

---

### Accenture Song / AI — 78% fit

**Strengths:**
- Full-stack AI (FastAPI backend + Streamlit frontend + LLM API) — Accenture builds these for clients
- Deployed live projects (keonhee-finagent.streamlit.app) — rare for students
- MCP knowledge (Accenture is moving toward MCP-native tooling in 2026)
- Business + technical bridge (Accenture values communication skills alongside AI)

**Gaps (22%):**
- No cloud-native deployment (Accenture uses Azure primarily)
- No enterprise system integration experience
- Global AI program Jun–Aug 2026 — apply by ~Apr 2026

**How to close gaps:**
- Azure: Complete Azure AI-900 fundamentals certification (free study material, 1-week prep)
- Apply to program by April 2026 — don't miss the window

---

## Application Strategy

### Phase 1 — Portfolio visibility (this week)
- [ ] Push FinAgent to public GitHub + run `/geo:github-readme`
- [ ] Push DART MCP Server to public GitHub + run `/geo:github-readme`
- [ ] Update LinkedIn About (draft at `projects/next-ai-role/linkedin-about.md`)

### Phase 2 — Applications (rolling, start now)
- Start with Upstage (cover letter ready → `cover-letter-upstage.md`) and Deloitte Korea
- Use `/apply [company]` for each cover letter — consulting-specific framing
- Use `/interview-prep` with full consulting prep 48 hours before each interview

### Phase 3 — Skills gap closure (parallel with applications)
- SQL advanced: Mode Analytics tutorial (~6 hours)
- AWS: One hands-on project (~1 day)
- Case interviews: 10+ practice cases using `/interview-prep` with "full case" mode

---

## Tracking

Update table above as applications are submitted.
Log interview outcomes in `decisions/log.md`.

**자소서 narrative drafts (초안 — not ready to submit as-is):**

Korean companies use 자기소개서 with company-specific portal prompts. These files have the key content (지원동기, 직무경험, 강점) but need to be restructured to match each company's actual questions.

- `cover-letter-upstage.md` — 자소서 초안 (Upstage — startup, email format may be fine)
- `cover-letter-deloitte.md` — 자소서 초안 (Deloitte Korea AI & Analytics)
- `cover-letter-bcg.md` — 자소서 초안 (BCG Gamma Korea)
- `cover-letter-mckinsey.md` — 자소서 초안 (McKinsey QuantumBlack)
- `cover-letter-accenture.md` — 자소서 초안 (Accenture Song / AI)
- `cover-letter-samsung-sds.md` — 자소서 초안 (Samsung SDS AI Solution 인턴)
- `cover-letter-lgcns.md` — 자소서 초안 (LG CNS AI 인턴)

**To apply:** Go to each company's 채용 portal → get their 자소서 항목 → use `/apply [company]` to adapt the draft content to the actual prompts.
