# Keonhee — Portable Study Guide
_Generated 2026-03-12 | Take this file anywhere_

---

## WHAT TO DO RIGHT NOW (priority order)

1. **BCG Gamma** — applications are OPEN NOW. Go to careers.bcg.com → Korea → apply. Use 자소서 content below.
2. **Deloitte Korea AI** — 80% fit (your highest). careers.deloitte.com (Korea region).
3. **Accenture Song/AI** — deadline ~April 2026. accenture.com/kr → Careers.
4. **LinkedIn About** — copy the bilingual bio below and paste it.
5. **SQL window functions** — practice section is below. Do Mode Analytics tutorial.

---

## YOUR STORY (memorize these — use in every interview)

### The Three Projects (STAR format)

**FinAgent** — Lead with this for every tech question
> 다중 에이전트 금융 분석 시스템을 직접 설계하고 배포했습니다. LangGraph Router가 자연어 질문을 분석해 SQL 에이전트, RAG 에이전트, 또는 두 가지 모두를 동적으로 라우팅합니다. ChromaDB가 Python 3.14와 호환되지 않을 때 외부 의존성 없이 커스텀 VectorDB를 구현했습니다. 현재 keonhee-finagent.streamlit.app에 배포되어 있습니다.

**SDC Grader** — Lead with this for process automation questions
> SDC 컨설팅 동아리에서 지원서 100개 이상을 수동으로 검토하는 프로세스를 자동화했습니다. Gmail → PDF 추출 → Claude Haiku API 자동 평가 → Google Sheets 기록 워크플로우를 설계하고 구현했습니다. 검토 시간을 약 70% 단축했고, 현재 15분마다 자동 실행 중입니다.

**DART MCP Server** — Lead with this for Korean market / data questions
> 한국 금융감독원 DART 공시 데이터를 AI 도구로 노출하는 MCP 서버를 직접 개발했습니다. 2,500개 이상 상장기업의 재무제표, 공시, 기업정보를 Claude Code에서 직접 조회할 수 있습니다. Python + FastAPI 기반, Claude Code MCP 프로토콜 구현.

### Why consulting (not ML lab)?
> 저는 AI 시스템을 만들 수 있고, 그 시스템이 비즈니스에 미치는 영향도 설명할 수 있습니다. 대부분의 AI 엔지니어는 비즈니스를 모르고, 대부분의 컨설턴트는 시스템을 만들지 못합니다. 컨설팅 AI 팀이 제가 가장 임팩트를 낼 수 있는 곳입니다.

### The ChromaDB decision (use for "technical decision under uncertainty")
> **Situation:** FinAgent에 벡터 DB가 필요했는데 ChromaDB가 Python 3.14와 호환되지 않았습니다.
> **Task:** 배포 일정을 지키면서 대안을 찾아야 했습니다.
> **Action:** ChromaDB가 내부적으로 하는 일(코사인 유사도 계산)을 분석하고, OpenAI 임베딩 + NumPy로 200줄 커스텀 구현을 만들었습니다. Pinecone과 성능 비교 후 유사한 결과를 확인했습니다.
> **Result:** 외부 의존성 없이 제때 배포. 이 결정이 지금 GitHub README에서 가장 많이 언급되는 기술적 판단입니다.

---

## 자소서 CONTENT BY COMPANY

### BCG Gamma

**지원동기**
> BCG Gamma는 AI를 전략 조언에 그치지 않고 실제로 구현합니다. 저는 FinAgent를 통해 LangGraph 기반 다중 에이전트 금융 분석 시스템을 프로덕션 레벨로 만들었고, DART MCP 서버를 통해 한국 금융 데이터를 AI 도구로 노출했습니다. 이런 구현 경험을 컨설팅 클라이언트 문제에 적용하고 싶습니다. BCG Gamma 서울 오피스는 한국 기업들이 AI 전환을 시작하는 지금 시점에서 가장 임팩트가 큰 자리라고 생각합니다.

**강점**
> 제약 조건에서 설계 결정을 내리는 능력입니다. ChromaDB가 Python 3.14와 호환되지 않을 때 외부 의존성 없이 커스텀 VectorDB를 구현했습니다. 이는 단순 코딩이 아니라 "왜 이 접근이 가장 좋은가"를 데이터로 정당화하는 과정이었습니다. BCG 컨설턴트도 제약 조건 내에서 최선의 해결책을 찾는 일을 합니다.

**실패 경험**
> 처음 FinAgent를 만들 때 라우팅 로직을 단일 에이전트로 구현했습니다. SQL 질문과 RAG 질문을 같은 에이전트가 처리하니 성능이 일관되지 않았습니다. Router → SQL Agent → RAG Agent의 다중 에이전트 아키텍처로 재설계했고, 응답 품질이 크게 향상됐습니다. 복잡한 시스템은 관심사 분리가 핵심이라는 것을 배웠습니다.

