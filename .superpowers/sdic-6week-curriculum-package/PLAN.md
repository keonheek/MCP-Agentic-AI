# Plan: SDIC 6-Week AI Curriculum Package

## Scope (locked)
Six deliverables across 4 sequential tasks. All output is Notion pages (member-accessible or private).
4주 is deleted everywhere — not hidden, not toggled off. Deleted.
Every guide includes a WHY before each action block.
Mac AND Windows instructions appear together wherever setup differs.

---

## Task 1: Delete all 4주 content from existing Notion pages

**Pages:** 코스 안내 (3474292aa5f98185ac0ac812d7a32123) + 관리팀 (3474292aa5f981ba88f3e98c7b4963ab)

**Action:**
- 코스 안내: Remove the entire "4주 커리큘럼 (집중 과정)" toggle section. Update intro callout to say "6주" only (remove "4주 (집중) 또는"). Remove the 4주 vs 6주 comparison table. Remove the 4주 row from the 참가비 table ($20 / 1개월 row). Remove 4주 CV bullet from 이력서 라인.
- 관리팀: Remove "4주 vs 6주 vs 공모전 응답 집계" from 1주차 checklist. Update KakaoTalk Post 2 template to remove "4주 or 6주" — replace with just "6주".
- 온보딩 영상 스크립트: Update 파트 5 — 1주차 예고 to remove reference to "4주 or 6주" and lock to 6주 framing.

**Verify:** Re-fetch all three pages and grep for "4주" — zero matches expected.

**Done:** All three existing Notion pages contain no 4주 references.

---

## Task 2: Create Member Step-by-Step Guide

**New Notion page:** "멤버 가이드 — 단계별 프로젝트 실행 매뉴얼"
Parent: SDIC AI parent page (3474292aa5f981e29ddec2dc69eb57bc)

**Action:** Build a self-contained guide that answers "what do I do and WHY" for every step of the 6-week program. Structure:

### Section 0: 사전 준비 (세션 전 필수)
- WHY 박스: "이걸 미리 안 하면 2시간 세션이 설치로 낭비됩니다"
- VS Code 설치 — Mac vs Windows 나란히
- Claude Code 확장 + 로그인
- Python 3.11 설치 (Windows: PATH 체크 강조 / Mac: brew or python.org)
- Git 설치 (Windows: Git for Windows / Mac: xcode-select --install)
- GitHub 계정 생성
- GitHub 저장소 clone (팀 레포 링크 받은 후)

### Section 1: 팀 내 역할과 파일 소유권
- WHY 박스: "4명이 하나의 파일을 건드리면 충돌이 발생합니다. 1인 1파일 원칙이 충돌을 99% 막습니다."
- Pipeline Lead → graph.py
- Data Lead → data.py
- UI Lead → app.py
- Report Lead → report.py

### Sections 2-7: Week 1-6 — 이번 주 내가 할 일
- Each week: WHY 박스 (왜 이 주에 이걸 하는가) + 내 역할별 할 일 + 완료 기준

**Verify:** A member with no prior context can read this page and arrive at session 1 with everything set up.

**Done:** Notion page published and linked from 코스 안내 page.

---

## Task 3: Create Team Collaboration Guide

**New Notion page:** "팀 협업 가이드 — Git + Claude Code 워크플로우"
Parent: SDIC AI parent page

**Action:** Build the guide around 3 pillars:

### Pillar 1: Git 워크플로우 (브랜치 전략)
- WHY 박스: "main에 바로 push하면 팀원 코드가 덮어씌워집니다. 브랜치 = 개인 작업공간"
- 브랜치 명명: `data/이름`, `pipeline/이름`, `ui/이름`, `report/이름`
- 순서: git pull → 내 파일 수정 → git add 내파일만 → git commit → git push → PR → merge
- Mac terminal vs Windows Git Bash 명령어 비교 (동일하지만 터미널 실행 방법 다름)

