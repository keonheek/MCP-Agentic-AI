# Service A Operating Manual
## AI Automation for D2C

**Last updated:** 2026-05-11  
**For:** Daily operations, sales execution, delivery  
**Owner:** Keonhee + 영범 (lead-sourcing partner)

---

## 1. Service A at a Glance

### What is Service A?

Automated lead capture, enrichment, and CRM integration for e-commerce brands. Turns website visitors into qualified leads within 24 hours. No more manual form collection. Built on Claude + Make.com webhooks + n8n backend.

### Single Defensible Position

"Speed-to-lead for beauty D2C." We position exclusively in the cosmetics vertical (화장품 D2C). We own this wedge, not horizontal automation.

### ICP (Ideal Customer Profile)

- D2C beauty/cosmetics brands (스킨케어, 뷰티 스타트업)
- Monthly ad spend: 500K~3M KRW
- CRM: Naver PPC + Instagram ads + Naver Shopping
- Current lead process: manual form collection, no nurture, low conversion
- Decision maker: Marketing Manager or CEO (startup)
- Deal size: comfortable with 500K~3M monthly retainers

### The Tier Ladder

| Tier | Name | What Client Gets | Setup | Monthly | TCO (Year 1) |
|------|------|------------------|-------|---------|-------------|
| 1 | **DEMO** | Webhook proof-of-concept on client's domain | Free | Free | Free |
| 2 | **STARTER** | Lead capture + Naver Shopping CSV export + manual nurture | 500K | 200K | 2.9M |
| 3 | **D2C STACK** | Lead capture + Naver/Instagram enrichment + email sequence setup | 1.2M | 400K | 5.8M |
| 4 | **PIPA Tier P** | Everything above + SMS automation + compliance audit + lead scoring | 3M | 500K | 9M |

**Positioning rule:** Always lead with DEMO. Demo = no objection, no money. If they ask "how much," mention STARTER (500K upfront, 200K/month). If they press for more features, jump to PIPA Tier P (the "everything" tier).

---

## 2. Five Products at a Glance

### Product Taxonomy

Service A owns 5 distinct products under one umbrella. Learn each, know which ICP buys which.

| Product | What It Does | Ideal Client | Setup $ | Monthly $ | Notes |
|---------|--------------|--------------|---------|-----------|-------|
| **Speed-to-Lead** | Webhook captures leads + auto-enriches from Naver/Instagram ads | SMB D2C (500K~1M ad spend) | 500K | 200K | Entry point. Most common first sale. |
| **Automation Workflows** | Pre-built n8n workflows: lead routing, slack notifications, CRM sync | D2C brands using Zapier/Make already | 1M | 300K | Upsell to STARTER after 2-3 months. |
| **SaaS Integrations** | Connect client's own SaaS stack to Claude for document parsing, lead scoring | Mid-market (lead scoring use case) | 1.2M | 400K | Heavier lift. Sell only if client mentions "AI" first. |
| **PIPA Tier P** | Compliance-audited SMS + email + lead scoring + monthly board report | Brands doing 2M+ monthly spend | 3M | 500K | Highest margin. Needs compliance sign-off. |
| **GEO SEO Blog** | AI-generated blog content for organic lead capture (backup product) | Brands with organic channel | 500K | 250K | Don't lead with this. Mention only if client asks about content. |

**Daily operating rule:** DEMO and STARTER are 80% of your pipeline. PIPA Tier P is 20% but highest margin. GEO/SaaS Integrations are specialists. Don't mention them unless ICP shows interest in that specific use case.

---

## 3. Daily Operating Rhythm

### Morning Standup (09:00)

1. Open Telegram. Check A1-A6 fleet digest from overnight.
2. Open "Service A Prospect Sheet" (shared with 영범). Mark prospects from yesterday's leads as "New" or "Follow-up".
3. Read overnight responses in DMs. Move repliers to "Warm" status.
4. Review calendar: any demos booked? Any PIPA audit calls? Prep talking points 30 min before first call.

### Morning Execution (09:15-12:00)

1. **Warm outreach (15 min):** DM 2-3 warmest leads from yesterday's digest. Use Sales Flow template below.
2. **Follow-ups (10 min):** Message prospects who said "maybe" 3 days ago. Simple: "Did you see the demo? Questions?" One line only.
3. **Fleet check (5 min):** A1 fleet = running today? Check Telegram for "A1 complete" message. If no message by 08:00, manually trigger:
   ```bash
   curl -X POST https://api.telegram.org/bot[BOT_TOKEN]/sendMessage \
     -d chat_id=[KEONHEE_CHAT_ID] \
     -d text="A1: Trigger manual sweep"
   ```

