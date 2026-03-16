# Accenture Song / AI — Interview Prep

_Fit: 78% — Global AI & Data Program Jun–Aug 2026. Apply by April 2026._
_Language: Korean (Accenture Korea HR process); some roles may interview in English_
_Key deadline risk: cohort-based program. Miss April → miss Summer 2026._

---

## Accenture Song vs. Accenture AI

| Practice | Focus | Relevance to Keonhee |
|----------|-------|---------------------|
| **Accenture Song** | GenAI + creative/digital transformation for brands | Full-stack AI (FastAPI + Streamlit + LLM) = client deliverable experience |
| **Accenture AI** | Applied AI for enterprise operations | FinAgent + RAG pipeline architecture = direct fit |
| **Global AI & Data Program** | June–August 2026 cohort — targeted at students | Apply by April 2026 |

**Most relevant:** Global AI & Data Program (cohort-based, structured) OR direct AI intern role in Accenture Korea's Technology/AI practice.

---

## Accenture Interview Format

Unlike BCG/McKinsey, Accenture does **less case-heavy interviewing** at student level:

1. **서류 심사** — Resume + cover letter
2. **온라인 역량 검사** — Cognitive + personality assessment (varies by role)
3. **1차 면접** — Behavioral (STAR format) + some technical questions for AI roles
4. **2차 면접** — Technical depth (AI roles) or group discussion (consulting track)
5. **최종 면접** — HR culture fit, motivation

For AI & Data roles: expect Python/data questions, AI concept questions (not heavy algorithms), and system design discussion.

---

## Key Behavioral Questions (Korean)

### "아센추어를 선택한 이유는?"

> 아센추어 Song과 AI 팀은 GenAI를 클라이언트 제품에 실제로 구현하는 곳입니다. 저는 FinAgent를 통해 LangGraph 기반 다중 에이전트 시스템을 실제 배포까지 경험했습니다. 아센추어가 클라이언트에게 제공하는 AI 솔루션 — 자동화, 개인화, 데이터 파이프라인 — 이 제가 이미 소규모로 해온 일과 같습니다. 2026년에 한국 기업들이 GenAI를 도입하기 시작하는 시점에서 아센추어 코리아의 AI 팀에서 그 구현을 직접 경험하고 싶습니다.

### "가장 자랑스러운 프로젝트는?"

> FinAgent입니다. 단순히 API를 붙인 것이 아니라, LangGraph Router가 자연어 질문을 분석해서 SQL 에이전트, RAG 에이전트, 또는 두 가지 모두를 동적으로 라우팅하는 아키텍처를 설계했습니다. ChromaDB가 Python 3.14와 호환되지 않자 OpenAI 임베딩과 NumPy만으로 커스텀 VectorDB를 직접 구현했습니다. 지금 keonhee-finagent.streamlit.app에 실제 배포되어 있습니다. 문제에 부딪혔을 때 한 단계 더 깊이 들어가는 것 — 이게 제 방식입니다.

### "팀워크 경험을 말해주세요"

> SDC 컨설팅 동아리에서 지원서 검토 프로세스 자동화를 주도했습니다. 동아리 임원들이 100개 이상의 지원서를 수동으로 읽는 데 많은 시간을 쓰고 있었습니다. 저는 Gmail에서 PDF를 자동 추출하고, Claude Haiku API로 평가하고, Google Sheets에 기록하는 시스템을 설계했습니다. 임원들의 피드백을 반영해 한국어 약점 분석, 시간 가용성 메모 등을 추가했고, 최종적으로 검토 시간을 70% 줄였습니다. 기술만 아니라 사용자의 실제 필요를 이해하는 과정이었습니다.

### "AI의 한계와 리스크에 대해 어떻게 생각하나요?"

> 세 가지입니다. 첫째, 설명 가능성 — 특히 금융, 의료 등 규제 산업에서 LLM 결과의 근거를 설명하기 어렵습니다. 아센추어가 클라이언트에 AI 솔루션을 납품할 때 이 점이 가장 큰 도전이 될 것입니다. 둘째, 데이터 의존성 — 좋은 AI는 좋은 데이터에서 나옵니다. FinAgent도 처음에는 한국 기업 특화 데이터 없이 일반적인 답만 했습니다. 셋째, 변화 관리 — AI가 기술적으로 준비되어도 조직이 준비되지 않으면 도입이 실패합니다. 이는 기술 문제가 아니라 컨설팅 문제입니다.

---

## Technical Questions (AI & Data Role)

### "LLM과 기존 ML 모델의 차이는?"