### Pillar 2: 충돌 예방 규칙 3가지
- WHY 박스: "충돌이 생기면 세션 시간이 트러블슈팅으로 사라집니다"
- 자기 파일만 건드린다 (절대 rule)
- 세션 시작 전 반드시 git pull
- 세션 끝나기 전 반드시 push

### Pillar 3: Claude Code 팀 사용법
- WHY 박스: "Claude Code는 혼자 쓸 때와 팀으로 쓸 때 전략이 다릅니다"
- 각자 로컬 Claude Code에서 작업 — 서로 세션 공유 X
- @파일명으로 내 파일만 참조
- CLAUDE.md는 팀 공통 — 변경 시 PR 필수
- /clear 언제 써야 하는지

### Pillar 4: Mac/Windows 환경 차이 대응
- 가상환경 활성화: Mac `source venv/bin/activate` / Windows `venv\Scripts\activate`
- 줄바꿈 설정: .gitattributes로 LF 고정 (Mac/Windows 혼용 충돌 방지)
- Python 명령어: Mac `python3` / Windows `python`

**Verify:** Member can follow this guide end-to-end without asking Keonhee a question.

**Done:** Notion page published, linked from both 코스 안내 and 멤버 가이드.

---

## Task 4: Create Facilitator Package (Keonhee's private guide)

**New Notion page:** "회장 진행 가이드 — 6주 세션 운영 스크립트" (내부 공개 금지)
Parent: SDIC AI parent page

**Action:** 6-week × 2-hour session run-of-show. Each week has:
- 세션 전 준비 (5분): what Keonhee prepares before members arrive
- 타임라인: minute-by-minute breakdown
- 전환 멘트: exact phrases to say at each transition
- 막힘 대응: top 3 failure modes and how to handle them

**Week structure (2 hours):**
- 0:00-0:10 — 오프닝: 지난주 회고 + 이번 주 목표 발표
- 0:10-0:20 — 개념 설명: 이번 주 WHY (짧게, 시각자료 없이 말로만)
- 0:20-0:50 — 팀 실행 세션 (Keonhee walks the room, 멘토가 팀 지원)
- 0:50-1:30 — 딥 빌드 (각 팀 자기 파일 작업, 멘토 1:1 지원)
- 1:30-1:50 — Git push + 동작 확인 (반드시 로컬 실행 확인)
- 1:50-2:00 — 다음 주 예고 + 질문

**Per-week content:**
- Week 1: 온보딩 + CLAUDE.md + 첫 commit →막힘 대응: Python PATH 오류, clone 실패
- Week 2: DART ETL + LangGraph 2-node → 막힘 대응: DART API 키 오류, SQLite not found
- Week 3: Supervisor 멀티에이전트 → 막힘 대응: agent import 오류, handoff 미작동
- Week 4: RAG + Text2SQL + PDF → 막힘 대응: OpenAI embeddings 비용 초과, fpdf2 인코딩
- Week 5: Plotly + LLM evaluator → 막힘 대응: Plotly not rendering, judge 점수 편향
- Week 6: 채팅 Q&A + Streamlit Cloud 배포 + 데모 → 막힘 대응: deployment secrets, demo 시간 초과

**Also includes:** Updated video script section — 파트 1의 WHY를 강화 (교수 피드백 반영), 6주 전용 framing

**Verify:** Keonhee can run any week's session using only this guide, zero prep time.

**Done:** Notion page created, private (Keonhee only). All 6 weeks have timestamped agendas.

---

## Verification

| Task | Done Criteria | Result |
|------|--------------|--------|
| Task 1 | Re-fetch Notion pages, grep "4주" → 0 hits | pending |
| Task 2 | Member guide page exists, linked from 코스 안내 | pending |
| Task 3 | Collaboration guide exists, Mac+Windows sections present | pending |
| Task 4 | Facilitator guide exists, 6 timestamped session agendas | pending |