### During Day (12:00-18:00)

- **Respond to inbound:** DM replies come in clusters (10:00-12:00, 14:00-16:00). Check every 2 hours.
- **Demo requests:** If someone asks for a 15-min demo, reply in <2 hours. Use demo-script.md. Book call within 24h.
- **Delivery:** If a client is in STARTER setup phase, check n8n webhook logs. Any errors? (See Delivery Flow below.)

### Evening Standup (17:30)

1. Count inbound replies. Log to Prospect Sheet.
2. Check M1 (Orientation) fleet push. M1 tells you who's ready for a demo vs needs more nurture.
3. Update Telegram notes: "3 warm leads, 1 demo booked tomorrow, 0 sales."
4. Reset for next day.

### Weekly (Friday)

- Audit Prospect Sheet for stale leads (>7 days, no reply). Mark for breakup email or archive.
- Check PIPA audit queue. Any Tier P clients awaiting compliance review? If yes, schedule 30-min call.
- Log weekly revenue: # of STARTER sales, # of PIPA sales, total MRR gained.

---

## 4. Lead-Gen Pipeline (A1-A6 Fleet)

### Fleet Diagram

Six agents run in sequence, daily, 06:00 KST:

```
A1: Telegram Digest (list new D2C leads from overnight scrapers)
  → A2: Lead Enrichment (Naver/Instagram lookup, scoring)
  → A3: Conversation Starter (DM hook + copy generation)
  → A4: Urgency Prompt (recent product launch, new feature, trend angle)
  → A5: Cold Email Fallback (if DM unavailable, email subject + body)
  → A6: Lead Logger (push to Prospect Sheet, set followup date)
```

### What You See Each Morning

Telegram message from A1, format:

```
[A1 Digest - 2026-05-12]

3 new leads | 7 nurture-track | 1 ready to demo

HOTTEST (Call Today):
- Avestar (skin care D2C, 1.2M/mo spend) — just launched new line. A4 generated hook: "Your new serum is live. 40% of visitors bounce. We catch the other 60%."
- Yuna Beauty (makeup, 800K/mo) — DM replied to previous outreach 3 days ago, been silent since.

WARM (Follow-up This Week):
- Puritree (organic cosmetics, 600K/mo)
- Derm+ (dermatologist brand, 900K/mo)

NURTURE TRACK (Touchpoint Due):
- [5 more names with dates]

Next trigger: A2 enrichment complete by 08:00.
```

### What You Do with the Digest

**Hottest tier:** Make 2-3 personalized DMs before 10:00. Use template from Sales Flow below.

**Warm tier:** Send one-liner follow-up message. No sell. Example: "Saw your product launch — did you want to test our lead capture for the new line?"

**Nurture track:** Automated. You don't act. A6 will send a weekly touchpoint.

### Prospect Sheet URL

Location: Shared Google Sheet with 영범. Columns:

- Company Name
- Contact (name + KakaoTalk/Instagram handle)
- Ad Spend (estimated)
- Status (New / Warm / Demo Booked / Proposed / Won / Dead)
- Last Outreach (date)
- Next Action (date)
- Notes (product angle, objection, personal detail)

**Daily:** Mark A1 new leads as "New". Move responders to "Warm".

**Weekly:** Review "Dead" column. Archive anyone >14 days with no response.

### Manual Trigger (If A1 Fails)

Location: `agents/service_a_leadgen/`

```bash
cd C:\Users\keonh\Dev\MCP_Agentic_AI\agents\service_a_leadgen
python a1_telegram_digest.py --date 2026-05-12 --force
```

---

## 5. Sales Flow: First DM to Close

### Step 1: Cold Outreach (A1-A4 Generate Hook)

**When:** Morning standup, for "hottest" tier leads.

**Template:**
```
[Hook from A4] 
예: "Avestar님, 새 라인 론칭 축하합니다. 론칭 후 웹사이트 방문자 40%가 나가간다고 하던데..."

One-liner ask:
"15분 가량 고객사 Lead Capture 시스템 데모 보여드려도 될까요?"

Sign-off:
"건희 / AI Automation @ AI Agency"
```

**Golden rule:** One message. One ask. No paragraph. If they don't respond in 3 days, move to Step 2.

### Step 2: First Follow-up (Day 3, No Reply)

**Template:**
```
"혹시 바쁘신가 해서 다시 연락드렸습니다. 데모는 정말 15분이면 끝나요. 편한 시간 있으신가요?"
```

**If still no reply by Day 7:** Move to "Dead" or "Nurture" track. Don't spam.

### Step 3: Warm Reply Received (They Say "Maybe")

**Your move:** Book a demo within 24 hours.

