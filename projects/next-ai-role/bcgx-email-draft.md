# BCGX AI Position — Email Draft

_Direct email to personal contact. Korean. Tone: confident, specific, not formal 자소서 style._
_Fill in: [담당자 이름], [포지션 명칭], [본인 연락처]_

---

**제목:** BCGX AI 포지션 지원 — 김건희 (SKKU 경영학과)

---

안녕하세요, [담당자 이름]님.

SKKU 경영학과 학생 김건희입니다. BCGX AI 포지션에 지원하고 싶어 연락드립니다.

저는 현재 **컨설팅 AI 자동화 시스템을 직접 설계·배포**하고 있습니다. 가장 최근 작업물은 **M&A Due Diligence Suite**로, MBB·Big4 컨설팅 펌의 실무 분석 워크플로우를 자동화한 멀티 에이전트 AI 파이프라인입니다.

- **LangGraph** 기반 Supervisor 에이전트가 쿼리를 분류 후 Text2SQL, RAG, DCF 밸류에이션 에이전트로 자동 라우팅
- **한국 DART 공시 데이터** (삼성전자, SK하이닉스, LG전자) 실시간 연동
- **DCF + EV/EBITDA Comps** 밸류에이션 + **XGBoost 재무 부실 예측 모델** 통합
- **AWS Lambda** (ap-northeast-2) 프로덕션 배포 완료, PowerPoint 자동 생성 포함
- GitHub: github.com/keonhee3337-art/consulting-emulation

이전 작업물인 **FinAgent** (keonhee-finagent.streamlit.app)는 LangGraph + 커스텀 VectorDB + Text2SQL로 구성된 금융 분석 멀티 에이전트 시스템으로, Streamlit Cloud에 배포되어 있습니다. ChromaDB 호환성 문제를 마주했을 때 외부 라이브러리에 의존하지 않고 NumPy 기반 코사인 유사도 VectorDB를 직접 구현한 것이 이 프로젝트의 핵심 기술적 결정이었습니다.

최근에는 동일한 VectorDB를 **LangChain `BaseRetriever`** 인터페이스로도 래핑해, 필요 시 LangChain 체인과도 완전히 호환됩니다.

저는 경영학 배경과 에이전틱 AI 기술 스택을 동시에 갖춘 보기 드문 학생 지원자입니다. BCGX가 클라이언트에 실제로 배포하는 것과 동일한 유형의 AI 시스템 — 멀티 에이전트 파이프라인, 구조적·비구조적 데이터 통합, 컨설팅 등급 아웃풋 — 을 학생 단계에서 이미 만들고 있습니다.

이력서와 GitHub 포트폴리오를 첨부드립니다. 짧게라도 미팅 기회를 주신다면 감사하겠습니다.

감사합니다.

**김건희**
SKKU 경영학과
[본인 연락처]
github.com/keonhee3337-art

---

## 첨부 체크리스트 (보내기 전 확인)

- [ ] CV (.pdf) — `projects/next-ai-role/cv-kearney-ra-v2.docx` 기반으로 impact lines 추가 후 PDF 변환
- [ ] [담당자 이름] 채워넣기
- [ ] [포지션 명칭] 확인 후 제목 수정
- [ ] [본인 연락처] 채워넣기
- [ ] GitHub 링크 클릭해서 모든 repo 접근 가능한지 확인

## CV에 반드시 들어가야 하는 impact lines (이번 세션에 작성)

**M&A Due Diligence Suite**
> LangGraph 멀티 에이전트 M&A 분석 파이프라인. Text2SQL + RAG + DCF 밸류에이션 + XGBoost 부실 예측. AWS Lambda 프로덕션 배포. 한국 공기업 60초 내 분석.

**FinAgent**
> LangGraph 3-노드 에이전트 파이프라인 (RAG → Text2SQL → 합성). 삼성/SK하이닉스 분석 시간 수 시간 → 2분 이내로 단축. Streamlit Cloud 배포.

**SDC 학회 지원자 자동 심사 시스템**
> Gmail → PDF 추출 → Claude Haiku 채점 → Google Sheets 자동 기록. 50+ 지원서 심사 시간 85% 단축 (~4시간 → 30분).

**Claude Code AI 툴링**
> 커스텀 Claude Code second-brain: 11개 skill, 7개 sub-agent, 자동화 hook, Notion/GitHub/DART MCP 서버 연동. 에이전트 오케스트레이션 및 hook 기반 워크플로우 자동화 숙련.
