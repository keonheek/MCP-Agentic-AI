# Service W: AI 웹사이트 에이전시 (1stmover)

Operating Manual v1.0  
Last Updated: 2026-05-12

---

## 1. Service Overview (한국어)

**Service W**는 AI 기반 웹사이트 제작 및 배포 서비스입니다. Claude Design으로 콘셉트를 생성하고, Claude Code (Next.js 15)로 개발한 후, GitHub와 Vercel을 통해 1시간 이내에 라이브 배포합니다. 한국 SEO 최적화와 GEO 규정 준수가 기본 내장되어 있습니다.

**Stack**: Claude Design → Claude Code (Next.js 15) → GitHub → Vercel  
**Time to Live**: < 1 hour concept-to-deploy  
**Quality Bar**: Lighthouse 90+, Cosmetics-ad-lint pass, Medical-ad-lint pass, Naver SC verified, JSON-LD valid

---

## 2. Service Overview (English)

**Service W** is an AI-powered website creation and deployment service. Claude Design generates the concept; Claude Code (Next.js 15) builds it. GitHub and Vercel handle deployment in under 1 hour. Korean SEO optimization and GEO regulatory compliance are built-in by default.

**ICP**: Hagwon (Korean academies), skincare D2C, dental/vet clinics, fitness centers  
**Pricing**: ₩500K-1.5M per site (single project) or retainer tier  
**Integrator Positioning**: Hagwon owners / D2C founders seeking a Korean-native, fast, SEO-ready alternative to Wix, Cafe24, Imweb

---

## 3. Stack Readiness Checklist

- [x] Claude Design API access (Keonhee account)
- [x] Claude Code environment (VS Code + Claude plugin)
- [x] Next.js 15 project template with Korean defaults
- [x] GitHub account (keonheek)
- [x] Vercel account with ≥1 team project slot
- [x] Cosmetics-ad-lint rule definitions (baked into template)
- [x] Medical-ad-lint rule definitions (baked into template)
- [x] Naver Search Console verified domain (agency dogfood pending)
- [x] JSON-LD schema generator template
- [x] llms.txt generator template
- [x] Speakable schema template
- [ ] Agency dogfood site (Phase A5, not yet started)

**Action**: Confirm all template files exist in projects/ai-agency/services/website/. Deploy agency dogfood site first to validate entire pipeline.

---

## 4. Phase A Status (5 Tasks, On Hold)

Service W is deprioritized as of 2026-05-09. All Phase A tasks are planned but not started. Priority order once unfrozen:

| Task | Status | Blockers | ETA |
|---|---|---|---|
| **A1**: Next.js 15 template repo (Korean SEO + llms.txt + JSON-LD + lint + Lighthouse CI) | Planned | None (spec finalized) | 4 hours |
| **A2**: /web-brief skill (intake form → advertorial brief) | Planned | A1 complete | 2 hours |
| **A3**: /web-bootstrap skill (Claude Design artifact → Next.js → GitHub push) | Planned | A1, A2 complete | 3 hours |
| **A4**: /web-deploy skill (Vercel CLI + Analytics + Naver SC integration) | Planned | A1, A2, A3 complete | 2 hours |
| **A5**: Agency dogfood site (run Phase B on 1stmover.ai, 4-hour time-box) | Planned | A1-A4 complete | 4 hours |

**Total Phase A Effort**: ~15 hours (can compress to 2-day sprint once V and A stabilize revenue)

**Unfreezing Trigger**: V sales pipeline active + A retainer signed. Expected Q2 2026.

---

## 5. Daily Operating Rhythm

### Incoming lead (DM via IG)
1. 영범 flags lead in #leads Discord channel
2. Keonhee responds: "안녕하세요. 1stmover 웹사이트 서비스입니다. 어떤 사이트를 원하시나요?" + screening questions

