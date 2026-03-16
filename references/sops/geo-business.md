# SOP: GEO as a Business (South Korea)

_Generative Engine Optimization — getting clients cited by AI systems._

---

## What you're selling

When a potential client's customer asks ChatGPT, Perplexity, or Google AI:
- "Best [product/service type] in Korea"
- "Which [company type] should I use in Seoul"
- "Who are the top [industry] companies in South Korea"

Your client should appear in the answer. Right now most Korean SMEs don't. You fix that.

---

## The audit → rewrite → monitor process

### Step 1 — AI Visibility Audit (1–2 hours per client)

Ask these exact questions across ChatGPT, Perplexity, and Google AI Overview:
1. "[Client's industry] companies in [city/Korea]"
2. "Best [product/service] in Korea"
3. "[Client's company name]" — what does AI say about them?

Document: what's returned, where the client appears (if at all), what competitors appear.

Deliverable: 1-page audit report with screenshots. This is the sales tool.

**Template:** `references/examples/geo-audit-template.md`

---

### Step 2 — Content Rewrite (3–5 hours per client)

Rewrite these surfaces in priority order:

| Surface | Why it matters | Time |
|---------|---------------|------|
| Website homepage (About/Hero) | Most crawled, highest weight | 1.5h |
| Google Business Profile description | Directly feeds Google AI Overview | 30min |
| LinkedIn company page About | High authority signal for B2B | 45min |
| Press releases / blog posts | External citations = AI trust | 1h |
| Product/service descriptions | Long-tail query coverage | 1h |

**GEO rewrite principles:**
- Replace vague claims ("leading company", "quality service") with specific, verifiable ones ("serves 200+ clients in Seoul", "founded 2018", "certified by X")
- Use exact category terms AI would retrieve: not "IT solutions" but "enterprise cloud migration and DevOps consulting"
- Add structured data where possible (schema.org markup on website)
- Cross-platform consistency: same core claims on website, Google, LinkedIn, Naver

---

### Step 3 — Monitor & Iterate (monthly)

Re-ask the same audit questions monthly. Track:
- Which AI platforms cite the client now vs. before
- What exact phrasing triggers a citation
- Competitor positioning shifts

Deliverable: 1-page monthly report with before/after citations.

---

## Pricing (Korean market)

| Package | What's included | Price |
|---------|----------------|-------|
| **Audit only** | AI visibility audit + 1-page report + recommendations | ₩300,000–₩500,000 |
| **One-time rewrite** | Audit + full content rewrite (website, Google, LinkedIn) | ₩1,500,000–₩3,000,000 |
| **Monthly retainer** | Audit + rewrite + monthly monitoring + updates | ₩800,000–₩1,500,000/month |

Start low for first 3 clients (free or cost price) to build case studies. Raise rates once you have 2–3 documented before/afters.

---

## Client acquisition

### Fastest path: SDC Consulting Club
- You're already in the room with companies that need this
- Offer a free audit as a consulting club project — position it as applied AI consulting work
- Convert 1–2 to paid clients from there

### Cold outreach script

Subject: "AI search isn't finding [Company Name] — here's why"

> Hi [Name],
>
> I ran a quick test — asked ChatGPT and Perplexity "[their industry] companies in Korea." [Company Name] didn't appear, but [Competitor] did.
>
> This is a GEO gap — Generative Engine Optimization. As AI replaces search for buyer research, companies not optimized for AI citation lose visibility fast.
>
> I'm a student at SKKU building expertise in this area. I'd like to run a free AI visibility audit for [Company Name] — 30 minutes, no commitment. Would that be useful?

### Target client profile
- Korean SMEs with English-language ambitions (need AI visibility in English, not just Korean)
- Korean startups raising money (investors use AI to research companies)
- Korean branches of foreign companies (their HQ uses AI tools to research local market)
- Professional services: lawyers, accountants, consultants (high search intent categories)

---

## Your unfair advantage

Most GEO agencies are run by marketing people who don't understand how LLMs actually retrieve content. You do — you've built RAG pipelines from scratch.

When you explain to a client:
> "The reason AI doesn't cite you is that your website uses vague language AI can't anchor to. I know this because I build the retrieval systems — here's exactly what the model is looking for."

That's a pitch no marketing agency can match.

---

## Tools to use

| Task | Tool |
|------|------|
| Research competitor AI visibility | Perplexity API via `research` skill |
| Write/rewrite client content | `writing-agent` + `geo` skill |
| Track citations over time | Manual audit (monthly) |
| Build client reports | `writing-agent` |
| Store client info | `notion-agent` → Notion database |

---

## First milestone

Run a free GEO audit for one SDC club connection. Document before/after. That case study = your portfolio for this business.

Use `/geo:project-description` to write the case study once it's done.
