# Skill: Interview Prep — Consulting + AI Roles

Structure prep for consulting and AI interviews — company research, talking points, case frameworks, behavioral Q&A, and story framing.

Updated 2026-03-11: Focus shifted to AI consulting targets (McKinsey QuantumBlack, BCG Gamma, Deloitte Korea AI, Accenture Song).

## Trigger phrases
- "prep me for my interview at X"
- "what should I know about X company"
- "mock interview for X role"
- "help me answer [interview question]"
- "build my talking points for X"
- "walk me through a consulting case"
- "give me a case interview"

---

## Target Companies (as of 2026-03-11)

### Tier 1 — Apply First
| Company | Practice | Keonhee's angle |
|---------|----------|-----------------|
| **McKinsey QuantumBlack** | AI-first analytics arm of McKinsey | Python/ML analytics + business narrative |
| **BCG Gamma** | BCG's data science + AI unit | LangGraph/RAG + strategy framing |
| **Deloitte Korea AI & Analytics** | Big 4, real AI implementation (not strategy) | Technical build + Korean market |
| **Accenture Song / AI** | Technology consulting, Global AI program Jun–Aug 2026 | Full-stack AI + client delivery |

### Tier 2 — Apply in Parallel
| Company | Notes |
|---------|-------|
| **Samsung SDS AI** | Enterprise AI solutions, SKKU connection |
| **LG CNS AI** | Korean IT services, data/AI team |
| **Strategy& (PwC) Korea** | More strategy, less technical — if others slow |

---

## How to use this skill

Give Claude the company, role, and any context. Examples:
- "Prep me for my McKinsey QuantumBlack first round — behavioral + case"
- "Mock interview — ask me case questions for BCG Gamma"
- "Help me answer: why consulting when you build AI?"
- "Walk me through a market sizing case"
- "Give me 10 likely interview questions for Deloitte Korea AI"

---

## What Claude does

1. **Load company context** — Research the specific firm, practice area, recent AI projects
2. **Build talking points** — Why you, why them, your relevant projects in their language
3. **Q&A prep** — Generate likely questions and coach answers
4. **Story framing** — Frame FinAgent, DART MCP, SDC grader in terms the interviewer cares about
5. **Case practice** — If requested, run a full case with feedback
6. **Mock Q&A** — Asks questions, you answer, Claude gives direct feedback

---

## Keonhee's Key Narratives for Consulting AI Roles

### "Why consulting when you build AI?"
_This is the #1 question you'll get. Answer:_
> I build AI systems specifically to solve business problems — that's what consulting does at scale. FinAgent isn't a research project; it's a tool for financial decision-making. DART MCP isn't a toy; it exposes real Korean corporate data that matters to investors, analysts, and strategists. Consulting lets me work on that problem set across industries and at scale — instead of building one tool for one company.

### "Why AI consulting specifically?"
> Because most AI projects fail at the deployment step — not the model step. Consulting firms with AI practices are where that gap gets solved. I've experienced this firsthand: building FinAgent and seeing it work end-to-end changed how I think about what AI actually requires to ship.

### FinAgent → consulting frame
- Don't say "I built a multi-agent LLM system." Say: "I built a system that automated financial analysis workflows — routing queries to the right analysis method (SQL vs. RAG) without human decision-making at each step."
- Tie it to business outcome: "The value was accuracy + speed. What used to take an analyst 30 minutes took 5 seconds."

### DART MCP → consulting frame
- "I built a data integration layer that makes Korean corporate financial data accessible to any AI agent — the equivalent of building a proprietary data pipeline for a consulting project."

### SDC Grader → consulting frame
- "I automated the application review process for our consulting club — Claude API graded applications against structured rubrics and logged results to Google Sheets. It's a small-scale version of what consulting firms are doing with AI for talent screening and document processing."

---

## Case Interview Framework

### Structure for any case
1. **Clarify** — Ask 2-3 questions to confirm scope (market, time horizon, objective)
2. **Framework** — State your approach (MECE issue tree or hypothesis-driven)
3. **Analyze** — Work through each branch, use numbers
4. **Synthesize** — Lead with the answer, support with evidence
5. **Recommend** — Concrete, defensible recommendation

### Common frameworks for AI/tech cases
- **Market entry**: Market size → Competition → Fit with client capabilities → Entry mode
- **AI implementation**: Problem definition → Data availability → Build vs. buy → Deployment risk → ROI
- **Profitability decline**: Revenue (price × volume) vs. Cost (fixed vs. variable) → Root cause → Solutions

### Market sizing (quick mental models)
- Korean population: 51M
- Korean GDP: ~$1.7T USD
- Korean smartphone penetration: ~95%
- Korean internet penetration: ~98%

### Useful AI-specific case data points
- Korean AI R&D budget 2026: KRW 9.9 trillion (~$7.5B USD)
- Global AI capex 2026: ~$527B
- Korean AI Framework Act: Jan 2026 enforcement started