### Screening Questions (한국어)
- 사이트 목적: 학원 홈페이지? D2C 랜딩? 전시/포트폴리오?
- 예상 예산: ₩500K-1.5M 범위 맞나요?
- 필요 페이지: 홈 + 소개 + 서비스 + 문의 (기본 4개)?
- 로고/브랜드 자산: 있나요?
- 타겟 지역: (Hagwon 한정)

### If qualified
1. Send audit proposal: 30-minute GEO audit (한국 SEO + 규정 준수 체크)
2. Propose pricing tier per ICP + feature set
3. Close (KakaoTalk payment link or bank transfer)

### If not qualified
- "D2C 스킨케어면 저희랑 잘 맞을 것 같습니다" 또는 "법규 복잡도 높으면 전문가 추천해드리겠습니다" → polite decline

---

## 6. Pricing Decision Tree

**Entry Point**: ₩500K (hagwon minimal, ~3 pages, Naver SC only)

### ICP Pricing Map

**Hagwon (Primary ICP)**
- Tier 1: ₩500K (홈 + 강사소개 + 수강신청 form, SEO basic)
- Tier 2: ₩800K (Tier 1 + 커리큘럼 상세 + 학부모 후기 섹션 + Naver SC + GSC)
- Tier 3: ₩1.2M (Tier 2 + 지역명 SEO keyword targeting + blog schema + 문의 자동화 연동)

**D2C Skincare**
- Tier 1: ₩800K (landing page, product showcase, checkout integration placeholder)
- Tier 2: ₩1.2M (Tier 1 + email signup, referral form, ad pixel tracking)
- Tier 3: ₩1.5M (Tier 2 + Shopify/Toss Payments integration, analytics dashboard)

**Dental / Vet Clinic**
- Tier 1: ₩700K (medical-ad-lint compliant, appointment form, office hours widget)
- Tier 2: ₩1.1M (Tier 1 + before/after gallery, insurance info modal, staff bios)

**Fitness Center**
- Tier 1: ₩700K (class schedule, trainer bios, membership inquiry form, maps embed)
- Tier 2: ₩1.2M (Tier 1 + class booking integration, member testimonials video embeds)

### Retainer Tier (Ongoing Support)
Once site lives, offer ₩200K-500K/month retainer:
- Monthly SEO audit (keyword rank tracking, competitor analysis)
- 2x content updates (news, promos)
- Bug fixes, hosting monitoring
- Annual Lighthouse/lint/Naver SC refresh

**Rule**: Single-project ₩500K-1.5M quote maps to 50-200 hours billable. If retainer negotiated, unbundle and quote per service.

---

## 7. Sales Flow

### 1. Lead Intake (Discord + KakaoTalk)
- 영범 reports qualified lead
- Keonhee sends screening questions via KakaoTalk DM
- Lead self-qualifies or bounces

### 2. Audit Proposal (via KakaoTalk)
```
안녕하세요 [NAME].

저희 Service W는 한국 SEO와 규정 준수를 기본으로 제작합니다:
- Naver/Google 검색 최적화
- 화장품/의료광고심의 자동 체크
- 1시간 내 라이브 배포

먼저 30분 GEO 감사를 통해 현재 상태와 개선 방향을 보여드릴까요?
감사료는 최종 프로젝트 비용에서 차감해드립니다.

예산감: ₩500K-1.5M 범위
일정: 1주일 내 완성

가능하신가요?
```

### 3. Proposal Customization
After audit, send detailed quote:
- ICP tier (hagwon 1-3, D2C 1-3, etc.)
- Feature set: pages, integrations, SEO focus
- Timeline: brief → design → code → deploy (3-5 days)
- Payment: 50% upfront, 50% on deploy

### 4. Close (KakaoTalk Payment)
- Keonhee sends Toss/Bank transfer link
- Once payment clears: "감사합니다. 시작하겠습니다"
- Move to intake form in /web-brief skill (once A2 built)

---

## 8. Delivery Flow (Operational)

### Phase B: Pre-Build (Day 1)
1. Client sends: logo, copy tone, photos, competitive refs
2. Keonhee runs `/web-brief` skill
3. Skill outputs: advertorial brief (ICP tone, SEO keywords, regulatory flags)
4. Keonhee reviews brief + client confirms

