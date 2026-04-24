# 라라스윗 GEO 최적화 구현 체크리스트
# GEO Implementation Checklist — 라라스윗
생성일 / Generated: 2026-03-22

---

## P0 - AI 접근 차단 해결 (즉시)
## P0 - Fix AI Access Blocks (Immediate)
*AI 크롤러가 사이트에 접근할 수 없으면 모든 최적화가 무의미합니다*
*If AI crawlers cannot access your site, all optimization is pointless*

- [ ] **llms.txt 생성** — AI 시스템에 콘텐츠 사용 권한 명시
> Create llms.txt — declare content permissions for LLM systems
  - 파일: `llms.txt` (첨부됨 / attached)
  - 위치: 웹사이트 루트 디렉토리 / Website root directory
  - 예상 시간 / Estimated time: 5분 / 5 min

## P1 - 빠른 개선 (1일)
## P1 - Quick Wins (1 Day)
*즉시 효과를 볼 수 있는 구조화된 데이터 추가*
*Add structured data for immediate AI readability gains*

- [ ] **Organization 스키마 추가** — 회사 정보를 AI가 읽을 수 있는 형태로 제공
> Add Organization Schema — provide company info in AI-readable JSON-LD format
  - 파일: `organization_schema.json` (첨부됨 / attached)
  - [TODO] 안의 정보를 실제 데이터로 교체 / Replace [TODO] fields with real data
  - 홈페이지 `<head>` 태그 안에 삽입 / Insert inside `<head>` tag on homepage
  - 예상 시간 / Estimated time: 30분 / 30 min

- [ ] **FAQPage 스키마 추가** — 자주 묻는 질문을 AI가 인용할 수 있게 구조화
> Add FAQPage Schema — structure Q&A so AI can cite your answers directly
  - 파일: `faqpage_schema.json` (첨부됨 / attached)
  - Q&A 내용을 실제 비즈니스에 맞게 수정 / Customize Q&A for your business
  - 예상 시간 / Estimated time: 1시간 / 1 hr

- [ ] **메타 태그 최적화** — title, description에 핵심 키워드 포함
> Optimize meta tags — include target keywords in title and meta description
  - 예상 시간 / Estimated time: 1-2시간 / 1-2 hrs

## P2 - 콘텐츠 개선 (1주)
## P2 - Content Improvements (1 Week)
*AI가 인용할 만한 콘텐츠 구조로 전환*
*Restructure content so AI is likely to quote it*

- [ ] **FAQ 섹션 작성** — 고객이 AI에 물어볼 법한 질문 10-15개와 상세 답변
> Write FAQ section — 10-15 questions customers ask AI, with detailed answers
  - 질문은 자연어 형태로 작성 / Write questions in natural language
  - 예상 시간 / Estimated time: 3-4시간 / 3-4 hrs

- [ ] **회사 소개 페이지 강화** — 300자 이상, 구체적 수치와 실적 포함
> Strengthen About page — 300+ chars, include specific metrics and achievements
  - 예상 시간 / Estimated time: 2시간 / 2 hrs

## P3 - 지속적 관리 (월간)
## P3 - Ongoing Maintenance (Monthly)
*AI 가시성을 유지하고 개선하기 위한 월간 활동*
*Monthly activities to maintain and improve AI visibility*

- [ ] **월간 SoV 추적** — AI가 귀사를 얼마나 추천하는지 모니터링
> Monthly SoV tracking — monitor how often AI recommends you
  - 파일: `sov_tracking_queries.txt` (첨부됨 / attached)
  - 매월 1회 ChatGPT + Perplexity에서 쿼리 실행 / Run queries monthly

- [ ] **콘텐츠 업데이트** — 분기별 1회 이상 주요 페이지 업데이트
> Content updates — update key pages at least once per quarter

---

*이 체크리스트는 GEO 진단 결과를 기반으로 자동 생성되었습니다.*
*This checklist was auto-generated from GEO audit results.*
*생성 도구 / Tool: GEO Audit Tool | 생성일 / Date: 2026-03-22*