---

## Behavioral Framework (STAR)

For all behavioral questions:
- **S**ituation — 1-2 sentences of context
- **T**ask — what was your responsibility specifically
- **A**ction — what YOU did (not the team) — be specific
- **R**esult — quantify if possible; what changed

### Pre-loaded STAR stories

**Leadership under ambiguity:**
> S: SDC consulting club needed an automated application review system — no clear spec. T: Design and build it end-to-end. A: Chose Claude API for grading, built PDF extraction, designed rubric, integrated with Google Sheets. No prior reference. R: System now runs automatically every 15 min; removed manual review burden.

**Technical problem-solving:**
> S: FinAgent's checkpointing relied on Supabase Postgres — connection kept failing ("Tenant or user not found"). T: Fix or find a fallback so the app doesn't break. A: Diagnosed pooler vs. direct connection issue; implemented fallback logic (Postgres → MemorySaver) so the app runs regardless. R: App stable, investigation ongoing.

**Business + technical bridge:**
> S: Evaluating which VectorDB to use for FinAgent's RAG pipeline. T: Make the right build-vs-buy decision. A: Tested ChromaDB (incompatible with Python 3.14), then built custom cosine similarity from scratch with NumPy. R: Shipped it, working in production, and now I can explain every line of the retrieval logic in an interview.

---

## Company-Specific Prep

### McKinsey QuantumBlack
- What they do: Advanced analytics, ML engineering, data strategy — not generalist consulting
- Key projects: Iguazu (internal GenAI platform), client AI implementations
- What they value: Python proficiency, ML fundamentals, structured problem-solving, business impact of AI
- Likely Q: "Walk me through a technical project where you made a key design decision"
- Flag: QuantumBlack interviews include a data/coding assessment (Python, SQL) — practice these

### BCG Gamma
- What they do: Data science, AI/ML implementation, GenAI strategy
- Key projects: GenAI deployment for Fortune 500; BCGX (tech arm) builds AI products
- What they value: ML skills + strategy thinking; can you go from data to recommendation?
- Likely Q: "How would you approach building an AI solution for a client who has no AI infrastructure?"
- Flag: BCG uses "potential model" hiring — fit + problem-solving over credentials

### Deloitte Korea AI & Analytics
- What they do: AI implementation consulting — RPA, GenAI, data engineering for Korean enterprises
- Key clients: Samsung, Hyundai, Korean banks, government
- What they value: Python, cloud tools, Korean business context, client communication
- Likely Q: "Describe a technical project where you had to explain a complex AI concept to a non-technical audience"
- Flag: Deloitte Korea interviews in Korean. Prepare Korean answers to all behavioral questions.

### Accenture Song / AI
- What they do: AI + creative tech, GenAI deployment, digital transformation
- Program: Global AI & Data Development Program (Jun–Aug 2026 cohort)
- What they value: Cloud experience (Azure/AWS), Python, ability to deliver client-facing work
- Likely Q: "How do you prioritize when building an AI solution for a client under time constraints?"
- Flag: Accenture emphasizes client skills and communication alongside technical depth

---

## Output format

- Bullet points throughout — no paragraphs unless drafting a written answer
- Talking points as a numbered list (prioritized)
- Mock Q&A clearly labeled: **Q:** / **A:** / **Feedback:**
- Case interview: labeled stages (Clarify → Structure → Analyze → Synthesize → Recommend)

## Notes

- Say "be harsh" for blunt feedback on answers
- Say "Korean interview mode" to switch to Korean-language prep
- Say "full case" to run a complete 20-min simulated case with scoring at the end
- For AI jargon, always translate to business terms: "LangGraph" = "orchestration layer", "RAG" = "AI that retrieves from your own documents", "MCP" = "plugin system for AI agents"
- External tone: professional, confident, no hedging

---

## Reference Files

Load the relevant file based on context:

| File | When to use |
|------|-------------|
| `references/consulting/case-frameworks.md` | Full case frameworks, STAR stories, scoring checklist, practice schedule |
| `references/consulting/deloitte-korea-interview-prep.md` | Deloitte Korea: Korean Q&A, technical questions, AI implementation case, application checklist |
| `references/consulting/bcg-gamma-interview-prep.md` | BCG Gamma: case format, candidate-led vs interviewer-led, quantitative prep, STAR answers |
| `references/consulting/mckinsey-qb-interview-prep.md` | McKinsey QB: technical gaps (PySpark, AWS), candidate-led case format, Python/ML questions |
| `references/consulting/accenture-interview-prep.md` | Accenture: behavioral in Korean, GenAI case style, Azure AI-900, April deadline |
| `references/consulting/sql-practice.md` | SQL window functions: LAG, RANK, PARTITION BY, consulting-context exercises |
| `references/consulting/aws-quickstart.md` | AWS Lambda deployment guide, key concepts, 1-week learning path |
