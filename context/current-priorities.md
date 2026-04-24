# Current Priorities

_Last updated: 2026-04-22 — Life review: Phase 0 YouTube stalled, SDIC infra in progress, 제자훈련 on track_

---

## 1. AI Study — Daily Non-Negotiable

**6 hours/day, Mon–Fri.** Everything else is secondary to this.

- Deepen understanding of agentic AI, MCPs, LangGraph, RAG, Claude Code
- Build fluency so I can teach SDIC members from genuine expertise
- Primary reading surface: NotebookLM notebooks (Hormozi, AI Workflow, Claude & AI Tools, Consulting Interview)

---

## 2. YouTube Business — Primary Revenue Path

**Partner model:** 영범과 파트너십. 공통 코어 인프라 기반 3채널 순차 운영.

### 3 Channels (탁구 제거, Sing It 추가)
| Channel | Topic | Phase | Partner Lead |
|---|---|---|---|
| Sing It 파트너십 | 해외 음악/보컬 영상 번역 (Shorts) | **1 — MVP NOW** | 영범 60% |
| AI 자동화 | AI 툴 데모 + Shorts + Stories | 2 | 건희 60% |
| 한국 정치 롱폼 | 시니어 타겟 정치 뉴스 | 3 | TBD |

### Phase 0 (이번 주 — 계약 확정 + 인프라)
- [ ] Sing It 측 플랫 레이트 협상 (월 50-100만원) — 실패 시 구독당 50%
- [ ] 영범과 내부 계약 서명 (`projects/youtube-biz/config/partner-agreement.md`)
- [ ] YouTube Data API OAuth 셋업 (Sing It 채널용)
- [ ] `python scripts/run_phase0_smoketest.py` 통과
- [ ] 테스트 영상 1개 End-to-End 성공

### Phase 1 (4-6주 — Sing It MVP 검증)
- [ ] 주 5개 Shorts 업로드 (Mon-Fri 자동)
- [ ] 링크 CTR 1% 이상 확인
- [ ] 월 수익 100만원+ 검증 → Go/No-Go

### Logic
Sing It 파트너십 수익 확정 → AI 채널 + 유료 커뮤니티($99/mo) → 정치 롱폼 또는 스케일

### 자동화 코어 (구현 완료)
`projects/youtube-biz/` — Layer 1-5 공통 파이프라인
- Layer 1: 뉴스/트렌딩 수집 (yt-dlp, HN, Naver)
- Layer 2: Claude Haiku 채점 + Sonnet 스크립트 + autoresearch 품질 루프
- Layer 3: yt-dlp 다운로드 + faster-whisper 자막 + ffmpeg 편집
- Layer 4: YouTube Data API + Instagram Graph API (Phase 2)
- Observability: UTM 추적 + Obsidian KPI 리포트

---

## 3. SDIC 학회 — AI Curriculum 🟡 IN PROGRESS

- 12 members (IM 3, PR 4, EDU 3 + 임원 2). 1차 OT held March 20.
- Teaching members AI through real project builds (FinAgent, GEO, SME, etc.)

### This Phase
- [ ] Assign branch leads — IM, PR, EDU team leads
- [ ] Share Notion workspace with all 12 members
- [ ] AI 커리큘럼 1차 초안 — based on SDIC 4주 프로젝트 guide
- [ ] Get 태훈 feedback on 4주 vs 6주 curriculum decision

---

## 4. 제자훈련 — Weekly Cadence 🟢 ACTIVE

매주 토요일 12:00–16:00. Submission to jwj.kr before 12:00.
Daily: 기도 5분 + 성경읽기 5분 (Mon–Sat). Use `/jeja` for all tracking.

---

## BACKLOG (paused — not dead)

These stay in the AI Projects DB for SDIC teaching. Not active revenue priorities.

- **GEO Agency** — all code built. Revive when YouTube channels are live.
- **SME Diagnostic AI** — needs Streamlit Cloud deploy (keonhee-sme-diagnostic)
- **ERP Demo** — needs Streamlit Cloud deploy + Soomgo listing
- **Lead Intelligence** — deployed at keonhee-leadintelligence.streamlit.app

---

_Job search PAUSED. BCGX: "Best CV I've read, come back at graduation ('27)." Strategy: build evidence via YouTube + SDIC teaching → re-engage at graduation._