---

### Deloitte Korea AI & Analytics

**자기소개**
> 저는 성균관대학교 경영학부 재학 중인 김건희입니다. 지난 6개월간 에이전트 AI 시스템을 직접 설계하고 배포하는 데 집중해왔습니다. FinAgent는 LangGraph 기반 다중 에이전트 시스템으로 현재 실제로 배포되어 운영 중입니다. 경영학 전공을 통해 비즈니스 문제를 이해하고, AI 기술로 그 문제를 해결하는 것이 제 강점입니다.

**지원동기**
> Deloitte는 AI를 자문하는 게 아니라 실제로 구현하는 회사입니다. 저는 SDC 동아리에서 Claude API 기반 지원서 자동 평가 시스템을 실제 운영했습니다. 이런 구현 경험이 Deloitte의 클라이언트 프로젝트와 직접 연결된다고 생각합니다.

**어려웠던 기술적 문제**
> FinAgent 개발 중 ChromaDB가 Python 3.14와 호환되지 않는 문제에 부딪혔습니다. 외부 의존성 없이 OpenAI 임베딩 + NumPy 코사인 유사도 기반의 커스텀 VectorDB를 직접 구현했습니다. 결과적으로 ChromaDB보다 더 가볍고 검색 성능도 유사한 솔루션을 만들었습니다.

**팀 프로젝트**
> SDC 컨설팅 동아리에서 지원서 검토 프로세스 자동화를 주도했습니다. Gmail → PDF 추출 → Claude API 자동 평가 → Google Sheets 기록 워크플로우를 설계하고 구현했습니다. 임원들의 피드백을 반영해 한국어 약점 분석 항목을 추가했고, 검토 시간을 약 70% 단축했습니다.

**AI의 한계**
> 세 가지입니다. 첫째, 설명 가능성 — LLM 결과의 근거를 추적하기 어렵습니다. 둘째, 도메인 데이터 의존성 — 좋은 AI는 좋은 데이터에서 나옵니다. 셋째, 환각 — FinAgent에서는 모든 수치를 SQLite 직접 조회로 검증합니다.

---

### Accenture Song / AI

**지원동기**
> 아센추어 Song과 AI 팀은 GenAI를 클라이언트 제품에 실제로 구현하는 곳입니다. 저는 FinAgent를 통해 LangGraph 기반 다중 에이전트 시스템을 실제 배포까지 경험했습니다. 아센추어가 클라이언트에게 제공하는 AI 솔루션이 제가 이미 소규모로 해온 일과 같습니다. 2026년에 한국 기업들이 GenAI를 도입하기 시작하는 시점에서 구현을 직접 경험하고 싶습니다.

**가장 자랑스러운 프로젝트**
> FinAgent입니다. LangGraph Router가 자연어 질문을 분석해서 SQL 에이전트, RAG 에이전트, 또는 두 가지 모두를 동적으로 라우팅합니다. ChromaDB 호환성 문제를 만났을 때 한 단계 더 깊이 들어가 커스텀 VectorDB를 구현했습니다. 현재 keonhee-finagent.streamlit.app에 실제 배포되어 있습니다.

---

### McKinsey QuantumBlack (English)

**Tell me about yourself**
> I'm Keonhee Kim, studying Business Administration at Sungkyunkwan University in Korea. Over the past year, I've been building production agentic AI systems — not demos, but live deployed applications. My main project is FinAgent: a multi-agent financial analysis system using LangGraph, Text2SQL, and a custom vector database I built from scratch when standard tools weren't compatible with my environment. I'm one of the rare students who combines business administration training with hands-on AI engineering experience. I'm targeting QuantumBlack because it's where those two things come together at the highest level.

**Why QuantumBlack?**
> QuantumBlack works at the intersection of AI engineering and client business outcomes. I've built systems that would be considered QB deliverables: multi-agent pipelines, RAG systems, custom data tooling. But I've also studied how business strategy works. Most AI engineers can't explain what their system means for client operations. Most business consultants can't build the system. I can do both.

**Technical decision under uncertainty**
> Situation: FinAgent needed a vector database. ChromaDB was the standard choice but incompatible with Python 3.14.
> Action: I analyzed what ChromaDB was actually doing — cosine similarity over high-dimensional vectors. Built a custom implementation in ~200 lines using OpenAI embeddings and NumPy. Benchmarked it against Pinecone on a 100-document corpus and confirmed comparable results.
> Result: Deployed on time, no external dependency. Now one of the most-discussed parts of the GitHub README.

---

## LINKEDIN ABOUT (paste this)