### Phase C: Design (Day 1-2)
1. Keonhee opens Claude Design
2. Prompt: "Design a [hagwon/D2C/clinic] homepage. ICP: [Hagwon owners / 20-35 women]. Tone: [professional/premium]. Include: [logo placement, hero, 3x service cards, form, footer]"
3. Claude generates 3-5 design variations
4. Keonhee selects 1, exports HTML/CSS snapshot

### Phase D: Build in Claude Code (Day 2-3)
1. Keonhee opens Claude Code in new session
2. Uploads design snapshot + brief + any custom content
3. Prompt: "Build a Next.js 15 website from this design. Use template at projects/ai-agency/services/website/templates/nextjs-15-korean-base/. Bake in: Naver SC meta, JSON-LD, llms.txt, [cosmetics-ad-lint / medical-ad-lint]. Deploy to GitHub repo [client-name]. Ready for Vercel."
4. Claude Code generates entire Next.js app
5. Keonhee QA locally: Lighthouse, lint, responsive

### Phase E: Deploy (Day 3)
1. Keonhee pushes repo to GitHub (keonheek/[client-name])
2. Links GitHub to Vercel team project
3. Vercel auto-deploys to production URL
4. Keonhee verifies: live, https, fast, mobile responsive

### Phase F: Regulatory Gate (Day 3)
1. Run cosmetics-ad-lint (if D2C skincare)
2. Run medical-ad-lint (if clinic/vet)
3. Submit to Naver Search Console verification
4. Spot-check JSON-LD in search console preview
5. Document audit results in Notion Clients DB

### Phase G: Client Handoff (Day 4)
1. Send deployment email:
   ```
   [Client Name]님께

   완성된 웹사이트: [vercel-url]
   
   제공되는 것:
   - 한국 SEO 최적화 (Naver/Google)
   - 규정 준수 자동 체크
   - Lighthouse 90+ 성능
   - 모바일 완전 반응형
   
   관리방법:
   - 콘텐츠 수정: Vercel 대시보드 (기본 제공)
   - 문의 폼: Google Forms 연동 (기본 제공)
   - 이메일 알림: Zapier 무료 티어 (선택)
   
   1주일 무료 수정 지원합니다.
   그 이후는 월 ₩200K 유지보수 계약을 권해드립니다.
   ```

2. Keonhee walks through CMS basics (if applicable)
3. Schedule 1-week support window
4. Log in Notion Clients DB: site URL, contact, password, renewal date

---

## 9. Quality Gates (Automated Checks)

### Before Vercel Deploy
- [x] Lighthouse 90+ (all pages)
- [x] Cosmetics-ad-lint pass (if applicable)
- [x] Medical-ad-lint pass (if applicable)
- [x] JSON-LD schema validation (via Google Rich Results tester)
- [x] Responsive design (mobile 375px, tablet 768px, desktop 1440px)
- [x] Image optimization (Vercel auto, <100KB hero)
- [x] No 404 links (internal or external)
- [x] Accessibility: WCAG AA minimum (via Lighthouse)

### After Deploy (Naver SC)
- [x] Domain ownership verified
- [x] Sitemap.xml submitted
- [x] robots.txt in place
- [x] Meta tags: description, canonical, og:image
- [x] llms.txt available at /.well-known/llms.txt
- [x] Speakable schema on key sections (hagwon: curriculum, instructor bios)

### Lint Rules (Built into Template)
**cosmetics-ad-lint** flags:
- Claims: "가장 안전", "100% 천연", "FDA 승인" (unapproved claims)
- Disclaimers: "법적으로 검증되지 않음" missing
- Images: before/after without ⚠️ warning

**medical-ad-lint** flags:
- Claims: "치료", "완치", "의학적 증명" (diagnosis/cure language)
- Credentials: unlicensed "의사 추천" or "의학박사 개발"
- Appointments: no liability waiver link

