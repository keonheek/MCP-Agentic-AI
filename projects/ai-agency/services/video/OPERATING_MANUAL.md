# Service V Operating Manual
## AI 영상 광고 에이전시

**Last updated:** 2026-05-11  
**Status:** Pre-launch (API keys pending)  
**Owner:** Keonhee  
**Primary audience:** Korean D2C cosmetics/skincare brands

---

## 1. Overview: What We Sell

Service V transforms product photography into scroll-stopping video ads. One client input. Nine concept variations. Three polished finals. Delivery in 5 business days.

**What the client gets:**
- 3 finished video ads (15-30 sec, mobile-native)
- Korean voiceover (natural, on-brand tone)
- Royalty-free background music
- Notion delivery package with usage rights
- 화장품법 compliance check (built-in)

**What we charge:**
- Standard: ₩500K–₩1M per project (3 finished ads)
- Retainer: ₩2.5M–₩5M/month (4-8 projects)
- Rush (48h): +₩300K

**ICP (Ideal Client Profile):**
- Korean D2C skincare/cosmetics brands
- Annual marketing budget: ₩50M+
- 1–3 existing product lines
- Running paid social (Naver SmartStore, Instagram, TikTok)
- Pain: video content is slow, expensive, risky legally
- Buying signal: "our ads convert 2%, we need 3-4%"

**Why they choose us over competitors:**
- **vs. sadarifilm.com:** Same day turnaround, 1/3 the price, legally compliant by default
- **vs. premier.ai.kr:** Higgsfield Pro handles Korean text/branding better; we own the entire stack
- **vs. aidonna.kr:** We focus cosmetics-first (not general e-commerce); cosmetics law is our native playbook

---

## 2. Stack Readiness Checklist

| Tool | Purpose | API Key | Cost/mo | Status | Signup URL | ETA |
|---|---|---|---|---|---|---|
| Higgsfield Pro | Image→video gen, motion control | Required | $99 | PENDING | higgsfield.ai/pro | This week |
| Veo 3 | Hero shot generation (Google) | GCP Service Account | $0–300/mo | PENDING | console.cloud.google.com | This week |
| ElevenLabs v3 | Korean voiceover (natural speech) | Required | $99 | PENDING | elevenlabs.io/app/billing | This week |
| Suno Pro | Background music generation | Required | $15/mo | PENDING | suno.com/app/billing | This week |
| Claude Sonnet 4.6 | Concept writing, brief drafting | API key from main account | Included | OK | Already configured | Ready |

**Total monthly cost:** ~₩350K (₩99+99+15+50 at ~₩3.8 rate, Veo 3 variable)

**Critical path to launch:**
1. Higgsfield Pro signup + API key (48 hours, one-person task)
2. Google Cloud Veo 3 (1 business day, requires GCP project setup)
3. ElevenLabs v3 + Korean voice clone optional (24 hours)
4. Suno Pro (immediate, add to account)
5. All integration tests pass (1 day)

---

## 3. Unblock Plan (This Week)

Do these in order. Check off as you go.

### Monday 2026-05-12

**Step 1: Higgsfield Pro signup [45 min]**
- Go to https://higgsfield.ai/pro
- Sign up with keonhee3337@gmail.com
- Choose "Video Generation (Pro)" tier
- Accept billing (card on file, $99/mo or prepay)
- Get API key from dashboard > Integrations > API Keys
- Test with: `curl -X POST https://api.higgsfield.ai/generate -H "Authorization: Bearer <KEY>" -d '{"model":"hf-motion","input":"test"}'`
- Save key to `.env` as `HIGGSFIELD_API_KEY=...`
- Mark: DONE

**Step 2: Google Cloud Veo 3 setup [90 min]**
- Create GCP project: https://console.cloud.google.com/projectcreate
- Project name: `keonhee-service-v` (simplicity)
- Enable APIs: Vertex AI, ImageAPI (search for them in API console)
- Create Service Account: IAM > Service Accounts > Create Service Account
  - Name: veo3-api
  - Grant: `Vertex AI User` role
  - Generate JSON key > download and save to `.env` or config file