**Korean:**
> 성균관대학교 경영학부 재학 중이며, 에이전트 AI 시스템을 직접 설계하고 배포하는 데 집중하고 있습니다.
>
> **주요 프로젝트:**
> • FinAgent — LangGraph + RAG + Text2SQL 기반 다중 에이전트 금융 분석 시스템 (배포 완료: keonhee-finagent.streamlit.app)
> • DART MCP Server — 한국 금융 공시 데이터를 AI 도구로 노출하는 커스텀 MCP 서버
> • SDC 자동화 — Gmail → Claude AI → Google Sheets 지원서 자동 평가 파이프라인
>
> **기술 스택:** LangGraph, RAG, FastAPI, Streamlit, OpenAI API, Claude API, SQLite, Python
>
> McKinsey QuantumBlack, BCG Gamma, Deloitte Korea AI, Accenture Song/AI 포지션에 관심 있습니다.

**English:**
> SKKU Business Administration student building production-grade agentic AI systems.
>
> **Projects:** FinAgent (LangGraph multi-agent financial analysis, live at keonhee-finagent.streamlit.app) · DART MCP Server (Korean financial disclosure data via custom MCP) · SDC Auto-Grader (Gmail → Claude Haiku → Google Sheets pipeline)
>
> **Stack:** LangGraph · RAG · FastAPI · Streamlit · OpenAI API · Claude API · Python
>
> Targeting AI consulting roles at McKinsey QuantumBlack, BCG Gamma, Deloitte Korea AI, Accenture Song/AI.

---

## SQL WINDOW FUNCTIONS (study this)

### Core syntax
```sql
function_name() OVER (
    PARTITION BY column   -- like GROUP BY but keeps all rows
    ORDER BY column
)
```

### The 5 you must know cold

**ROW_NUMBER / RANK / DENSE_RANK**
```sql
RANK() OVER (PARTITION BY sector ORDER BY revenue DESC)
-- RANK: gaps after ties (1,1,3)
-- DENSE_RANK: no gaps (1,1,2)
-- ROW_NUMBER: always unique (1,2,3)
```

**LAG / LEAD — year-over-year analysis**
```sql
SELECT
    company, year, revenue,
    LAG(revenue) OVER (PARTITION BY company ORDER BY year) AS prev_year,
    revenue - LAG(revenue) OVER (PARTITION BY company ORDER BY year) AS yoy_change
FROM financials;
```

**Running total / moving average**
```sql
SUM(revenue) OVER (PARTITION BY company ORDER BY year) AS cumulative
AVG(revenue) OVER (
    PARTITION BY company ORDER BY year
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
) AS rolling_3yr_avg
```

**NTILE — quartile bucketing**
```sql
NTILE(4) OVER (ORDER BY revenue DESC) AS quartile
```

**KEY INTERVIEW POINT:** GROUP BY collapses rows. PARTITION BY in a window function keeps all rows and computes over a partition. Know this cold.

### Practice: profitability diagnosis query
```sql
WITH margin_calc AS (
    SELECT business_unit, year,
        ROUND(100.0 * (revenue - cost) / revenue, 2) AS margin_pct
    FROM financials
),
margin_change AS (
    SELECT *,
        LAG(margin_pct) OVER (PARTITION BY business_unit ORDER BY year) AS prev_margin,
        margin_pct - LAG(margin_pct) OVER (PARTITION BY business_unit ORDER BY year) AS delta
    FROM margin_calc
)
SELECT * FROM margin_change WHERE delta IS NOT NULL ORDER BY delta ASC;
```

**Resources:**
- mode.com/sql-tutorial (free, do the advanced section — ~6 hours)
- platform.stratascratch.com (real McKinsey/BCG SQL questions)
- LeetCode SQL: problems 177, 181, 184, 197

---

## BCG CASE INTERVIEW (practice this)

### BCG format: interviewer-led (they guide you)

**Opening (30 seconds):**
1. Listen, take notes
2. Ask 1-2 clarifying questions max
3. State your framework: "I'd like to approach this by looking at [X, Y, Z]"

### Profitability case framework
```
Revenue: Volume × Price
  - Volume: market size change? market share change?
  - Price: pricing power? customer mix change?

Cost: Fixed vs. Variable
  - Fixed: overhead, headcount, facilities
  - Variable: COGS, distribution, tech
```

### AI Implementation case framework (BCG Gamma specific — know this cold)
```
1. Problem: what inefficiency is AI solving?
2. Data: does the client have the data?
3. Solution: build vs. buy? what model type?
4. Implementation: timeline, change management, integration
5. ROI: cost vs. value
6. Risk: bias, regulation, accuracy threshold
```

### Closing recommendation (always definitive, never hedge)
> "Based on my analysis, I recommend [specific action] because [2-3 reasons]. The key risk is [X], which I'd mitigate by [Y]."