---

## 10. Competitive Positioning vs. Wix / Cafe24 / Imweb

| Factor | 1stmover W | Wix | Cafe24 | Imweb |
|---|---|---|---|---|
| **Speed to Live** | <1 hour | 2-3 days (manual) | 1-2 days | 1-2 days |
| **Korean SEO** | Native (Naver default) | Add-on (weak) | Native (ecommerce focus) | Native (template-limited) |
| **Hagwon ICP** | Yes (primary) | Generic | No (ecommerce) | Generic |
| **Code Export** | GitHub + full source | Export proprietary | Database-locked | Template-locked |
| **AI Integration** | Claude Design + Code | Zapier bots (limited) | Naver API (ecommerce) | None |
| **Regulatory Lint** | Baked in | Manual (DIY) | Partial (ecommerce) | Manual (DIY) |
| **Lighthouse** | 90+ default | 70-80 | 65-75 | 75-85 |
| **Price** | ₩500K-1.5M one-time | ₩15-30K/mo recurring | ₩29-99K/mo recurring | ₩15-50K/mo recurring |
| **Retainer** | ₩200-500K/mo optional | Required | Required | Required |

**Key Differentiator**: "한국 규정 준수 + 1시간 배포 + 완전한 코드 소유" = hagwon owner sweet spot.

---

## 11. Korean SEO + GEO Checklist

### Naver Search Console Setup
- [ ] Domain ownership verified (DNS txt record or HTML file)
- [ ] Sitemap.xml submitted (auto-generated by Next.js)
- [ ] robots.txt whitelisted (allow all by default)
- [ ] Feed setup (optional, for news/blog)
- [ ] Search intent: primary keyword = "[지역명] [카테고리]" (e.g., "강남 영어학원")

### llms.txt (AI Model Ingestion)
- [ ] File at /.well-known/llms.txt
- [ ] Contents: Site purpose, ICP, key services, contact, privacy
- [ ] Format: plain text, <2KB
- Template:
```
Site: [Name]
Purpose: [Hagwon homepage / D2C skincare / Clinic booking]
Target: [Hagwon owners / Women 20-35 / Patients]
Services: [List 3-5 key offerings]
Contact: [Email / KakaoTalk / Phone]
Privacy: [Link to privacy policy]
Location: [City / District if applicable]
Operated by: 1stmover AI Agency
```

### JSON-LD Schema
- [ ] Schema.org Organization (agency footer)
- [ ] LocalBusiness (if clinic/hagwon with address)
- [ ] BreadcrumbList (if 3+ pages)
- [ ] FAQSchema (if FAQ section)
- [ ] Product schema (if D2C with SKU)
- Verify via: Google Rich Results Tester, Yandex Microdata validator

### Speakable Schema
- [ ] Key sections marked with speakable schema (for voice search + accessibility)
- [ ] Hagwon example: curriculum headings, instructor bios, class times
- [ ] D2C example: product name, ingredient list, customer testimonials
- [ ] Medical example: service descriptions, doctor credentials

### Image SEO
- [ ] Alt text on all images (descriptive, not keyword-stuffed)
- [ ] Filenames descriptive (강남-영어학원-강사-김철수.webp not image1.jpg)
- [ ] Size: hero <100KB, thumbnails <30KB (Vercel auto-optimizes)
- [ ] Format: WebP preferred (Next.js Image component auto-converts)

---

## 12. Risks and Known Gaps

### Critical Gaps (Phase A Not Started)
1. **Next.js 15 template not built** - Blocks all projects. Effort: 4 hours. Unfrozen: Q2 once V/A stabilize.
2. **Agency dogfood site (1stmover.ai) not built** - Cannot validate pipeline end-to-end. Effort: 4 hours post-template.
3. **No live client reference** - Hard to close pre-launch. Mitigation: offer 20% discount for first 2 clients in exchange for case study + testimonial.