- Test auth: `gcloud auth activate-service-account --key-file=veo3-sa-key.json`
- Mark: DONE

**Step 3: ElevenLabs v3 signup [30 min]**
- Go to https://elevenlabs.io/app/billing
- Choose "Starter" or "Professional" (Starter: $5/mo, Professional: $99/mo)
- Professional recommended for Korean voice quality + API batch calls
- Get API key from Settings > API Keys
- Optional: clone Keonhee's voice (Settings > Voice Cloning, upload 30sec sample) for personal branding
- Test: `curl https://api.elevenlabs.io/v1/models -H "xi-api-key: <KEY>"`
- Save key to `.env` as `ELEVENLABS_API_KEY=...`
- Mark: DONE

**Step 4: Suno Pro signup [15 min]**
- Go to https://suno.com/app/billing
- Upgrade to Pro ($15/mo, billed monthly)
- Get API key from Settings > API Keys
- Test: `curl https://api.suno.ai/api/auth/verify -H "Authorization: Bearer <KEY>"`
- Save key to `.env` as `SUNO_API_KEY=...`
- Mark: DONE

**Step 5: Create `.env` file [10 min]**
- Location: `projects/ai-agency/services/video/.env`
- Contents:
  ```
  HIGGSFIELD_API_KEY=sk_...
  ELEVENLABS_API_KEY=...
  SUNO_API_KEY=...
  GCP_SERVICE_ACCOUNT_FILE=./veo3-sa-key.json
  GOOGLE_APPLICATION_CREDENTIALS=./veo3-sa-key.json
  CLAUDE_API_KEY=[from main]
  ```
- Mark: DONE

### Tuesday 2026-05-13

**Step 6: Integration test [120 min]**
- Create test script: `projects/ai-agency/services/video/test_stack.py`
- Test each tool in sequence:
  - Higgsfield: image→video (use dummy product photo)
  - Veo 3: generate hero shot
  - ElevenLabs: generate 10-second Korean voiceover
  - Suno: generate 30-second background track
  - Claude Sonnet: generate brief from product description
- All 5 must pass before moving to dogfood
- Mark: DONE

**Step 7: Generate Service V's own dogfood reel [240 min]**
- See section 4 below for full step-by-step
- Deliverable: 3 final ads for Keonhee's own "fictional" skincare brand (MOCKUP)
- Purpose: prove the stack works, create internal portfolio asset, identify workflow gaps
- Deadline: EOD Tuesday
- Mark: DONE

### Wednesday 2026-05-14

**Step 8: Brand name decision [locked][BLOCKERS]**
- Current state: "AI Agency by Keonhee Kim" placeholder
- This blocks all cold DM copy, Notion client DB naming, Service V landing page
- Recommendation: 3-letter Korean or English name (easy to spell, domain available)
  - Example: VID (영상), ADS (광고), PLIX (Play+Mix)
- Decision: Async on Notion or Discord with 영범 by EOD Tuesday
- Mark: DECIDED or SKIP (decision pending)

**Step 9: Notion Clients DB setup [60 min]**
- Create database at `projects/ai-agency/crm/Clients`
- Fields: Name, Service (V/A/W), Status (Lead/Qualified/Proposal/Won/Lost), Product Photos (file), Brief (text), Quote (₩), Timeline
- Create automation: "When Status = Won, create Delivery folder in Drive"
- Mark: DONE

---

## 4. Pre-Launch Dogfood: Your First Ad

**Why:** Proof of concept. Identify workflow gaps. Build internal portfolio. Time box: 4 hours.

**Setup:**
- Use 3 dummy product photos (find 3 realistic skincare product images, 1000x1000px minimum)
- Fictional brand: "LUME" (skincare)
- Brief: "Lightweight, waterless serum for sensitive skin. Target: women 25-35, natural ingredients angle."

**Step-by-step:**

### 1. Write the concept brief (20 min)

Use Claude Sonnet with this prompt:

