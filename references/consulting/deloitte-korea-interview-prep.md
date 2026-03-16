# Deloitte Korea AI & Analytics — Interview Prep

_Fit: 80% — highest of all targets. Priority: apply first._
_Language: Korean. All interview prep Q&A below is in Korean._

---

## Why Deloitte Korea First

| Advantage | Detail |
|-----------|--------|
| 80% fit | FinAgent + SDC grader + DART knowledge = AI implementation track record |
| Korean language | Interviews in Korean — non-Korean candidates have a real disadvantage |
| SKKU credibility | Samsung/LG enterprise clients are SKKU alumni employers; known university |
| Business + AI | Deloitte values business context alongside technical — rare at student level |
| AI implementation, not just AI theory | Deloitte deploys AI for clients; Keonhee has deployed AI for actual use |

---

## Interview Format (Deloitte Korea General Pattern)

1. **서류 심사** — Application review: resume + cover letter
2. **1차 면접** — Group case or individual case interview (비즈니스 케이스)
3. **2차 면접** — Behavioral + technical interview (AI & Analytics: may include SQL/Python questions)
4. **최종 면접** — Culture fit, motivation, career goals

---

## Key Questions — Behavioral (Korean)

### "자기소개를 해주세요"

> 저는 성균관대학교 경영학부 재학 중인 김건희입니다. 지난 6개월간 에이전트 AI 시스템을 직접 설계하고 배포하는 데 집중해왔습니다. 대표적으로 FinAgent는 LangGraph 기반 다중 에이전트 시스템으로 현재 실제로 배포되어 운영 중입니다. 경영학 전공을 통해 비즈니스 문제를 이해하고, AI 기술로 그 문제를 해결하는 것이 제 강점입니다. Deloitte Korea의 AI & Analytics 팀에서 기술과 비즈니스를 연결하는 역할을 하고 싶습니다.

### "왜 Deloitte입니까?"

> Deloitte는 AI를 자문하는 게 아니라 실제로 구현하는 회사입니다. 저는 FinAgent를 통해 금융 분석 자동화 시스템을 end-to-end로 만들었고, SDC 동아리에서는 Claude API 기반 지원서 자동 평가 시스템을 실제 운영했습니다. 이런 구현 경험이 Deloitte의 클라이언트 프로젝트와 직접 연결된다고 생각합니다. 한국 기업들이 AI를 도입하는 중요한 시기에, Deloitte Korea에서 그 과정에 기여하고 싶습니다.

### "가장 어려웠던 기술적 문제와 해결 방법은?"

> FinAgent를 개발하던 중 ChromaDB가 Python 3.14와 호환되지 않는 문제에 부딪혔습니다. 단순히 다른 버전의 Python으로 다운그레이드하는 것은 프로덕션 배포 목표에 맞지 않았습니다. 그래서 외부 의존성 없이 OpenAI 임베딩 + NumPy 코사인 유사도 기반의 커스텀 VectorDB를 직접 구현하기로 결정했습니다. 결과적으로 ChromaDB보다 오히려 더 가볍고 검색 성능도 유사한 솔루션을 만들었고, 제약 조건이 더 나은 아키텍처 결정을 유도했다는 것을 배웠습니다.

### "팀 프로젝트에서의 역할은?"

> SDC 컨설팅 동아리에서 지원서 검토 프로세스 자동화 프로젝트를 주도했습니다. 동아리 임원들이 100개 이상의 지원서를 수동으로 검토하는 데 많은 시간을 쓰고 있었습니다. 제가 Gmail → PDF 추출 → Claude API 자동 평가 → Google Sheets 기록의 워크플로우를 설계하고 구현했습니다. 임원들의 피드백을 반영해 한국어 약점 분석 항목을 추가했고, 최종적으로 검토 시간을 약 70% 단축했습니다.

### "AI의 한계는 무엇이라고 생각하나요?"

> 세 가지를 꼽겠습니다. 첫째, 설명 가능성 — LLM이 왜 그 답을 냈는지 추적하기 어렵고, 이는 컨설팅 클라이언트에게 신뢰를 주기 어렵게 만듭니다. 둘째, 도메인 데이터 의존성 — FinAgent도 처음에는 한국 기업 특화 데이터 없이 일반적인 답만 했습니다. 좋은 RAG 파이프라인과 도메인 데이터가 있어야 실용적입니다. 셋째, 환각 — LLM은 없는 사실을 만들어냅니다. 재무 분석에서 이는 치명적이므로, FinAgent에서는 모든 수치를 SQLite 직접 조회로 검증합니다.