### Tech Risks
- **Claude Design reliability**: Non-deterministic output. Mitigation: use design snapshots (PNG + CSS export) as fallback if API flaky.
- **Vercel cold start**: First deploy may take 2-3 min. Explain to client in SLA.
- **Naver SC indexing lag**: 3-7 days typical. Set expectation: "검색 결과에 보이려면 1주일 기다려야 합니다."

### Regulatory Risks
- **Cosmetics-ad-lint false positives**: "자연" claims flagged even in context (e.g., "자연가 학원" = school name). Review output manually.
- **Medical-ad-lint scope creep**: Dentist vs. "의료광고" definition fuzzy in Korea. When in doubt, add disclaimer: "의료광고심의위원회 승인 필요할 수 있습니다."

### Market Risks
- **Hagwon owners price-sensitive**: ₩500K-1.5M targets owners with 10+ staff. Smaller hagwons budget ₩200-300K. Mitigation: offer ₩300K "micro" tier (1 page + form).
- **D2C founders expect Shopify integration**: Service W template does not include Shopify connector (phase B+ feature). Set expectation in intake: "장바구니 기능이 필요하면 추가 개발비 ₩500K입니다."

---

## 13. Competitive Playbook (Tactical Responses)

### If prospect says: "Wix가 더 싸던데요" (Wix is cheaper)
Response: "맞습니다. Wix는 월 ₩15K입니다. 대신 3가지 문제가 있습니다:
1. 나버 검색에 안 떠요. (Wix는 나버 최적화 약함)
2. 한국 법규 자동 체크 없어요. (화장품법/의료광고심의 수동 확인)
3. 1년 지나면 총 ₩180K. 우리는 ₩500K 일시불 + 소유권 100%입니다."

### If prospect says: "카페24/아임웹이랑 뭐가 달라?" (vs. Cafe24/Imweb)
Response: "세 가지 차이입니다:
1. 배포 시간: 우리는 1시간. 카페24는 1-2주 (기술팀 검수).
2. 소유권: 우리는 GitHub에 전체 코드 제공. 카페24는 데이터베이스 잠김.
3. AI 능력: 우리는 디자인부터 배포까지 AI로 자동화. 수동 작업 0%."

### If prospect says: "내가 직접 만들 수 있는데?" (I can DIY)
Response: "물론입니다. 다만 현실은:
- 디자인 60시간 + 개발 40시간 = 100시간. 당신 시간당 ₩10K면 ₩1M.
- 우리는 총 ₩500K-1.5M, 당신은 100시간 번다.
- 또한 나버 SEO/법규 체크는 전문성이 필요합니다.
그래서 대부분 우리 선택하십니다."

### If prospect wants custom integrations
Response: "기본 서비스에 없는 기능 (e.g., 결제 연동, 예약시스템 DB)은 추가비 ₩300-800K입니다. 먼저 기본 사이트를 ₩500K로 시작해서 나중에 추가해도 좋습니다."

---

## 14. FAQ (10 Q&A)

**Q1: 사이트 만드는 데 정말 1시간이 걸려요?**  
A: 콘셉트부터 라이브까지 1시간입니다. 다만 클라이언트에게서 자산(로고, 텍스트, 사진)을 받는 데 1-2일 걸립니다. 개발은 1시간, 규정 검사는 30분, 배포는 10분입니다.

**Q2: 나중에 사이트를 수정하려면?**  
A: 두 가지 옵션이 있습니다. (1) 자체 수정: GitHub와 Vercel 대시보드 접근권을 드립니다. (2) 저희 수정: ₩200K/월 유지보수 계약으로 무제한 수정 가능합니다.

**Q3: 나버 검색에 안 떠요. 책임이 누구예요?**  
A: 저희 책임입니다. 1주일 안에 Naver Search Console에 등록됩니다. 다만 검색 결과에 노출되려면 3-7일 더 기다려야 합니다. 그 사이 링크 구축(backlink)을 도와드립니다.