```
당신은 한국 화장품 광고 카피라이터입니다. 

제품: 가벼운 워터리스 세럼
타겟: 여성 25-35세, 자연 성분 선호
키메시지: "물 없이도 깊게 보습된다"

요구사항:
- 한글 자연스러운 톤 (딱딱하지 않게)
- 30초 광고용 (120-150 글자)
- 한 가지 감정: "가볍지만 강하다" (light but powerful)
- 해시태그 3개

결과: 3가지 다른 앵글의 스크립트를 제시하세요.
1. 감성라이프스타일 (새벽의 루틴)
2. 성분 신뢰 (투명성)
3. 즉각적 효과 (신뢰도)
```

**Output:** 3 concept variations (e.g., "Morning ritual angle", "Ingredient trust", "Instant results"). Save to Notion.

### 2. Generate 3 hero images with Veo 3 (60 min)

For each concept, generate ONE high-fidelity hero shot.

**Example prompt for Veo 3:**

```
A close-up of transparent serum droplets falling onto a porcelain plate. 
Soft morning light. 
Minimalist white background. 
Product bottle visible in soft focus. 
Korean aesthetic. 
4K resolution.
```

- Tool: Vertex AI Studio (console.cloud.google.com) > Veo 3
- Generate 3 images, one per concept
- Download + save to `projects/ai-agency/services/video/dogfood_lume/images/`
- Target: 1280x720px (landscape for Higgsfield input)

### 3. Create 3 animated product videos with Higgsfield Pro (120 min)

For each hero image, generate motion.

**Higgsfield prompt:**

```
"Product serum bottle slowly rotating on white background. 
Soft light. 
Duration: 10 seconds. 
4K. 
30fps. 
No camera shake."
```

- Use Higgsfield API or dashboard at https://higgsfield.ai/projects
- Input: each Veo 3 hero image
- Output: 10-second video loop
- Download as MP4 (H.264, 1920x1080)
- Save to `dogfood_lume/videos/`

### 4. Generate Korean voiceover (30 min)

For each concept, generate a 15-second voiceover using ElevenLabs.

**Script example (concept 1):**

```
새벽, 가벼운 루틴이 시작된다.
물 없이도, 깊게 보습된다.
LUME 세럼. 가볍지만 강하다.
```

- Tool: ElevenLabs API or dashboard
- Voice: Korean female (natural, not robotic) — Korean-native voice recommended
- Speed: 1.0x
- Output: 15-second MP3
- Save to `dogfood_lume/audio/voiceover/`

### 5. Generate background music (15 min)

For each concept, generate complementary background music using Suno.

**Suno prompt:**

```
Minimal, modern instrumental background music. 
Korean skincare aesthetic. 
Soft piano + ambient strings. 
30 seconds. 
Royalty-free for commercial use.
BPM: 90. Mood: calm, luxurious.
```

- Tool: Suno Pro dashboard
- Output: 30-second WAV or MP3
- License: Confirm commercial use is allowed
- Save to `dogfood_lume/audio/music/`

### 6. Stitch final videos with ffmpeg (60 min)

Combine video + voiceover + music into 30-second vertical ads (9:16 ratio).

**Command template:**

```bash
ffmpeg -i dogfood_lume/videos/hero_1.mp4 \
  -i dogfood_lume/audio/voiceover/concept_1.mp3 \
  -i dogfood_lume/audio/music/bg_music_1.mp3 \
  -filter_complex "[0]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[v]; \
                   [1]volume=0.7[vo]; \
                   [2]volume=0.3[bg]; \
                   [vo][bg]amix=inputs=2:duration=first[a]" \
  -map "[v]" -map "[a]" \
  -c:v libx264 -c:a aac -shortest \
  dogfood_lume/final/ad_concept_1_final.mp4
```

- Repeat for 3 concepts
- Output: 3 x 30-second vertical videos (1080x1920, H.264, AAC)
- Save to `dogfood_lume/final/`

### 7. QA checklist before "ship"

Before showing anyone:

