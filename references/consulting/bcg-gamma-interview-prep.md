# BCG Gamma Korea — Interview Prep

_Fit: 70% — applications NOW OPEN as of March 2026. Apply immediately._
_Key gap: case interviews. BCG has the hardest case process of all 4 targets._
_Language: Korean (1차 면접), potentially English for Gamma-specific roles_

---

## BCG Gamma vs. BCG Consulting

| Aspect | BCG (General) | BCG Gamma |
|--------|--------------|-----------|
| Work | Strategy consulting | AI, data science, advanced analytics for clients |
| Interviews | Case only | Case + technical (data/ML questions may appear) |
| Fit | MBA/undergrad strategic thinkers | Quant + AI + business |
| Keonhee's angle | Business + AI is unusual for standard BCG | Exact fit for Gamma |

---

## BCG Interview Process (Korea, 2026)

1. **서류 전형** — Resume + (sometimes) cover letter
2. **1차 면접 (Case)** — 1-2 case interviews. Standard BCG case format.
3. **2차 면접 (Case + Fit)** — Senior partner case + behavioral questions
4. **(Gamma) Technical screen** — May include Python/SQL/data reasoning questions

**Timeline:** Applications open now → interviews October-January → decisions early winter

---

## BCG Case Interview — Format

BCG cases are **interviewer-led** (unlike McKinsey's candidate-led cases):
- Interviewer gives the case premise
- Asks specific questions at each stage
- You answer each sub-question, then interviewer moves on
- Less open-ended than McKinsey; more guided

**What BCG assesses:**
1. Structured thinking (break the problem into components)
2. Quantitative fluency (math, estimations, data interpretation)
3. Insight quality (not just analysis — what does the data mean?)
4. Communication (clear, confident, not over-explaining)

---

## BCG Case — Step-by-Step Approach

### Opening (30 seconds)
- Listen to the case
- Take notes
- Ask 1-2 clarifying questions maximum (don't over-clarify)
- State your framework structure: "I'd like to approach this by looking at [X, Y, Z]"

### Framework
State a clear MECE framework. For BCG Gamma cases (AI/analytics angle):

**Profitability case:**
```
Revenue side: Volume × Price
  - Volume: market size change? market share change?
  - Price: pricing power? customer mix change?

Cost side: Fixed vs. Variable
  - Fixed: overhead, headcount, facilities
  - Variable: COGS, distribution, tech costs
```

**Market Entry case:**
```
1. Market attractiveness (size, growth, competitive dynamics)
2. Company fit (capabilities, resources, competitive advantage)
3. Entry strategy (build vs. buy vs. partner)
4. Financial viability (revenue model, breakeven)
5. Risks and mitigants
```

**AI Implementation case (Gamma-specific, know cold):**
```
1. Problem diagnosis — what inefficiency/decision is AI solving?
2. Data availability — does the client have the data needed?
3. Solution design — build vs. buy? What model type?
4. Implementation — timeline, change management, integration
5. ROI — cost of implementation vs. value of outcome
6. Risk — bias, regulation, accuracy threshold required
```

### Math
- Always estimate before calculating
- Show your work: "If revenue is ~X and cost is ~Y, margin is roughly Z%"
- Round numbers to make mental math easy
- When you get a result, **interpret it**: "That's a 15% margin drop — that's significant. Let me look at why."

### Recommendation
BCG expects a clear recommendation at the end:
> "Based on my analysis, I'd recommend [specific action] because [2-3 reasons]. The key risk to watch is [X], which could be mitigated by [Y]."

Do not hedge. Be definitive.

---

## Practice Cases — BCG Gamma Angle

These are the case types most likely for Gamma (AI/data science consulting):

### Case 1: AI Implementation for Korean Retail Bank

> **Premise:** A major Korean retail bank wants to use AI to reduce loan default rates. Currently approving loans manually. Default rate is 3.2%, industry average 2.1%. What AI approach would you recommend?

**Good answer structure:**
1. Clarify: What data do they have? (transaction history, credit scores, demographics?) Timeline to implement?
2. Framework: Problem → Data → Model → Implementation → ROI → Risk
3. Analysis: Supervised classification (predict default probability). Input features: credit history, income stability, debt-to-income, transaction patterns. Output: probability score → approve/reject threshold.
4. Risk: Model bias (certain demographics flagged disproportionately) → needs audit. Regulatory: FSS (금융감독원) AI guidelines.
5. ROI: Each avoided default saves average loan value × default rate. With 1M loans/year, even 0.5% improvement = significant.
6. Recommend: Pilot with 10% of loans first, monitor 6 months, then full rollout.

**Keonhee's edge:** "I've built exactly this type of pipeline — Text2SQL to query loan databases, RAG to search compliance documents. The architecture challenge is data freshness, not model complexity."

---

### Case 2: Market Sizing — Korean GenAI Market

> **Premise:** BCG client wants to know the market size for enterprise GenAI consulting services in Korea in 2026.

**Good answer (top-down):**
1. Korean enterprise companies: ~5,000 companies with >100 employees
2. % considering AI adoption: ~40% in 2026 (high due to government AI push, Samsung/LG leading)
3. Average consulting spend on AI per company: 2-5억 KRW/year for initial implementation
4. Addressable market: 5,000 × 40% × 3억 = 6,000억 KRW (~$450M USD)
5. BCG Gamma's addressable share: top-tier consulting gets ~20-30% → 1,200-1,800억 KRW

**Cross-check (bottom-up):** BCG Korea office has ~200 consultants. At 80% utilization, typical project value, the market figure is plausible.

---

## Behavioral Questions (BCG Gamma)

### "왜 BCG Gamma입니까?" (must be specific to Gamma, not just BCG)

> BCG Gamma는 AI를 전략 조언에 그치지 않고 실제로 구현합니다. 저는 FinAgent를 통해 LangGraph 기반 다중 에이전트 금융 분석 시스템을 프로덕션 레벨로 만들었고, DART MCP 서버를 통해 한국 금융 데이터를 AI 도구로 노출했습니다. 이런 구현 경험을 컨설팅 클라이언트 문제에 적용하고 싶습니다. BCG Gamma 서울 오피스는 한국 기업들이 AI 전환을 시작하는 지금 시점에서 가장 임팩트가 큰 자리라고 생각합니다.

### "당신의 가장 큰 강점은?"

> 제약 조건에서 설계 결정을 내리는 능력입니다. ChromaDB가 Python 3.14와 호환되지 않을 때 외부 의존성 없이 커스텀 VectorDB를 구현했습니다. 이는 단순 코딩이 아니라 "왜 이 접근이 가장 좋은가"를 데이터로 정당화하는 과정이었습니다. BCG 컨설턴트도 제약 조건 내에서 최선의 해결책을 찾는 일을 합니다. 같은 사고방식입니다.

### "실패한 경험과 그에서 배운 점은?"

> 처음 FinAgent를 만들 때 라우팅 로직을 단일 에이전트로 구현했습니다. SQL 질문과 RAG 질문을 같은 에이전트가 처리하니 성능이 일관되지 않았습니다. 이유를 분석하니 프롬프트가 너무 많은 역할을 하고 있었습니다. Router → SQL Agent → RAG Agent의 다중 에이전트 아키텍처로 재설계했고, 응답 품질이 크게 향상됐습니다. 복잡한 시스템은 관심사 분리가 핵심이라는 것을 배웠습니다 — 이는 컨설팅 프로젝트 구조화에서도 동일하게 적용됩니다.

---

## Quantitative Prep (BCG Gamma)

BCG 케이스에서 자주 나오는 계산:

```
CAGR: (End / Start)^(1/n) - 1
Break-even: Fixed Cost / (Price - Variable Cost)
Market share: Company Revenue / Total Market Revenue × 100
Margin: (Revenue - Cost) / Revenue × 100
ROI: (Benefit - Cost) / Cost × 100
Payback period: Initial Investment / Annual Benefit
```

**Mental math tricks for Korean market:**
- 한국 인구: 5,100만명
- 한국 GDP: 약 2,000조원 (2조 달러)
- 서울 인구: 약 950만명 (수도권 2,600만명)
- 한국 상장기업: KOSPI 800개, KOSDAQ 1,700개
- 평균 한국 직장인 연봉: 3,500-4,000만원

---

## Case Practice Schedule

| Week | Target | Cases |
|------|--------|-------|
| Week 1 | Understand framework | 3 profitability cases (any source) |
| Week 2 | Quantitative fluency | 3 market sizing + 2 more profitability |
| Week 3 | AI implementation cases | 2 AI cases + 2 market entry |
| Week 4 | Full mock interview | 3 full 45-min mock cases via `/interview-prep` |

**Resources:**
- BCG OneDay@BCG virtual experience (free, bcg.com)
- CaseCoach.me (paid, but has free samples)
- Victor Cheng's Case Interview Secrets — free YouTube
- `/interview-prep` "full case" mode with McKinsey/BCG framing

---

## Application Checklist

- [ ] Cover letter: `projects/next-ai-role/cover-letter-bcg.md` ✅
- [ ] Submit via careers.bcg.com/global/en/locations/korea
- [ ] Check campus career center for SKKU-specific BCG recruiting events
- [ ] Prepare case practice: start immediately (BCG has hardest case process)
- [ ] BCG OneDay@BCG virtual experience — free, do this before applying for context
