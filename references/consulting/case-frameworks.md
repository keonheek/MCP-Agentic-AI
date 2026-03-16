# Consulting Case Frameworks

Reference for interview prep at McKinsey QuantumBlack, BCG Gamma, Deloitte Korea AI, Accenture Song.

_Use this with `/interview-prep` + "full case" mode._

---

## Core Principle: Lead with Structure

Never dive into analysis before stating your framework. Interviewers score:
1. Did you structure the problem before calculating?
2. Is your framework MECE (mutually exclusive, collectively exhaustive)?
3. Did you lead with a hypothesis, not a fishing expedition?

---

## Framework 1: Profitability Decline

**When to use:** Client's profit is falling. Diagnose why.

```
Profit = Revenue - Costs

Revenue
├── Price (per unit)
│   ├── Pricing strategy change?
│   ├── Competitive pressure?
│   └── Mix shift (lower-margin products)?
└── Volume (units sold)
    ├── Market shrinking or company losing share?
    ├── Distribution issues?
    └── Product/quality issue?

Costs
├── Fixed costs (overhead, rent, salaries)
│   └── Did fixed costs increase? Scale not achieved?
└── Variable costs (COGS, materials, logistics)
    ├── Input cost inflation?
    └── Process inefficiency?
```

**Hypothesis-first approach:**
> "My initial hypothesis is that this is a revenue issue, not a cost issue — specifically a volume decline rather than a price issue. I'd like to check: has the market grown while the client stagnated, or has the whole market contracted?"

---

## Framework 2: Market Entry

**When to use:** Should client enter a new market / launch a new product?

```
1. Market attractiveness
   ├── Market size (TAM) — how big?
   ├── Growth rate — expanding or mature?
   ├── Profitability — what margin do players earn?
   └── Structure — concentrated or fragmented?

2. Competitive landscape
   ├── Who are the key players? Their strengths?
   ├── What are the barriers to entry?
   └── Is there a clear #1? Is there room for disruption?

3. Client fit
   ├── Does client have the capabilities to compete?
   ├── Existing assets that transfer (brand, distribution, tech)?
   └── What would need to be built from scratch?

4. Entry mode
   ├── Build (organic) vs. Buy (M&A) vs. Partner (JV/licensing)
   ├── Speed-to-market requirements?
   └── Capital requirements?

5. Expected return
   ├── Revenue potential (market share * TAM)
   ├── Investment required
   └── Payback period / IRR
```

---

## Framework 3: AI Implementation for a Client

**When to use:** BCG Gamma / McKinsey QuantumBlack AI-specific case

```
1. Problem definition
   ├── What specific business problem are we solving?
   ├── Is AI the right tool (vs. process improvement, hiring, etc.)?
   └── What would success look like? (KPIs, timeline)

2. Data availability
   ├── Does the client have the data needed?
   ├── Data quality? Labeling requirements?
   └── Data governance / compliance (esp. Korean AI Framework Act)

3. Build vs. buy
   ├── Custom model vs. fine-tuned foundational model vs. API
   ├── Time-to-value vs. control
   └── Ongoing maintenance cost

4. Deployment risk
   ├── Integration with existing systems
   ├── Change management (user adoption)
   └── Model drift / monitoring requirements

5. ROI calculation
   ├── Cost savings (FTEs automated, error rate reduction)
   ├── Revenue uplift (faster decisions, new capabilities)
   └── Implementation cost (data prep + build + deployment + maintenance)

6. Risk mitigation
   ├── Regulatory compliance (Korean AI Framework Act, Jan 2026)
   ├── Privacy / data security
   └── Fallback if model fails
```

**Keonhee's edge:** He has built AI systems and can speak concretely to each step (FinAgent = deployed AI, SDC grader = real automation, DART MCP = data integration). Most candidates give generic answers here.

---

## Framework 4: Market Sizing

**When to use:** "How big is the market for X in Korea?"

**Method:**
```
Choose: Top-down (total market → slice) OR Bottom-up (unit × price × frequency)

Example: Korean AI compliance software market
Top-down:
- Korean companies subject to AI Framework Act: ~500 high-risk AI deployments (estimate)
- % that will buy compliance software: 30% in year 1
- Average contract value: KRW 50M/year
- Market: 500 × 0.30 × 50M = KRW 7.5B = ~$5.7M
→ Small but fast-growing; 3x by 2027 as more deployments hit high-risk threshold

Always sanity check with second method or comparable market.
```