- [ ] Video plays on mobile (test on phone or Lighthouse mobile sim)
- [ ] Audio levels: voiceover -3dB, music -12dB (no peaking)
- [ ] Text overlay (if any): no blur, readable at 360px width
- [ ] Aspect ratio: exactly 9:16 (no letterboxing)
- [ ] File size: <50MB per video
- [ ] Total creative credits used: log for client cost breakdown

**Save results to Notion:** Create page "Dogfood Project: LUME" with 3 final videos embedded. This is your internal proof.

---

## 5. Once Launched: Daily Operating Rhythm

Service V runs in repeating sprints. Each sprint = one client, 5 business days.

```
Day 1 (Monday): Client intake + brief writing
Day 2 (Tuesday): Generate 9 concept variants
Day 3 (Wednesday): Client review + feedback loop (2h turnaround)
Day 4 (Thursday): Generate 3 finalists
Day 5 (Friday): Final QA + deliver to client Notion
```

### Daily rhythm (Mon–Fri):

**Monday 08:00 – Intake call or form submission**
- Client fills: brand name, product category, tone (luxury/playful/scientific), current pain points
- Collect: 2–3 product photos (minimum 1000x1000px)
- Schedule weekly check-ins (async Notion comments are preferred, calls only if stuck)
- Estimated time: 30 min

**Monday 10:00 – Brief writing**
- Claude Sonnet: generate 3 concept angles from product + brand info
- Write in Korean, natural tone, no jargon
- Share draft with client for sign-off (4h turnaround SLA)
- Estimated time: 45 min

**Tuesday 09:00 – Concept generation**
- Veo 3: generate hero shot for each of 3 concepts (3 images)
- Higgsfield Pro: motion-animate each hero (3 videos)
- ElevenLabs: voiceover for each concept (3 MP3s)
- Suno: background music for each (3 tracks)
- Estimated time: 4 hours (parallel where possible)

**Wednesday 09:00 – Stitch & client review**
- ffmpeg: combine all pieces into 3 rough cuts
- Upload to Notion client workspace
- Client reviews, provides feedback (voiceover tone? music tempo? pacing?)
- Estimated time: 2 hours

**Thursday 09:00 – Polish phase**
- Implement feedback: re-voiceover? different music? trim pacing?
- Regenerate only what changed
- Final QA: mobile playback, audio levels, aspect ratio, legal compliance
- Estimated time: 2 hours

**Friday 14:00 – Final delivery**
- Package: 3 final MP4s + usage rights (Notion page)
- Send invoice
- Archive project in drive
- Estimated time: 30 min

---

## 6. Pricing Decision Tree

Use this flow to quote correctly. All prices in Korean won (KRW).

```
Is client asking for:
├─ Single project (3 ads)? [YES]
│  ├─ Standard timeline (5 days)? [YES]
│  │  └─ Quote: ₩500K (new client) or ₩700K (repeat)
│  └─ Rush (48h)? [YES]
│     └─ Quote: ₩800K–₩1M
│
├─ Multiple projects (4+ per month)? [YES]
│  ├─ Committed retainer (3+ months)? [YES]
│  │  ├─ 4 projects/month? └─ ₩2.5M/month
│  │  ├─ 8 projects/month? └─ ₩4M/month
│  │  └─ Unlimited (10+)?  └─ ₩5M/month + success share (%)
│  └─ Ad-hoc pricing (no commitment)? [YES]
│     └─ Quote ₩700K per project (volume discount starts at 4)
│
└─ Hero asset only (1 Veo 3 image, no video)? [YES]
   └─ Quote: ₩200K (cheaper, faster, no voiceover/music overhead)
```

**Discount rules:**
- First 3 clients: offer ₩100K discount (position as "launch special")
- Repeat clients: -₩100K per project
- Retainer 6+ months: add success share clause (e.g., "if CTR exceeds 4%, we earn 10% of incremental revenue")

**Never quote below ₩500K** (margin dies below that). If client balks, pivot to retainer (predictable revenue, client commits to volume).

---

## 7. Sales Flow

From cold DM to signed contract in 5 days.

