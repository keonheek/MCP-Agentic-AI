# Plan: GEO Service — Practice Audit + Value Proposition + Client Moat

## Context

The GEO audit tool is built and tested on 3 companies (솔브레인, 스타벅스코리아, 현대모비스). Keonhee asks three critical questions:
1. Run a practice audit on a new company and show the report
2. What deliverables would actually make clients pay?
3. Why can't they do it themselves — why do they need me?

This plan answers all three and defines the execution path to first revenue.

---

## Part 1: Practice Audit — 에이스침대 (Ace Bed Korea)

**Why this company:** Korean mid-market mattress manufacturer. Consumer-facing product everyone understands. Likely low GEO score (traditional manufacturer, no AI optimization). Strong "before/after" potential — when someone asks Perplexity "best Korean mattress brand," foreign brands (Simmons, Sealy, Tempur) likely get cited instead.

**How to run:**
```bash
cd "C:/Users/keonh/Dev/MCP_Agentic_AI/projects/geo-agency"
streamlit run app.py
# Enter: 에이스침대 / 침대 매트리스
```

**Alternatives if 에이스침대 fails:** 매일유업, 오뚜기, 한샘

**Verify:**
- PDF appears in `projects/geo-agency/reports/`
- All 7 dimensions have non-zero scores
- Before text is a real Perplexity response
- After text is a plausible improved AI response

---

## Part 2: Six Gaps to Fix Before Client Delivery

### Gap 1: Recommendations are hardcoded (CRITICAL — fix before ANY client)

**Problem:** `app.py` lines 108-112 produce the same 3 recommendations for every company. A company scoring 30/30 on crawler access still gets told to fix robots.txt.

**Fix:** Create `generate_dynamic_recommendations(breakdown: dict) -> list[str]` in `geo_audit.py`. Maps low-scoring dimensions to specific recs:
- `llms_txt == 0` → "웹사이트 루트에 llms.txt 파일 생성 (AI 시스템 접근 허용 표준)"
- `schema_org < 10` → "홈페이지에 Organization JSON-LD 구조화 데이터 추가"
- `citability < 20` → "주요 페이지에 50단어 이상의 구체적 텍스트 블록 추가"
- `korean_presence < 10` → "네이버 비즈니스 프로필 및 카카오맵 등록"
- `crawler_access < 20` → "robots.txt에 GPTBot, ClaudeBot, PerplexityBot 허용"
- `share_of_voice < 5` → "업계 키워드에서 AI 인용 빈도를 높이기 위한 콘텐츠 전략 필요"

**Status:** ✅ COMPLETE — `generate_dynamic_recommendations()` implemented in `geo_audit.py`

### Gap 2: Streamlit UI shows 3 of 7 dimensions

**Problem:** Only citability, crawler, brand shown as `st.metric()`. Schema, llms, korean_presence, sov are computed but invisible.

**Fix:** Add second row of 4 columns in `app.py` after line 90.

**Status:** ✅ COMPLETE — all 7 dimensions visible in UI

### Gap 3: PDF has no competitive comparison

**Problem:** `sov_competitors` list exists in audit dict but is never shown in PDF or UI.

**Fix:** Add "Competitive Landscape" section to page 2 of `geo_report_pdf.py`.

**Status:** ✅ COMPLETE

### Gap 4: Projected score is a naive +30

**Problem:** `geo_report_pdf.py` projects same score improvement for every company.

**Fix:** Calculate based on recoverable points from low-scoring dimensions.

**Status:** ✅ COMPLETE

### Gap 5: No implementation roadmap in PDF

**Status:** ✅ COMPLETE — Phase 1/2/3 roadmap added

### Gap 6: No content rewrite examples

**Status:** Deferred — Tier 2 feature only

---

## Part 3: Three Service Tiers

### Tier 1: GEO 진단 리포트 — 300K-500K KRW