### Market sizing — Korean benchmarks (memorize)
- 한국 인구: 5,100만명
- 한국 GDP: 약 2,000조원
- 서울 인구: 950만명 (수도권 2,600만명)
- KOSPI: ~800개 상장사, KOSDAQ: ~1,700개
- 한국 직장인 평균 연봉: 3,500-4,000만원
- 한국 중소기업: 800만개 (전체 기업의 99.9%)

### Math you need fast
```
CAGR = (End/Start)^(1/n) - 1
Break-even = Fixed Cost / (Price - Variable Cost)
Market share = Company Revenue / Total Market × 100
Margin = (Revenue - Cost) / Revenue × 100
ROI = (Benefit - Cost) / Cost × 100
```

---

## McKINSEY CASE FORMAT (candidate-led — harder than BCG)

You drive the entire structure. Interviewer gives the case, you ask for what you need.

**Template:**
1. "May I ask a clarifying question — [question]?"
2. "I'd like to take a moment to structure my approach." *(30 seconds of silence is fine)*
3. "To diagnose [problem], I'd look at [Area 1], [Area 2], [Area 3]. I'll start with [Area 1]. Does that make sense?"
4. "To test this hypothesis, I'd need to see [data]. Do you have that?"
5. After each section: "So from this analysis, [finding]. This suggests [implication]. Let me move to [next area]."
6. Final: "My recommendation is [specific action]. Primary driver: [finding]. Main risk: [X], mitigated by [Y]. Next step: [immediate action]."

---

## YOUR FIT SCORES (reference)

| Company | Fit | Key strength | Gap |
|---------|-----|--------------|-----|
| Deloitte Korea AI | 80% | FinAgent + SDC grader + Korean language | No RPA experience |
| Accenture Song/AI | 78% | Full-stack AI + MCP knowledge | No Azure/cloud deployment |
| McKinsey QuantumBlack | 72% | Python + structured problem-solving | No PySpark/cloud, SQL depth |
| BCG Gamma | 70% | LangGraph/RAG + business background | No case practice, no cloud |

**Gap closure (do in this order):**
1. SQL window functions — Mode Analytics, ~6 hours
2. 10+ case interviews — practice with a friend using BCG case framework above
3. AWS Lambda deploy — deploy FinAgent FastAPI endpoint, ~1 day
4. PySpark basics — conceptual only, ~2 hours reading

---

## TECHNICAL QUESTIONS TO PREPARE

**"What is RAG?"**
> RAG는 LLM이 답변을 생성하기 전에 관련 문서를 검색해서 컨텍스트로 제공하는 방식입니다. LLM의 최신 정보 부재와 환각 문제를 보완합니다. FinAgent에서는 재무 보고서를 임베딩 벡터로 저장하고, 사용자 질문과 코사인 유사도 비교로 관련 문서를 찾아 GPT-4o에 전달합니다.

**"GROUP BY vs PARTITION BY?"**
> GROUP BY는 행을 집계해 행 수를 줄입니다. PARTITION BY는 윈도우 함수와 함께 쓰며, 집계 후에도 원래 행 수를 유지합니다.

**"Precision vs Recall?"**
> Precision: 내가 양성이라고 예측한 것 중 실제 양성 비율. Recall: 실제 양성 중 내가 찾아낸 비율.
> 사기 탐지: Recall 중요(놓치면 안 됨). 스팸 필터: Precision 중요(정상 메일을 스팸으로 분류하면 안 됨).

**"LLM vs traditional ML?"**
> 전통 ML은 특정 태스크에 맞게 훈련 — 좁고 정확하고 설명 가능. LLM은 일반 목적 언어 모델 — 다양한 태스크를 자연어로 수행하지만 도메인 정확도가 낮을 수 있음. 최선은 둘을 결합: LLM(추론) + 도메인 DB(정확한 데이터) = FinAgent의 RAG + Text2SQL 방식.

---

## PENDING ACTIONS WHEN YOU'RE BACK

| Task | Time | Details |
|------|------|---------|
| Submit BCG Gamma | 15 min | careers.bcg.com/global/en/locations/korea |
| Submit Deloitte | 15 min | careers.deloitte.com (Korea) |
| LinkedIn About | 5 min | Paste bilingual bio above |
| Supabase restore | 2 min | supabase.com/dashboard → Restore project |
| NotebookLM auth | 5 min | `python -m notebooklm auth login` in terminal |
| GitHub PAT renewal | 5 min | github.com/settings/tokens (expires Apr 8) |
| Redeploy FinAgent | 2 min | Push already done. Check Streamlit auto-deployed. |

---

_This file is self-contained. No internet required to study from it._