**Quick Korean benchmarks:**
- Population: 51M
- GDP: ~$1.7T (2024)
- Smartphone penetration: ~95%
- Working population (15-64): ~36M
- Number of Korean public companies (KOSPI+KOSDAQ): ~2,500
- Large enterprises (>1,000 employees): ~3,000
- Korean AI R&D budget 2026: KRW 9.9 trillion (~$7.5B)

---

## Behavioral Question Bank (STAR format)

### "Tell me about a time you led a project with ambiguity."
> **S:** SDC Consulting Club needed an AI-powered application review system. No prior system. No spec. No budget.
> **T:** Design and build end-to-end in 2 weeks.
> **A:** Chose Claude Haiku API (cost-effective for volume). Wrote structured evaluation rubric. Built PDF extraction. Integrated with Google Sheets. No one on the team had done this before.
> **R:** Live system. Runs every 15 minutes. Eliminated manual first-round screening.

### "Tell me about a time you made a technical decision under constraints."
> **S:** Building FinAgent's retrieval layer. Initially planned to use ChromaDB (industry standard).
> **T:** Make the retrieval layer work with Python 3.14.
> **A:** Discovered ChromaDB incompatible with Python 3.14 (Pydantic v1 runtime issue). Evaluated options. Built custom cosine similarity VectorDB from NumPy — 50 lines, zero dependencies, fully transparent.
> **R:** Shipped. Works in production. And now I can explain every line of my retrieval system in an interview — which I couldn't have done with ChromaDB as a black box.

### "Tell me about a time you used data to inform a decision."
> **S:** FinAgent initially had a linear pipeline: all queries went through SQL → RAG → Report, regardless of type.
> **T:** Improve response time and cost without sacrificing quality.
> **A:** Analyzed query types. 40% were pure factual/numeric (SQL only, no docs needed). Added a router agent that classifies queries first. Built conditional LangGraph edges.
> **R:** SQL-only queries now skip the RAG step. Faster responses, lower API cost per query. Demonstrated that small architectural changes have disproportionate impact.

### "Why consulting?" (key question for someone with a technical background)
> "I build AI systems specifically to solve business problems. Consulting lets me work on that problem across industries and at scale. FinAgent started as a tool for one use case. Consulting means I'm designing AI solutions for dozens of different clients, business models, and datasets — that's where the generalization happens. I want to work at the intersection of 'what does the AI make possible' and 'what does the business actually need.' Consulting AI practices are where that happens best."

### "Why [specific firm]?"
- **McKinsey QuantumBlack:** "QuantumBlack started as a Formula 1 data science consultancy — analytics as competitive advantage, not just a tool. That's the mindset I want to work in. They also have one of the best Python/ML engineering cultures in consulting."
- **BCG Gamma:** "BCG's potential model — bet on problem-solving over credentials — is the right call for AI roles. The technical depth + strategy combination is where I'm strongest, and BCG Gamma deploys exactly that for clients."
- **Deloitte Korea AI:** "Deloitte Korea's clients are the companies whose data I've been working with — Samsung, Hyundai, Korean banks. I have context most other candidates don't: I understand DART, I understand Korean corporate structure, I understand the AI Framework Act implications."

---

## Quick Scoring Checklist (after each practice case)

- [ ] Stated framework before calculating?
- [ ] Led with a hypothesis?
- [ ] Numbers were reasonable / sanity-checked?
- [ ] Communicated clearly at each transition?
- [ ] Ended with a concrete recommendation?
- [ ] Connected data to business implication?

**Pass threshold for McKinsey/BCG:** All 6 consistently. Below that: practice more cases.

---

## Case Practice Schedule

Before applying to BCG Gamma or McKinsey QuantumBlack, complete:
- [ ] 10 profitability cases (use `/interview-prep` "full case" mode)
- [ ] 5 market sizing cases
- [ ] 3 AI implementation cases (Keonhee's strongest)
- [ ] 2 market entry cases

Track progress: add a checkbox to `tasks/todo.md` as cases complete.
