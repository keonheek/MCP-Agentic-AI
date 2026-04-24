# GEO Agency

## What this is
Generative Engine Optimization audit service. Audits Korean SME websites for AI citability and generates PDF reports + implementation kits.

## Key files
- `app.py` — Streamlit UI (audit form, PDF download, kit preview)
- `geo_report_pdf.py` — 2-page PDF generator (fpdf2, 맑은고딕)
- `before_after.py` — Perplexity "before" + Claude Haiku "after" citation proof
- `geo_audit.py` — Core audit engine (5 categories, 10 dimensions)

## ICP (Revised 2026-03-25)

**Tier 1 — Primary targets (clearest GEO ROI, willingness to pay):**
- 세무사 / 노무사 / 법무사 — corporate clients use ChatGPT/Perplexity to find them
- Premium medical/aesthetic clinics — educated patients research via AI before calling
- E-commerce brands (cosmetics, food exports) — international buyers use AI heavily
- B2B SaaS / tech startups — already understand digital presence

**Tier 2 — Secondary (good fit with right framing):**
- Franchise operators (ROI multiplies across locations)
- Premium fitness studios, language academies
- Specialty food/beverage brands with national distribution

**Tier 3 — Portfolio/lead magnet only (NOT paying clients):**
- Neighborhood cafes, nail salons, barbershops
- These customers use Naver Map, not ChatGPT — GEO has no direct ROI for them
- Use 3D landing page demos for Instagram portfolio and door-opening only

**Why lifestyle SMEs are poor GEO targets:**
Korean local business customers discover businesses via Naver Map/Kakao Map, not ChatGPT. GEO = AI citation optimization — only valuable when customers use AI to search. Tier 1 clients have customers who do.

## Outreach Channels (NOT LinkedIn — low penetration in Korea)
- **Naver Smart Place / Naver Blog** — find Tier 1 contact info
- **KakaoTalk** — universal. Most small B2B firms have KakaoTalk Channel or listed number.
- **Naver Café** — 소상공인/세무/노무 커뮤니티. Post useful content, not sales pitch.
- **Cold text/call** — still standard in Korean small B2B.

## Credibility (student, no clients yet)
1. Lead with SKKU: "SKKU 경영학과 재학 중, AI 마케팅 연구 중입니다"
2. Free audit opener — paste ChatGPT result for their business, offer to fix it
3. 라라스윗 case study PDF — attach to every outreach (before/after proof)
4. GitHub portfolio — shows technical ability
5. Naver Blog — publish "세무사를 위한 AI 검색 최적화 가이드"

## Status
Built. First client not yet contacted. ICP revised to B2B service providers (세무사, clinics, e-commerce).

## Pricing
- Free audit (demo) → 500K KRW (paid audit + kit) → 1.5M KRW/month (retainer)
- Market ceiling: 4-7M KRW per audit

## Stack
- Python, Streamlit, fpdf2, Perplexity API (sonar), Anthropic API (Haiku)
- ANTHROPIC_API_KEY required for before_after.py "after" generation

## Run
```bash
streamlit run app.py
```