**Template:**
```
"감사합니다! 내일 14시가 어떠신가요? Zoom 링크 보내드릴게요.

데모에서 보여드릴 것:
- 1분: 고객 웹사이트에 어떻게 적용되는지
- 3분: 실시간 Lead Capture 화면
- 5분: Naver/IG 광고 연동 효과
- 6분: 비용 (DEMO는 무료)

혹은 더 좋은 시간 있으신가요?"
```

### Step 4: Demo Call (15 min Zoom)

**Before call:** Open demo-script.md. Review the exact talking points and demo flow.

**Script outline (from demo-script.md):**
1. **Warmup (1 min):** "Thanks for taking 15 min. I know you're busy. Let me show you something that takes 3 days of work and turns it into 24 hours."
2. **Problem (1 min):** "You run ads on Naver/Instagram. You get traffic. But 40-60% never fill out a form. They just bounce."
3. **Demo (3 min):** Screen share. Show webhook firing on a test product page. Show enrichment happening in real time (name + phone auto-populates from Instagram).
4. **Proof (2 min):** "This is live. We've tested it on 7 D2C brands already. Average: 60% more leads, same ad spend."
5. **Offer (2 min):** "Starting point is STARTER: 500K upfront, 200K per month. That includes the webhook, Naver/Instagram integration, and 30-day onboarding. Want to try DEMO first? No cost, 3 days, shows exactly what you'd get."
6. **Close (1 min):** "Does this solve the problem?" Listen. Move to Step 5.

**After demo:** Send follow-up message within 30 min.

```
"고마워요. 어땠어요? 

일단 DEMO로 시작해서 실제로 효과 보시고 나서 STARTER로 결정하셔도 괜찮아요. 
언제 시작해볼까요?"
```

### Step 5: Proposal (If They Say "Yes")

**If they said "Yes" in the demo call:**

```
"완벽해요. STARTER 계약서 보내드릴게요. 내일까지 가능할까요?

요약:
- Setup: 500,000 KRW (일회비)
- Monthly: 200,000 KRW
- Term: 1년 (30일 cancellation notice)
- Included: Webhook setup, Naver/IG enrichment, Slack/email integration, 30일 onboarding

계약서 사인하시면 내일부터 onboarding 시작할게요."
```

**Use:** `projects/ai-agency/products/speed-to-lead/proposal-template.md` as the actual document. Fill in:
- Company name
- Contact person
- Tier (STARTER / D2C STACK / PIPA Tier P)
- Start date
- Monthly price
- SLA (see sla.md for terms)

**Send as:** PDF via KakaoTalk. Ask them to sign and return.

### Step 6: Close + Onboarding (Contract Signed)

Once signed, move to Delivery Flow (Section 6 below).

---

## 6. Delivery Flow by Product

Each product has an onboarding checklist. Use them.

### STARTER Onboarding (Most Common)

**Duration:** 30 days  
**Timeline:** Day 1 signup to Day 30 live traffic  
**Your role:** 3 check-ins (Day 1, Day 15, Day 29)

**Checklist (from onboarding.md):**

1. **Day 1: Kickoff call (30 min)**
   - Get client's product page URL + current form field names
   - Get Instagram ad account credentials (or Naver PPC login)
   - Schedule Day 15 check-in
   - Send welcome email + onboarding doc