**Deliverables:**
1. 2-page PDF audit report (dimension scores + visual bars)
2. Before/After AI visibility proof (real Perplexity query vs. simulated improvement)
3. 3-5 company-specific recommendations (dynamically generated)
4. Competitor names from Share of Voice analysis
5. 15-minute video call or KakaoTalk voice explaining results

**Your time:** 1-2 hours | **What makes them pay:** The Before/After proof. Seeing "ChatGPT doesn't mention you" is visceral.

### Tier 2: GEO 구현 패키지 — 1M-2M KRW

**Everything in Tier 1, plus:**
1. Copy-paste ready robots.txt changes
2. JSON-LD schema.org markup for homepage
3. llms.txt file content (ready to upload)
4. Rewritten About page text (GEO-optimized)
5. Rewritten product page text (1 page, with FAQ section)
6. Step-by-step implementation checklist for developer
7. 30-minute consultation call

**Your time:** 4-6 hours

### Tier 3: 월간 GEO 관리 — 500K-1M KRW/month (3-month min)

**Each month:**
1. SoV tracking report (15-20 queries across ChatGPT/Perplexity/Claude)
2. 2 content recommendations
3. Quarterly full re-audit
4. Monthly 15-minute check-in call

**Your time:** 3-4 hours/month

---

## Part 4: Why They Can't DIY — The Five Moats

1. **Market education gap** — Korean SMEs have never heard of GEO. You own the client relationship by explaining the problem first. Temporary moat (2-3 years).
2. **Systematic measurement is tedious** — Querying 15-20 prompts across 3-4 AI systems monthly, logging, comparing. No SME owner sustains this. Your tool automates it.
3. **Technical implementation knowledge** — schema.org JSON-LD, llms.txt, AI-extractable content structure. Most Korean SME developers have never heard of these.
4. **Before/After proof is your sales weapon** — `before_after.py` shows what AI says NOW vs. AFTER GEO, on-the-spot. No other Korean service does this.
5. **Accountability prevents quitting** — GEO takes 3-6 months to compound. Monthly retainer keeps clients committed through the lag.

**What NOT to claim:**
- Don't claim consulting experience you don't have
- Don't promise revenue outcomes — GEO increases AI visibility, not directly sales
- Don't position against established firms — your competition is "doing nothing"

---

## Part 5: Execution Timeline

| Week | Action | Output |
|------|--------|--------|
| This session | Run 에이스침대 practice audit | PDF + screenshot for case study |
| This session | Fix all 6 gaps | Client-ready tool |
| This week | Find SDC connection with online business, offer free audit | First target |
| Week 2 | Deliver free audit + record client reaction | Case study material |
| Week 2-3 | Post case study on LinkedIn (Korean) | Social proof |
| Week 3-4 | Second client at 300K KRW | First revenue |
| Month 2+ | Raise to 500K-700K KRW, offer Tier 2 | Scalable pricing |

---

## Files Modified

| File | Change | Status |
|------|--------|--------|
| `projects/lead-intelligence/geo_audit.py` | Add `generate_dynamic_recommendations()`, Korean presence, SoV | ✅ |
| `projects/geo-agency/app.py` | Replace hardcoded recs + show all 7 metrics | ✅ |
| `projects/geo-agency/geo_report_pdf.py` | Competitive landscape, realistic projected score, roadmap | ✅ |
| `projects/lead-intelligence/dart_screener.py` | Fix MultiIndex extraction bug | ✅ |

---

## Pending: GEO Scoring Restructure (5 Categories)

User requested restructure into consultant-grade 5-category system:

1. **AI Citability & Share of Voice** — Is the company cited by AI? Who are competitors in AI answers?
2. **Crawler & Agent Accessibility** — robots.txt AI directives + llms.txt + response headers
3. **Schema & Structured Data** — JSON-LD depth, Organization schema, FAQ schema
4. **Local Sync — KR Platforms** — Naver Smart Place consistency with global AI profiles
5. **Brand Sentiment & Mention Quality** — How is brand described in AI summaries? Premium vs. commodity?

This restructure is IN PROGRESS — see `geo_audit.py` for current implementation state.