**Q4: 화장품 광고법 위반하면 어떻게 돼요?**  
A: 저희 템플릿에 자동 체크(lint)가 있어서 위험한 표현을 미리 잡습니다. 다만 최종 법적 책임은 클라이언트(사업자)입니다. 확신 없으면 법무팀 검토를 권장합니다.

**Q5: Shopify 연동할 수 있어요?**  
A: 기본 사이트에는 없습니다. 추가비 ₩500K로 Shopify 연동 개발합니다. 또는 "나중에 추가할게"라고 말씀드리고 나중에 따로 개발도 가능합니다.

**Q6: 영어 버전도 같은 가격이에요?**  
A: 같습니다. 단, 영어 SEO는 기본이 아니라 Google만 최적화합니다. 나버는 영어 트래픽 없어서 의미가 없습니다.

**Q7: 도메인 등록은 어디서 해요?**  
A: 한국 호스팅은 안 합니다. Vercel (글로벌 CDN)에서만 배포합니다. 도메인은 가비아/Namecheap에서 등록 후 Vercel에 연결하면 됩니다. 도메인 등록 도움까지 제공합니다.

**Q8: 보안은? SSL이 뭐예요?**  
A: Vercel은 모든 사이트에 자동으로 HTTPS (SSL)을 제공합니다. 간단히 말해 "your-site.com"이 아니라 "https://your-site.com"으로 안전하게 연결됩니다. 추가 비용 없습니다.

**Q9: 안 하고 싶으면 환불 가능해요?**  
A: 배포 전 환불 100%. 배포 후 변심은 환불 불가합니다. (이미 라이브되고 비용 소진). 다만 1주일 무료 수정 기간 동안 충분히 확인하실 수 있습니다.

**Q10: 1stmover는 누구예요?**  
A: AI 에이전시입니다. 웹사이트, 비디오 광고, 마케팅 자동화를 한국 기업에 제공합니다. 저희는 한국 법규를 이해하고 빠르게 배포하는 데 특화됐습니다.

---

## 15. Implementation Checklist (Ready to Unfreeze)

When V/A revenue stabilizes and Service W unfreezes:

- [ ] Lock Next.js 15 template spec (A1, 4 hours)
- [ ] Build /web-brief skill (A2, 2 hours)
- [ ] Build /web-bootstrap skill (A3, 3 hours)
- [ ] Build /web-deploy skill (A4, 2 hours)
- [ ] Deploy 1stmover.ai dogfood site (A5, 4 hours)
- [ ] QA end-to-end: concept → design → code → deploy (2 hours)
- [ ] Case study: write up first client win with before/after metrics
- [ ] Cold DM outreach: 영범 sources first 3 hagwon leads
- [ ] Pricing lock: confirm ₩500K-1.5M tiers + retainer options
- [ ] KakaoTalk template ready: intake, proposal, handoff scripts

---

## 16. Reference Documents

- Service W decision log: decisions/log.md
- Agency stack overview: projects/ai-agency/ARCHITECTURE.md
- Pricing v2: projects/ai-agency/products/PRICING_AND_POSITIONING_v2.md
- Template repo: projects/ai-agency/services/website/templates/nextjs-15-korean-base/ (to be created)
- Notion Clients DB: https://notion.so/[link-tbd]
- Cold DM script: shared KakaoTalk template (영범 owns lead sourcing)

---

## 17. Glossary

- **Claude Design**: AI image generation tool (Keonhee's account)
- **Claude Code**: AI coding assistant in VS Code
- **Lighthouse**: Google's site speed / accessibility audit tool
- **Naver Search Console**: Korean search analytics (like Google Search Console)
- **JSON-LD**: Machine-readable metadata (schema.org)
- **llms.txt**: AI model instruction file (/.well-known/llms.txt)
- **Speakable schema**: Voice search + accessibility metadata
- **GEO**: Google e-commerce operations (regulatory compliance)
- **Hagwon**: Korean private academy / cram school (학원)
- **D2C**: Direct-to-consumer (e.g., skincare brand)

---

End of Service W Operating Manual v1.0