2. **Day 3-7: Webhook deployment**
   - Frontend dev (yours or client's) adds webhook snippet to product page:
   ```html
   <script src="https://webhook.ai-agency.co/capture.js"></script>
   <script>
     AICapture.init({
       apiKey: "[STARTER_KEY]",
       enrichFrom: ["naver", "instagram"]
     });
   </script>
   ```
   - Test on staging. Capture a test lead. Verify it appears in their CRM within 60 sec.
   - If client has no dev, you deploy via n8n. Takes 1-2 hours.

3. **Day 8-10: Integration setup**
   - Connect to client's CRM (Naver PPC, Naver Shopping, or email list)
   - Test: Submit form on product page. Verify lead appears in CRM within 2 min.
   - Document: "Lead is now auto-synced every 60 seconds."

4. **Day 15: First checkpoint**
   - Call client. Ask: "Any leads captured yet?"
   - If yes (common): Show dashboard. Celebrate first wins.
   - If no (rare): Debug. Check webhook logs (see Troubleshooting below). Fix by Day 20.

5. **Day 25-29: Handoff + training**
   - Show client the dashboard (Notion + Slack alerts)
   - Teach: How to export lead list, how to pause/resume webhook
   - Get feedback on first 2+ weeks of leads. Document: "Cost per lead: X KRW"

6. **Day 30: Go-live**
   - Send final checklist: "You're live. Leads will auto-capture. Monitor dashboard."
   - Set recurring: Monthly check-in call (first Monday of each month)

**Files to reference:**
- `projects/ai-agency/products/speed-to-lead/onboarding.md` (full step-by-step)
- `projects/ai-agency/products/speed-to-lead/sla.md` (guarantees, SLOs)

### PIPA Tier P Onboarding (Compliance-Heavy)

**Duration:** 45 days  
**Difference from STARTER:** SMS consent forms + compliance audit + monthly board report

**Checklist (additions only):**

1. **Day 3: PIPA consent template**
   - Prepare SMS opt-in form for client's website
   - Clause: "고객사는 광고성 정보를 수신하는 것에 동의합니다. 동의하지 않으시면 체크 해제하세요."
   - Client approves + deploys

2. **Day 20: Compliance audit**
   - Audit client's lead capture process against PIPA (Personal Information Protection Act, Art. 37-2)
   - Check: Consent collected? Data deletion policy clear? SMS frequency <= 3/day?
   - Document findings. Any violations? File compliance report.
   - Send to client: "PIPA 준수 현황" doc

3. **Day 30 onwards: Monthly board report**
   - Pull data: leads captured, conversion rate, cost per lead, SMS engagement
   - Format as 1-page Notion doc. Send to client's CMO/CEO.
   - Include: "Growth trend", "Bottleneck", "Recommendation for next month"

**Files:**
- `projects/ai-agency/products/pipa-tier-p/onboarding.md` (PIPA-specific steps)
- `projects/ai-agency/products/pipa-tier-p/compliance-audit.md` (PIPA checklist)
- `projects/ai-agency/products/pipa-tier-p/monthly-board-report-template.md`

### Automation Workflows + SaaS Integrations (If Client Buys)

These upsell to existing STARTER clients. Deliver only after Day 30 of STARTER is done.

**Rule:** Don't pitch in first call. Offer in Month 2 check-in. "Your leads look good. Now, do you want them auto-routed to your sales team? That's an Automation Workflows add-on."

---

## 7. Pricing Decision Tree

Use this to avoid leaving money on the table or pitching the wrong tier.

```
Does prospect mention "AI"?
├─ YES → Pitch PIPA Tier P (full suite, compliance, highest margin)
└─ NO → Does prospect have >1.5M/mo ad spend?
    ├─ YES → Pitch D2C STACK (Naver + Instagram + email sequence)
    └─ NO → Does prospect already use a CRM?
        ├─ YES → Pitch STARTER (simple, fast deployment)
        └─ NO → Start with DEMO (free, 3 days, builds trust)
            After DEMO works: Upgrade to STARTER

Does prospect ask "How much?"
├─ Say: "DEMO is free. If you want to go live, STARTER is 500K upfront, 200K/month."
└─ If they push back: "That's lead capture only. If you want SMS too, that's PIPA Tier P at 3M upfront, 500K/month. Your choice based on your budget."

Does prospect want "discount"?
├─ NO discount for STARTER (already cheap at 500K)
├─ For D2C STACK: Offer extended term (pay 2 years, get 10% off monthly)
└─ For PIPA Tier P: Only offer discount if Deal Size > 2M KRW/month. Max 10% off.

Rule: DEMO has no price anchor. STARTER is the anchor. Anything below STARTER is free (DEMO only). Anything above is a custom conversation.
```

---

## 8. Competitive Playbook

### Competitive Set

| Competitor | Strength | Your Counter |
|---|---|---|
| **TripleSong** | SMS automation, established brand | We're faster to deploy (3 days vs 2 weeks) + cheaper (200K vs 500K/mo) |
| **AI BRIDGE** | Lead scoring, ML-driven | We focus on D2C only, not horizontal. Our default enrichment beats their generic model. |
| **Channel Talk** | Customer service chat, big Korean brand | They're chat. We're lead capture. Different product. Don't compete; position complementary. |
| **리부티너** | Beauty D2C automation specialist | Strongest competitor. Price is similar. We differentiate on speed. Lead with DEMO proof. |

### If Prospect Mentions TripleSong

**What they'll say:** "TripleSong은 이미 쓰고 있는데..."

**Your response:**

```
"좋아요. 그럼 TripleSong이 뭘 해주는지 물어봐도 될까요?"

[Listen to what they use TripleSong for]

"알겠습니다. 우리가 차이나는 부분:
- TripleSong은 보낸 메시지 추적. 우리는 그 전 단계, 웹사이트에서 고객을 잡아냅니다.
- 우리 데모 보시면 'TripleSong에 넣을 고객 리스트'가 매일 자동으로 쌓이는 거 보게 되실 거예요.
- 먼저 lead capture 해야 SMS 보내죠?"

Ask: "3일 데모로 해볼래요? TripleSong이랑 연동도 되니까."
```

**Key insight:** You're upstream of TripleSong. You feed them data. Position as complementary, not competitive.

### If Prospect Mentions AI BRIDGE

**What they'll say:** "AI BRIDGE도 AI 자동화 하던데..."

**Your response:**

```
"맞아요. AI는 맞는데, 우리는 좀 특화했어요.
- AI BRIDGE는 모든 업계 (화장품, 패션, 전자제품 다 해요).
- 우리는 화장품 D2C만 한다. 그래서 Instagram lead enrichment가 정확해요.
- 한 예: 보글(실제 고객사) 웹사이트에 방문한 사람이 이전에 우리 광고 본 적 있으면, 우리는 그걸 알아낸다.
- 데모 보시면 ' 아, 이거는 화장품 고객만 될 수 있겠네' 하실 거예요."

Ask for DEMO.
```

**Key insight:** You win on specialization. Generalists lose on depth.

### If Prospect Mentions Channel Talk

**What they'll say:** "Channel Talk 써봤는데 안 좋았어..."

**Your response:**

```
"Channel Talk은 고객이 온 다음에 chat 거는 도구잖아요.
우리는 그 전, 고객이 올 때까지 기다리는 부분을 자동화해요.
예를 들어, 광고 봤는데 Form 안 채우고 나가는 사람들.
우리가 그 사람들을 잡아내고 자동으로 연락하는 거죠."

Don't bash Channel Talk. Position as different layers.
```

---

## 9. Operational Fleets Cheat Sheet

Three fleets push messages to your Telegram daily. Here's what each means and how to respond.

### Fleet M1: Orientation

**What it does:** Evaluates which leads are ready for a demo vs. need more education.

**Message format:**
```
[M1 Orientation - 2026-05-12]

READY FOR DEMO (Call Today):
- Yuna Beauty (1st touch was 5 days ago, 2 replies on outreach)
- Puritree (asked 3 specific questions about integration)

NEEDS 1 MORE TOUCHPOINT (Send Explainer):
- Derm+ (first reply, still skeptical about "lead capture")
- [others]

ACTION: Send explainer email to NEEDS group. Use template below.
```

**Your action:**

For "READY FOR DEMO" group: Send demo booking message immediately.

For "NEEDS 1 MORE TOUCHPOINT" group: Send educational email. Template:

```
"Derm+ 님께,

궁금한 점 감사합니다. 혹시 이런 거 궁금하신 거죠?

'우리 고객이 웹사이트 와서 폼을 안 채우고 나가면, 
우리는 누가 왔는지도 알 수 없고, 어디가 문제인지도 모르잖아요?'

맞죠. 그게 우리 제품이 푸는 문제예요. 
한 번 3일 데모로 직접 보시는 게 가장 빨아요. 
빠시다고 느껴지면, 계속하시면 되고, 아니면 그냥 끝내셔도 돼요."

Action: Book demo within 24 hours.
```

### Fleet M2: Blind Spot

**What it does:** Identifies prospects stuck in your sales process (no reply for 7+ days, replied but then went silent, etc).

**Message format:**
```
[M2 Blind Spot - 2026-05-12]

STUCK (No Reply, 7+ Days):
- Avestar (first DM 2026-05-05, no reply yet) — BREAKUP READY
- Puritree (last contact 2026-05-04, went silent after first reply) — RESCUE READY

RECOMMENDATION:
- BREAKUP: "고마워요. 바쁘신 것 같아서 이번엔 마칠게요. 나중에 필요하면 연락주세요!"
- RESCUE: "혹시 질문 있으신 거 빠진 게 없나요? 말씀해주시면..."

Take action today.
```

**Your action:**

- **BREAKUP:** Send the 1-line "goodbye" message. Mark in Prospect Sheet as "Dead". Move on.
- **RESCUE:** Send the 1-line "checking in" message. If no reply after this, move to BREAKUP.

### Fleet Evolution Loop

**What it does:** Every prospect in your pipeline gets a "next best action" based on where they are in the journey.

**Message format:**
```
[Evolution Loop - 2026-05-12]

NEXT ACTIONS:
1. Yuna Beauty (WARM tier) — Send DEMO booking link. Template: "...데모 가능하신 시간?"
2. Puritree (NURTURE tier) — Send educational email (see template above)
3. Derm+ (DEMO booked, date: 2026-05-14) — Send 24h reminder tomorrow
4. [others with specific actions]
```

**Your action:** Follow the recommendation exactly. Each one is 1-3 lines, no more. The loop is telling you what to do. Just do it.

---

## 10. Cloud Routines Status

Your sales pipeline runs on 5 RemoteTrigger routines deployed in Claude Routines. Each one fires automatically at a set time. Check their status weekly.

### Routine 1: A1 Daily Digest (06:00 KST)

**What:** Pulls overnight lead scrapes, pushes Telegram digest.

**ID:** `routine-a1-telegram-digest`

**Logs:** Check if "complete" message hits Telegram by 08:00 every morning.

**If fails:** Manual trigger:
```bash
curl -X POST https://api.remote.anthropic.com/routines/routine-a1-telegram-digest/trigger \
  -H "Authorization: Bearer [API_KEY]" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Reset:** Disable + re-enable:
```bash
# Disable
curl -X POST https://api.remote.anthropic.com/routines/routine-a1-telegram-digest/disable \
  -H "Authorization: Bearer [API_KEY]"

# Re-enable after 30 sec
curl -X POST https://api.remote.anthropic.com/routines/routine-a1-telegram-digest/enable \
  -H "Authorization: Bearer [API_KEY]"
```

### Routine 2: M1 Orientation (13:00 KST)

**What:** Evaluates warm leads, tells you who's demo-ready.

**ID:** `routine-m1-orientation`

**Logs:** Check Telegram by 14:00.

**If fails:** Manually trigger using same pattern as A1 above. Replace `routine-a1-telegram-digest` with `routine-m1-orientation`.

### Routine 3: M2 Blind Spot (17:00 KST)

**What:** Finds stuck prospects, recommends breakup or rescue.

**ID:** `routine-m2-blind-spot`

**Logs:** Check Telegram by 18:00.

### Routine 4: Evolution Loop (09:00, 13:00, 17:00 KST)

**What:** Gives next best action for every prospect in your pipeline.

**ID:** `routine-evolution-loop`

**Fires 3x daily.** Check Telegram after each window.

### Routine 5: PIPA Audit Scheduler (Weekly, Friday 14:00)

**What:** Checks if any Tier P clients are due for compliance review.

**ID:** `routine-pipa-audit-scheduler`

**Logs:** Check Telegram Friday afternoon. If a client is due, you'll see: "X clients overdue for compliance audit. Schedule 30-min call."

**Action:** Reply in Telegram thread with date + time. Routine will send calendar invite to client.

### Master Status Check (Weekly)

Every Friday at 17:00, run this to see overall health:

```bash
curl -X GET https://api.remote.anthropic.com/routines/status \
  -H "Authorization: Bearer [API_KEY]" \
  -H "Content-Type: application/json" | jq '.routines[] | select(.owner=="keonhee") | {name, status, last_run}'
```

**Expected output:**
```
{
  "name": "routine-a1-telegram-digest",
  "status": "enabled",
  "last_run": "2026-05-12T06:00:00Z"
}
```

If any routine shows `"status": "error"`, disable + re-enable it.

---

## 11. Risks and Known Gaps

### Risk 1: Smart Store Customer Endpoint

**Problem:** Naver Smart Store doesn't expose customer enrichment via API. You can pull orders, but not customer attributes (age, past purchases).

**Impact:** STARTER clients using Smart Store only get order history enrichment, not demographic enrichment.

**Mitigation:** At Day 3 kickoff, ask client: "Do you use Instagram ads?" If yes, we enrich from Instagram. If no, offer upgrade to D2C STACK (adds email list matching).

**Track:** Note in Prospect Sheet if "Smart Store only" client. Flag for monthly check-in.

### Risk 2: KakaoTalk Channel API Approval Delay

**Problem:** If client wants to send KakaoTalk messages to leads (not SMS), they need KakaoTalk Channel approval. Takes 3-5 business days.

**Impact:** SMS is faster. KakaoTalk is higher engagement but slower to deploy.

**Mitigation:** On Day 3 kickoff, if client wants KakaoTalk: "Let me start SMS while you get Channel approval. Once you're approved, we'll switch." Offer to manage the approval process (fill forms, submit).

**Track:** Add to onboarding checklist for any PIPA Tier P client.

### Risk 3: PIPA Article 37-2 Deadline

**Problem:** PIPA Article 37-2 (SMS consent) tightened in 2024. Your compliance template is from 2025. May be out of date by 2026-Q4.

**Impact:** If audit finds non-compliance, PIPA fines client + damages your reputation.

**Mitigation:** Q1 2026, audit PIPA Article 37-2 current statute + case law. Update compliance-audit.md. Retrain all PIPA Tier P clients.

**Track:** Add to calendar: "PIPA Statute Review Q1 2026".

### Risk 4: n8n Webhook Downtime

**Problem:** If n8n backend (prod automation) goes down, leads stop syncing to client CRM.

**Impact:** Client sees 0 leads for a few hours. Damages trust.

**Mitigation:** 
- Set up n8n uptime monitoring. If downtime > 15 min, get paged.
- Have a backup webhook endpoint (Make.com + ngrok) ready as fallback.
- On Day 1 kickoff, tell client: "We monitor uptime 24/7. If leads stop syncing, you'll hear from us within 15 min."

**Track:** n8n status dashboard is at https://ngrok.keonhee-automation.io/health. Check daily.

### Risk 5: Demographic Data Accuracy

**Problem:** Instagram enrichment pulls user bios + profile data. Accuracy varies (people lie on Instagram).

**Impact:** Cost per qualified lead may be worse than expected (you enrich with bad data, client gets garbage leads).

**Mitigation:** 
- At Day 15 checkpoint, ask client: "Of the first 10 leads, how many look real?" Listen. If <70% quality, investigate.
- Adjust enrichment rules (stricter keyword match, require both Instagram + Naver visibility, etc).
- Document: "First 100 leads had 75% accuracy. By month 2, we expect 85%+."

**Track:** Log quality score in monthly check-in notes.

---

## 12. Common Scenarios FAQ

### Scenario 1: Client Asks for Discount

**Situation:** "We like the product, but 500K is a bit high. Can you go lower?"

**Your response:**

"I get it. Here's what I can do:

Option A: We stick with STARTER at 500K. In return, you commit to 12 months upfront. That's 6.4M total. (No discount, but you save 200K by auto-renewing.)

Option B: You do the DEMO (free, 3 days). Prove it works. Then we talk pricing. Most clients say after the demo, 500K feels cheap.

Which sounds better to you?"

**If they push harder:** "I can't go below 500K on STARTER. That's break-even. But if you want more features, I can show you D2C STACK at 1.2M setup + 400K/mo. Might be worth it if your ad spend is >1.2M/mo."

**Rule:** Don't discount STARTER. If they want lower price, upsell features instead (move them to D2C STACK or offer DEMO as proof).

### Scenario 2: Prospect Ghosts After Demo

**Situation:** You did the demo. They said "looks good." Then radio silence for 5 days.

**Your response (Day 4):**

"고마워요. 혹시 질문이 더 생겼어요?
아니면 일단 DEMO 해보고 시작할래요?"

**Day 7 (if still silent):**

"아, 바쁘신 것 같아서 이번엔 마칠게요. 
나중에 필요하면 언제든 연락주세요. 
응원합니다!"

Mark as "Dead" in Prospect Sheet. Move on.

### Scenario 3: PIPA Audit Requested by Client

**Situation:** Client got a letter from data regulator (PIPC). Asks: "Can you prove we're PIPA-compliant?"

**Your response (same day, urgent):**

"당연하죠. 우리가 해드릴 게:

1. 48시간 내: 고객사 현황 감사 (웹사이트 consent form, SMS frequency, data deletion 정책 확인)
2. 그 다음: Compliance report 제출 (감시자에게 주셔도 돼요)
3. 필요하면: Our compliance expert랑 직접 통화

당황하실 필요 없습니다. 우리는 PIPA-ready 플랫폼입니다."

**Your action:** 
- Open `projects/ai-agency/products/pipa-tier-p/compliance-audit.md`.
- Audit client's setup against the 10-point checklist.
- Generate Compliance Report (1-pager, in Korean). Send within 48h.

**Track:** Log in Notion: "Audit completed 2026-05-12. Status: Pass / Needs Fix".

### Scenario 4: Service A Delivery Slips (Webhook Takes >7 Days)

**Situation:** Client signs contract Day 1. By Day 7, webhook still not deployed. Client is upset.

**Your response:**

"죄송합니다. 상황을 정리해드릴게요:

1. 지금 상태: [현재 진행 상황 명확히]
2. 원인: [시간이 걸린 이유, 예: client's dev team 응답 지연]
3. Recovery plan: 
   - 내일까지 [구체적 단계] 완료
   - [일자]까지 live
4. 보상: 첫 달 유지보수 비용 50% 감면"

**Your action:**
- If delay is on your side: Offer discount or extended trial.
- If delay is on client's side: Blame kindly ("Your dev team needs to review the code"). Offer to do it for them (charge 500K, or eat it if you caused confusion).
- Get back on track by Day 10. Don't let it slip 14+ days.

**Track:** Add post-mortem to Notion. "What went wrong? How do we avoid this next time?"

### Scenario 5: Client Gets 0 Leads in First Week

**Situation:** Week 1 of STARTER. Webhook is live. Zero leads captured. Client is panicking.

**Your response:**

"이건 정상입니다. 여기 이유들:

1. 광고를 아직 안 켜셨거나
2. 광고는 켰는데 방문자가 적거나
3. 웹사이트 트래픽이 오후에만 옴 (아침에 webhook 체크할 때 아무것도 없음)
4. Form을 안 채우던 사람들 = 우리가 자동으로 잡아내는 건데, 그런 사람들이 적은 경우

Day 15 체크인 때 다시 보기로 하고, 저는 'traffic 로그'를 매일 확인하고 있어요. 
문제 되는 게 있으면 제가 먼저 연락드릴게요."

**Your action:**
- Check n8n logs. Is webhook firing at all?
- If webhook is firing: Wait. Most clients see first leads by Day 10-14.
- If webhook is NOT firing: Debug immediately. Is the script deployed? Is API key valid? Call the client's dev team.

**Track:** Add to onboarding.md: "Set expectations: First leads usually Day 7-10."

### Scenario 6: Competitor Mentions "Better AI"

**Situation:** Prospect says, "Your competitor uses GPT-4o. You use Claude. Aren't they better?"

**Your response:**

"좋은 질문입니다. 정답은 no예요. 이유:

1. AI 모델은 도구일 뿐, 중요한 건 '뭘 하는지'.
2. 우리는 화장품 D2C만 하니까, Claude로 학습한 데이터도 화장품에 최적화됐어요.
3. GPT-4o는 일반적. 우리는 특화.

그리고 실제 비교는 'AI 모델명' 아니라 '결과'입니다. 
우리 DEMO 보시고 '이게 GPT-4o보다 낫네' 하실 거예요."

**Key insight:** AI model choice doesn't matter to clients. Speed, accuracy, and depth in the vertical matter. Lead with proof, not model names.

---

## 13. Appendix: File Reference Map

For quick lookup when you're mid-sales or mid-delivery:

| Task | File |
|------|------|
| First demo call | `projects/ai-agency/products/speed-to-lead/demo-script.md` |
| Proposal document | `projects/ai-agency/products/speed-to-lead/proposal-template.md` |
| STARTER SLA terms | `projects/ai-agency/products/speed-to-lead/sla.md` |
| STARTER onboarding steps | `projects/ai-agency/products/speed-to-lead/onboarding.md` |
| PIPA compliance checklist | `projects/ai-agency/products/pipa-tier-p/compliance-audit.md` |
| PIPA onboarding steps | `projects/ai-agency/products/pipa-tier-p/onboarding.md` |
| Monthly board report template | `projects/ai-agency/products/pipa-tier-p/monthly-board-report-template.md` |
| Competitive responses | `projects/ai-agency/products/_shared/battlecard.md` |
| Pricing + positioning strategy | `projects/ai-agency/products/PRICING_AND_POSITIONING_v2.md` |
| A1-A6 fleet code | `agents/service_a_leadgen/` |
| M1/M2/Evolution loop code | `agents/m1_orientation/`, `agents/m2_blindspot/`, `agents/evolution_loop/` |

---

## 14. Quick Reference: Daily Checklist

Print or bookmark this. Use every morning.

```
EVERY MORNING (09:00-12:00):
[ ] Check Telegram: A1 digest arrived?
[ ] Open Prospect Sheet. Mark "New" leads from A1.
[ ] DM 2-3 warmest leads (template in Sales Flow section 5.1).
[ ] Check for overnight replies. Reply within 2 hours.
[ ] Book any demo requests within 24h.
[ ] Check n8n logs for any STARTER client webhook errors.

EVERY AFTERNOON (14:00-17:00):
[ ] Check Telegram: M1/M2/Evolution loop messages arrived?
[ ] Act on M1 (send demo invites) + M2 (send breakup/rescue messages).
[ ] Prepare for any scheduled demo calls (review demo-script.md).
[ ] Check calendar: Any monthly check-ins due? Prep talking points.

EVERY EVENING (17:30):
[ ] Log inbound reply count to Prospect Sheet.
[ ] Update status of in-progress onboardings.
[ ] Check: Any STARTER clients hitting Day 15 checkpoint? Send email.

EVERY FRIDAY:
[ ] Audit Prospect Sheet for stale leads (>7 days, no reply).
[ ] Check Telegram: PIPA audit schedule routine fired?
[ ] Count weekly revenue: # STARTER wins, # PIPA wins, total MRR.
[ ] Check routine health: `curl -X GET https://api.remote.anthropic.com/routines/status`.
```

---

**End of Operating Manual**

Generated: 2026-05-11 | Owner: Keonhee | Partner: 영범