> 전통적인 ML 모델(예: 분류, 회귀)은 특정 태스크에 맞게 훈련됩니다. 좁고 정확하며 설명 가능합니다. LLM은 일반 목적 언어 모델 — 다양한 태스크를 자연어 프롬프트로 수행하지만, 특정 도메인 정확도가 낮을 수 있습니다. 기업 AI에서 최선은 LLM(일반 추론) + 도메인 특화 DB(정확한 데이터)를 결합하는 것 — FinAgent의 Text2SQL + RAG 접근이 바로 이것입니다.

### "RAG가 무엇인지 설명해주세요"

> RAG (Retrieval-Augmented Generation)는 LLM이 답변을 생성하기 전에 관련 문서를 검색해서 컨텍스트로 제공하는 방식입니다. LLM의 두 가지 약점을 보완합니다: 최신 정보 부재(검색으로 최신 데이터 삽입)와 환각(정확한 문서를 기반으로 답변 생성). FinAgent에서는 재무 보고서를 임베딩 벡터로 저장하고, 사용자 질문과 코사인 유사도 비교로 관련 문서를 찾아 GPT-4o에 전달합니다.

### "Python에서 데이터 처리 코드를 어떻게 최적화하나요?"

> 가장 큰 병목은 보통 반복문입니다. pandas vectorized operations이 Python for루프보다 10-100배 빠릅니다. 메모리가 제약될 때는 chunk 단위 처리나 데이터 타입 다운캐스팅(int64 → int32)을 씁니다. 대규모 데이터는 PySpark나 polars가 pandas보다 효율적입니다. FinAgent에서는 임베딩 계산에 NumPy 배치 연산을 써서 단일 문서 임베딩 루프 대비 처리 속도를 높였습니다.

---

## Accenture-Specific Case Style

Accenture 케이스는 BCG/McKinsey보다 덜 formal — **"실제 클라이언트 상황처럼" 진행**:

### GenAI 도입 케이스 (Accenture Song에서 자주 나옴)

**Premise:** 국내 대형 유통사가 고객 서비스에 GenAI 챗봇을 도입하려 한다. 접근 방법은?

**구조화된 답변:**
1. **현황 파악** — 현재 고객 서비스 방식? 인바운드 문의 볼륨? 주요 문의 유형?
2. **AI 솔루션 설계** — FAQ 응답 자동화 vs. 복잡한 민원 에스컬레이션. RAG 기반 FAQ 시스템 + GPT-4o 권장
3. **데이터 요건** — 과거 고객 문의 데이터, 상품 DB, 정책 문서 필요
4. **구현 단계** — Phase 1: 단순 FAQ 자동화 (2개월) → Phase 2: 복잡 민원 AI 보조 (4개월) → Phase 3: 풀 자동화 + 인간 감독
5. **ROI** — 상담원 처리 건수 20% 감소 × 상담원 인건비 = X억원 절감
6. **위험 관리** — 잘못된 정보 제공 시 브랜드 위험. 신뢰도 임계값 설정 + 인간 검토 프로세스

**Keonhee의 엣지:** "저는 SDC에서 실제로 이 구조를 작은 규모로 구현했습니다. Claude Haiku API로 지원서를 자동 평가하는 시스템을 만들었고, 잘못된 평가가 나올 경우 임원이 검토하는 에스컬레이션 레이어를 설계했습니다."

---

## Azure AI-900 — For Accenture (Optional but Differentiating)

Accenture는 Azure를 주요 클라우드 플랫폼으로 사용. Azure AI-900 기초 자격증:

- **학습 자료:** microsoft.com/learn → AI-900 learning path (무료)
- **시험비:** $165 USD (한국 시험 센터)
- **준비 기간:** 1주 (하루 1-2시간)
- **커버리지:**
  - Azure AI 서비스 개요 (Cognitive Services, OpenAI Service)
  - 기계 학습 기초 개념
  - 컴퓨터 비전, NLP, 챗봇 Azure 서비스
  - 책임 있는 AI 원칙

**인터뷰 활용:** "Azure AI 서비스를 이해하고 있으며, AI-900 자격증으로 공식 검증했습니다" — 짧지만 차별화.

**우선순위:** AWS 배포 후, Accenture 지원 전 시간이 있을 때. 필수는 아님.

---

## Application Checklist

- [ ] Cover letter: `projects/next-ai-role/cover-letter-accenture.md` ✅
- [ ] **Apply by April 2026** — Global AI & Data Program Jun–Aug 2026 cohort
- [ ] Check accenture.com/kr → Careers → Internship 2026 for exact deadline
- [ ] Prepare STAR stories: FinAgent + SDC grader + DART MCP
- [ ] Optional: Azure AI-900 cert before interview
- [ ] Accenture Song portfolio: live URL + GitHub = key differentiator