### Day 1: Cold DM (IG or KakaoTalk)

**IG DM template (Korean, natural tone):**

```
안녕하세요! 서비스 V (영상 광고)를 담당하는 김건희입니다.

귀사의 제품 사진을 보니 영상 광고가 정말 필요할 것 같아요. 
우리는 1주일 안에 3개의 완성도 높은 광고를 만들어 드립니다.
(가격: 50만원~)

포트폴리오 확인하고 싶으신가요? 
링크: [portfolio_url]
```

**Target:** cosmetics D2C brands with <100K followers (easier to land first clients)

### Day 2: Portfolio send + qualification call

- Send portfolio link (Notion page with 3 dogfood LUME ads embedded)
- Schedule 15-minute call (async Notion chat preferred if they're busy)
- Ask three questions:
  1. "How many new products are you launching this year?"
  2. "What's your current video content cost per ad?"
  3. "When would you want to start?"
- Qualify: if budget <₩500K or timeline >3 weeks, pause and offer retainer

### Day 3–4: Proposal send

- Email or Notion proposal (template below)
- Include: scope (3 ads, 5-day timeline), pricing, included revisions (2 rounds), cosmetics law compliance note
- Include simple deal structure graphic (input → 9 concepts → 3 finalists)

**Proposal template (Korean, Notion):**

```
# 제안서: 서비스 V (AI 영상 광고)

**클라이언트:** [Brand Name]
**프로젝트:** [Product Name] 광고 3개
**가격:** ₩700,000 (세금별도)
**일정:** 2026-05-19 ~ 2026-05-23 (5영업일)

## 포함 사항
- Veo 3 + Higgsfield Pro로 생성된 3개 영상 광고
- 한국어 자연스러운 보이스오버
- 저작권 자유로운 배경음악
- 2회 수정 포함
- 화장품법 컴플라이언스 체크 포함

## 흐름
1. (월) 제품 사진 + 기본정보 제출
2. (화) 3가지 컨셉 제시
3. (수) 피드백 수집
4. (목) 3개 완성본 제시
5. (금) 최종 전달 (Notion 링크)

## 법규 준수
우리는 모든 광고가 화장품법 및 의료광고심의 기준을 충족하도록 검토합니다.
(구체적인 체크리스트는 전달 시 포함)
```

### Day 5: Close or follow-up

- If client signs: great. Move to intake.
- If client hesitates: offer 48-hour "hero shot only" test (1 image, ₩200K, 24-hour turnaround). Lower barrier.
- If client ghosts: 1 follow-up after 1 week. Then archive.

---

## 8. Delivery Flow (Step-by-Step)

From client product photo to final delivery package.

```
Input: Product photo (1000x1000px+)
  ↓
Concept Brief (Claude Sonnet, 20 min)
  ↓
Hero Images (Veo 3, 3x, 60 min)
  ↓
Motion Video (Higgsfield Pro, 3x, 90 min)
  ↓
Voiceover (ElevenLabs, 3x, 30 min)
  ↓
Background Music (Suno, 3x, 15 min)
  ↓
Rough Cuts (ffmpeg, 60 min)
  ↓
Client Feedback (async, 24 hours)
  ↓
Polish & Revise (2 hours, 2 rounds included)
  ↓
Final QA (30 min, ship-worthy checklist)
  ↓
Delivery Package (Notion + MP4 download link)
```

**Total time: ~12 hours across 4 days (parallel work reduces wall-clock time)**

### Delivery package structure (in Notion):

```
[Client Name] / [Product] / Final Delivery

├─ 📹 Videos (3 MP4s embedded)
│  ├─ Ad 1: [Concept] (30 sec)
│  ├─ Ad 2: [Concept] (30 sec)
│  ├─ Ad 3: [Concept] (30 sec)
│
├─ 📋 Usage Rights
│  ├─ Your company may:
│  │  ├─ Post on social (Naver SmartStore, Instagram, TikTok, YouTube)
│  │  ├─ Run paid ads (Meta, Google, Naver)
│  │  ├─ Modify/trim/re-edit (using our MP4 as base)
│  ├─ Your company may NOT:
│  │  ├─ Sell/resell the raw MP4 files
│  │  ├─ Rebrand as your own creative studio (credit: "by Service V" optional but appreciated)
│
├─ 📝 Cosmetics Law Checklist (화장품법)
│  ├─ No exaggerated efficacy claims (e.g., "cure", "医治")
│  ├─ No prohibited ingredients mentioned
│  ├─ No unproven benefits (compare with approved claims on MFDS database)
│  ├─ Voiceover matches visual claims
│  ├─ Result: APPROVED for posting / REQUEST REVIEW / REJECTED
│
├─ 🎤 Voice & Music Credits
│  ├─ Voiceover: [ElevenLabs voice name] — royalty-free
│  ├─ Music: [Suno track name] — commercial use included
│
├─ 📊 Performance Recommendations
│  ├─ Best platforms: Naver SmartStore, Instagram (Reels), TikTok
│  ├─ Target audience: [from brief]
│  ├─ Suggested A/B test: these 3 ads vs. your current best-performing ad
│
└─ 💾 Download Links
   ├─ All 3 MP4s (zip, 1080x1920, H.264)
   ├─ Optional: individual MP4s
   └─ Expiry: 30 days (contact us to refresh)
```

---

## 9. Quality Gates: Ship-Worthy Checklist

Before any ad leaves your hands:

**Visual (60 sec review per video)**
- [ ] Aspect ratio is exactly 9:16 (no black bars, no crop distortion)
- [ ] Product is recognizable in the first 3 seconds
- [ ] Color grade matches brand (test on 3 different phone models + desktop)
- [ ] No blur, artifacting, or compression noise (especially in text)
- [ ] If hero image includes text, it's readable at 360px width minimum

**Audio (30 sec review)**
- [ ] Voiceover is audible at -20dB volume (not mumbled)
- [ ] No harsh plosives or mouth clicks
- [ ] Background music doesn't overpower voiceover
- [ ] Levels: VO at -3dB, music at -12dB, no peaking above 0dB
- [ ] Music matches pacing (slow for luxury, upbeat for playful)

**Compliance (화장품법 audit, 5 min)**
- [ ] No medical claims ("cure", "treat", "heal", "prevent")
- [ ] No exaggerated skincare claims without substantiation
- [ ] Voiceover text matches visual claims exactly
- [ ] If using before/after, disclaimer is present (not shown in this format, note for client)
- [ ] No prohibited ingredients or false benefit language

**Technical (2 min automated check)**
- [ ] File size: <50MB
- [ ] Duration: exactly 30 seconds (±1 frame)
- [ ] Codec: H.264 (libx264), 1080x1920, 30fps, AAC audio
- [ ] Metadata: includes brand name in title, no proprietary tags

**Mobile playback (1 min real-world test)**
- [ ] Play on actual phone (iOS Safari, Instagram app, TikTok app)
- [ ] No audio sync drift
- [ ] Starts cleanly at 0 seconds (no pre-roll lag)

**If any checkbox is FALSE:** do not ship. Regenerate that component.

---

## 10. Competitive Playbook

When a prospect mentions a competitor, here's what to say.

### vs. sadarifilm.com (전통 영상 제작사)

**Their position:** "Professional videographers, real actors, custom shoots"

**Your counter:** "sadarifilm is built for TV commercials (3–4 week timeline, ₩5M+). We're built for social (5 days, ₩500K). If you need speed and volume, we win. If you need celebrity talent, they win."

**When to use:** prospect mentions "sadarifilm quoted us but timeline is too long"

### vs. premier.ai.kr (AI 광고 제작 플랫폼)

**Their position:** "DIY AI ad generation, self-service, cheaper"

**Your counter:** "premier.ai is a tool; we're a service. They give you access to an API and say 'figure it out.' We take your product photo, handle the entire workflow (concepts, voiceover, music, legal), and deliver something client-ready. You get results, not tools."

**When to use:** prospect says "why not just use an AI platform ourselves?"

### vs. aidonna.kr (AI e-commerce 마케팅)

**Their position:** "Full e-commerce suite: inventory, ads, analytics"

**Your counter:** "aidonna is general e-commerce. We specialize in cosmetics law and video ad production. Cosmetics requires a separate compliance playbook (화장품법, 의료광고심의). That's baked into every ad we make. If you use aidonna's generic templates, you risk legal issues. We can't be outrun on compliance."

**When to use:** prospect is already using aidonna for everything else

### Generic positioning line

Use when you're unsure of the competitor:

"We're not competing on being the cheapest or the most feature-rich. We're competing on being the fastest, most compliant path from product photo to profitable ad. You hand us a photo Monday, you're running ads Friday. We handle the legal stuff. That's the trade-off."

---

## 11. Cosmetics Ad Law Lint (화장품법 체크리스트)

Clients will ask: "Is this legal to post?" Here's your reference.

**What you CANNOT say in cosmetics ads:**

- Medical claims: "cure", "treat", "heal", "prevent disease", "의료용"
- Unsubstantiated efficacy: "most effective", "clinically proven" (unless you have 3rd-party studies)
- Impossible claims: "reverse aging", "erase wrinkles" (tighten/minimize OK)
- False origin: "Korean ginseng" if it's synthetic ginseng extract
- Prohibited ingredients: anything on the MFDS banned list (formaldehyde, lead, etc.)

**What you CAN say:**

- Descriptive benefits: "moisturizes", "brightens", "softens", "provides hydration"
- Performance language: "helps reduce appearance of", "may improve", "supports"
- Ingredient highlights: "contains 90% centella asiatica", "infused with niacinamide"
- Before/after: if photo-based, must include small-print disclaimer (not for video ads, client responsibility)

**Your role in compliance:**

1. After drafting voiceover, run through MFDS database (cosmetics.mfds.go.kr) and search for prohibited terms
2. Create simple checklist in the delivery Notion page
3. Flag any high-risk claims for client review BEFORE finalizing
4. Include line in the delivery package: "Client is responsible for final legal review per 화장품법 §62 (advertising standards)."

**Reference:**
- MFDS cosmetics database: https://cosmetics.mfds.go.kr
- Prohibited claims list: 화장품법 §62 (의약품이 아님을 나타내는 광고)

---

## 12. Risks and Known Gaps

**Pre-launch blockers (currently holding launch):**

1. **Agency brand name not decided**
   - Affects: all cold DM copy, Notion client DB branding, Service V landing page
   - Impact: HIGH (communication confusion with 영범, client professionalism)
   - Timeline: decide by EOD Tuesday 2026-05-12
   - Recommendation: 3-letter name (VID, ADS, PLIX, or Korean equivalent)

2. **Stack API keys not yet secured**
   - Affects: integration tests, dogfood reel
   - Impact: CRITICAL (blocks all launch tasks)
   - Timeline: must complete by EOD Monday 2026-05-12
   - Owner: You (Keonhee)

**Post-launch risks:**

3. **Veo 3 API latency**
   - Issue: Google Vertex Veo 3 generation can take 3–5 minutes per image
   - Workaround: run all 3 Veo 3 calls in parallel on first day of sprint
   - Fallback: if Veo 3 fails, use Higgsfield's built-in image generation (lower fidelity, faster)

4. **Higgsfield Korean text rendering**
   - Issue: text prompts with Korean characters sometimes fail in motion generation
   - Workaround: keep product name in English or emoji; voiceover carries the Korean messaging
   - Fallback: regenerate without text overlay; add text in post-production (ffmpeg subtitle filter)

5. **Suno commercial licensing**
   - Issue: Suno's terms say Pro subscription allows commercial use, but verify on each track
   - Workaround: Always download + test each track's license metadata before using
   - Fallback: maintain a "approved music" library of confirmed tracks

6. **ElevenLabs Korean voice quality variance**
   - Issue: cloned Korean voices can sound unnatural; default Korean voices are better
   - Workaround: use default Korean female voice (no cloning) for MVP phase
   - Timeline: revisit voice cloning after 5 successful projects

**Known limitations (document for client conversations):**

- Voiceover cannot replicate celebrity vocal tone (Suno Gen music can match vibe, not exact voice)
- Product photo must be at least 1000x1000px (lower res = visible pixelation in hero shot)
- Revisions included: 2 rounds per project. Additional rounds: ₩100K each.
- Turnaround is 5 business days (Mon–Fri). Weekend requests quoted at +₩200K rush fee.

---

## 13. Quick Reference Commands

**Check all API keys:**
```bash
cd projects/ai-agency/services/video
cat .env | grep API
```

**Run integration test:**
```bash
cd projects/ai-agency/services/video
python test_stack.py
```

**Test Higgsfield Pro:**
```bash
curl -X POST https://api.higgsfield.ai/generate \
  -H "Authorization: Bearer $HIGGSFIELD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"hf-motion","input":"test image","duration":10}'
```

**Test ElevenLabs:**
```bash
curl https://api.elevenlabs.io/v1/voices \
  -H "xi-api-key: $ELEVENLABS_API_KEY"
```

**Generate ffmpeg stitch script:**
```bash
python projects/ai-agency/services/video/gen_ffmpeg_stitch.py \
  --video dogfood_lume/videos/hero_1.mp4 \
  --voiceover dogfood_lume/audio/voiceover/concept_1.mp3 \
  --music dogfood_lume/audio/music/bg_music_1.mp3 \
  --output dogfood_lume/final/ad_concept_1_final.mp4
```

**Deliver to Notion (one-liner):**
```bash
python projects/ai-agency/services/video/notion_deliver.py \
  --client-name "Brand Name" \
  --product-name "Product" \
  --video-paths "ad_1.mp4,ad_2.mp4,ad_3.mp4" \
  --notion-token $NOTION_API_KEY
```

---

## 14. Decision Log

| Date | Decision | Status | Owner |
|---|---|---|---|
| 2026-05-11 | Write Service V Operating Manual | DONE | Keonhee |
| 2026-05-12 | Signup for Higgsfield Pro + ElevenLabs + Suno + Veo 3 | TODO | Keonhee |
| 2026-05-12 | Build + pass integration test | TODO | Keonhee |
| 2026-05-13 | Generate dogfood LUME reel (3 final ads) | TODO | Keonhee |
| 2026-05-14 | Decide agency brand name | TODO | Keonhee + 영범 |
| 2026-05-14 | Launch cold DM outreach (first 5 leads) | TODO | Keonhee |

---

## 15. FAQ

**Q: How long until I can pitch a real client?**
A: After dogfood + integration tests pass (Wednesday). Pitch starting Thursday. First paying client by following week.

**Q: What if Veo 3 is slow? Can I skip it and just use Higgsfield?**
A: Yes. Hero images will be lower fidelity but videos will still be usable. Adjust pricing to ₩400K–₩600K.

**Q: Do I need to hire someone to handle production?**
A: Not for MVP phase. Once you hit 4+ projects/month, consider hiring a part-time video editor to handle ffmpeg stitching + QA. Until then, you can do it yourself (3 hours per project is manageable).

**Q: Can I re-use music and voiceovers across clients?**
A: For music: no (each Suno generation is unique and tied to that project). For voiceover: no, to protect brand differentiation. Each project must be unique (forces freshness).

**Q: What's your cuttoff for "not cosmetics"?**
A: If the product contains active pharmaceutical ingredients (vitamins, sunscreen, acne treatments), it falls under 의약외품 (quasi-drug) not 화장품. Different legal rules. Flag immediately and refer to compliance expert.

**Q: How do I handle rejections?**
A: Note in Notion (reason, date, follow-up plan). Reach back after 3 months with new positioning or pricing. Don't burn bridges.

---

**Document created:** 2026-05-11  
**Last reviewed:** 2026-05-11  
**Next review:** 2026-05-25 (post-launch, after first 2-3 clients)