---

## Technical Questions (Deloitte AI & Analytics)

Deloitte 2차 면접에서 기술 질문이 나올 경우:

### Python / 데이터 관련

**Q: pandas DataFrame에서 결측값을 처리하는 방법은?**
> fillna(), dropna(), interpolate() 세 가지 접근이 있습니다. 결측 비율이 낮으면 dropna(), 시계열 데이터면 interpolate(), 중앙값/평균으로 대체할 경우 fillna(df.median())를 사용합니다. FinAgent에서는 DART 재무 데이터의 결측 분기 데이터를 처리할 때 이전 연도 값으로 forward fill을 사용했습니다.

**Q: SQL에서 GROUP BY와 PARTITION BY의 차이는?**
> GROUP BY는 행을 집계해 행 수를 줄입니다. PARTITION BY는 윈도우 함수와 함께 쓰며, 집계 후에도 원래 행 수를 유지합니다. 예를 들어 각 부문별 평균 수익을 행마다 보여주고 싶을 때 PARTITION BY를 씁니다.

**Q: 머신러닝 모델 성능 평가 지표는?**
> 분류: Accuracy, Precision, Recall, F1, AUC-ROC — 불균형 클래스에서는 Accuracy보다 F1이 중요합니다. 회귀: RMSE, MAE, R² — RMSE는 큰 오차를 더 크게 패널티 주고, MAE는 로버스트합니다. FinAgent의 Samsung 주가 예측 프로젝트에서는 RMSE와 MAE를 동시에 보고했습니다.

---

## Case Interview Framework (Deloitte Korea)

Deloitte 케이스는 McKinsey/BCG보다 실무적 — 실제 클라이언트 상황, 구체적 데이터 제공 경우 많음.

### AI 도입 케이스 (Deloitte에서 자주 나옴)

**구조:**
1. **문제 정의** — 클라이언트가 AI로 무엇을 해결하려 하는가?
2. **현재 상태 분석** — 현재 프로세스, 데이터 현황, 조직 준비도
3. **AI 솔루션 설계** — 어떤 AI 접근 (분류, RAG, 에이전트, RPA, 예측 모델)?
4. **데이터 요건** — 학습/추론에 필요한 데이터, 품질 요건
5. **구현 로드맵** — 단계적 구현, MVP 우선
6. **ROI 추정** — 자동화 시간 절감 × 비용, 오류율 감소 등

**Keonhee의 강점:** SDC 그레이더 = 실제 AI 도입 케이스 경험. 이를 컨설팅 언어로 말할 것:
> "저는 SDC 동아리에서 비슷한 프로젝트를 실제로 했습니다. 수동 검토 프로세스를 분석하고, Claude Haiku API를 이용한 자동화 솔루션을 설계했으며, 70% 시간 절감이라는 측정 가능한 결과를 냈습니다."

---

## "Why AI" Narrative for Deloitte

Deloitte는 왜 AI를 공부하게 됐는지 물어볼 가능성 높음:

> 처음에는 삼성전자 주가 예측 프로젝트로 시작했습니다. 그냥 모델을 써보는 수준이었는데, 왜 예측이 틀리는지 이해하려면 데이터 파이프라인부터 모델 구조까지 알아야 했습니다. 그 과정에서 AI가 단순한 도구가 아니라 비즈니스 프로세스를 재설계할 수 있는 능력이라는 것을 깨달았습니다. 경영학 전공자로서 AI가 가져올 비즈니스 변화를 가장 잘 이해하고 전달할 수 있는 사람이 되고 싶었고, 그래서 직접 시스템을 만들었습니다.

---

## Application Checklist

- [ ] Cover letter: `projects/next-ai-role/cover-letter-deloitte.md` ✅
- [ ] Submit via Deloitte Korea careers site: careers.deloitte.com (Korea region)
- [ ] Or contact HR directly to confirm 2026 AI Analytics internship timeline
- [ ] Prepare: 자기소개서 (Korean format, different from 커버레터) — if required
- [ ] Prepare: Portfolio URL — keonhee-finagent.streamlit.app + GitHub links
- [ ] Follow up: 2 weeks after submission if no response
