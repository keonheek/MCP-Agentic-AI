# Decision Log

Append-only. When a meaningful decision is made, log it here.

Format: [YYYY-MM-DD] DECISION: ... | REASONING: ... | CONTEXT: ...

---

[2026-03-06] DECISION: Replace ChromaDB with custom VectorDB (OpenAI embeddings + numpy cosine similarity + JSON persistence) | REASONING: ChromaDB is incompatible with Python 3.14 due to Pydantic v1 runtime type inference issue. Custom VectorDB is simpler, fully controlled, and more educational for interview explanations. | CONTEXT: FinAgent build session, 6-hour window before Kearney interview.

[2026-03-06] DECISION: Use LangGraph (StateGraph, 3-node linear pipeline) over raw function chaining for FinAgent | REASONING: LangGraph gives structured state management (AgentState TypedDict), clean node/edge separation, and is industry-standard for multi-agent orchestration. Interview-ready explanation: directed graph where each node is an agent. | CONTEXT: FinAgent architecture planning.

[2026-03-06] DECISION: Deploy FinAgent on Streamlit Cloud (free tier) rather than self-hosted | REASONING: Zero infrastructure overhead, shareable URL for portfolio/interviews, fast iteration. | CONTEXT: keonhee-finagent.streamlit.app — live.

[2026-03-07] DECISION: Set up executive assistant / second brain in Claude Code (VS Code) as primary workspace | REASONING: Centralizes AI tooling, context, and muscle memory in one place. CLAUDE.md + context files + skills = persistent, improving assistant without re-explaining every session. | CONTEXT: Start of second brain setup session.

[2026-03-07] DECISION: Use GitHub Flow (feature branches → master) over Git Flow for solo AI developer | REASONING: Git Flow (develop/release/hotfix) adds overhead with no benefit for solo work. GitHub Flow is simpler: branch from master, PR when ready. | CONTEXT: 5-branch GitHub structure setup (master, dev, skills, agents, projects).

[2026-03-09] DECISION: Keep director-agent and coding-agent on Sonnet; writing-agent, notion-agent, research-agent on Haiku | REASONING: Orchestration and code generation require reasoning → Sonnet. CRUD, drafting from templates, and web search are mechanical → Haiku saves cost. | CONTEXT: Agent team build session.

[2026-03-09] DECISION: Adapt Anthropic's open-source Cowork plugins (finance, data) as Claude Code skills rather than using the Cowork product directly | REASONING: Cowork is a claude.com enterprise product requiring a Team/Enterprise plan. Claude Code skills give the same domain knowledge and workflow patterns at zero additional cost, fully customized for Keonhee's specific stack (FinAgent, Korean market, DART). | CONTEXT: Cowork plugin integration session.

[2026-03-09] DECISION: Kearney declined — pivot to next AI role rather than re-applying | REASONING: Rejection reason was "current project tech stack fit, not capability." Passion and AI interest confirmed by recruiter. Build more projects, identify better-fit targets. | CONTEXT: Rejection received 2026-03-09.
[2026-03-10] CONTEXT UPDATED: current-priorities.md written.
[2026-03-11] CONTEXT UPDATED: current-priorities.md written.
[2026-03-11] CONTEXT UPDATED: me.md written.
[2026-03-11] CONTEXT UPDATED: work.md written.
[2026-03-11] CONTEXT UPDATED: readme.md written.

[2026-03-11] DECISION: Pivot primary job targets from AI-native companies to consulting AI practices (McKinsey QuantumBlack, BCG Gamma, Deloitte Korea AI, Accenture Song) | REASONING: Business Administration + agentic AI technical skills is rare at student level. That combination is valued by consulting AI practices, not ML labs. Upstage retained as Tier 2. | CONTEXT: AI job openings research showed Kakao/Naver cycles closed; Samsung SAIC is US-only.

[2026-03-11] DECISION: All 10 skills overhauled for consulting focus (interview-prep complete rewrite, GEO adds consulting keywords, financial-analyst adds case mode, data-analyst adds window functions) | REASONING: Skills were generic; need to serve the consulting application cycle specifically. | CONTEXT: Skill evaluation and improvement session.

[2026-03-11] DECISION: Supabase connection failure is due to paused project (free tier) not wrong credentials | REASONING: Direct host db.bnsimxodkdnfxspwntro.supabase.co doesn't resolve (project offline), pooler returns "Tenant or user not found" (expected when paused). Fix: restore in Supabase dashboard. | CONTEXT: FinAgent Postgres checkpointing debugging session.

[2026-03-11] DECISION: GEO-optimize GitHub profile + FinAgent + DART MCP READMEs with consulting framing | REASONING: Previous READMEs described the tech but not the business impact. Consulting recruiters and AI search engines both need the business framing to be explicit. | CONTEXT: Portfolio visibility push session.

[2026-03-11] DECISION: PitchFi Agent (agentic financial analysis for Korean startup pitch decks) recommended as next product to build | REASONING: Fastest path to MVP (reuses FinAgent + DART MCP). DART MCP is a moat. SDC club = built-in first users. Aligns with consulting portfolio narrative. | CONTEXT: Cluely-style product opportunity research.

[2026-03-11] DECISION: Build SQL window function exercises + AWS quickstart guides as consulting gap-closure references | REASONING: McKinsey QuantumBlack requires SQL + cloud; resources needed to close the 28-30% fit gap before applying. Mode Analytics SQL tutorial + AWS Lambda deployment closes both gaps in ~2 days. | CONTEXT: Consulting interview prep session.

[2026-03-11] DECISION: Create company-specific interview prep files (Deloitte, BCG, McKinsey QB) rather than one generic consulting prep | REASONING: Each firm has a different interview format, technical depth, and language requirement. Deloitte = Korean behavioral; BCG = case-heavy; McKinsey QB = candidate-led + technical Python/SQL screen. Generic prep would underserve all three. | CONTEXT: Consulting application preparation session.

[2026-03-12] DECISION: Validate GEO agency targeting Korean SMEs before building — research showed addressable gap is real | REASONING: Korean SME AI consulting market research confirmed: only 31% of SMEs have adopted AI, 21.9% specifically want consulting guidance, and no player is offering affordable GEO or agentic workflow consulting at SME price points. Government subsidies (AX Sprint Track, 140B KRW) can offset 30-70% of fees. | CONTEXT: Korean SME AI consulting market research (research/2026-03-11-korean-sme-ai-consulting-market.md).

[2026-03-12] DECISION: GEO agency entry strategy — free audit for one SDC connection → prove citation in ChatGPT/Perplexity → 500K-1M KRW paid audit → monthly retainer upsell | REASONING: Market education is the main friction (SMEs don't know what GEO is). Free audit removes payment risk and produces a demo. Showing "when someone asks ChatGPT for your product, now they find you" is the clearest possible ROI proof. | CONTEXT: Follows from Korean SME market research.

[2026-03-12] DECISION: SDC Consulting Club Grader confirmed production-ready — live email test passed | REASONING: Pipeline triggered end-to-end with real email: Gmail → PDF extraction → Claude Haiku grading → Google Sheets logging. Korean output confirmed. No further dev work needed. | CONTEXT: Full live test completed 2026-03-12.

[2026-03-12] DECISION: Consulting emulation project scoped as "Automated M&A Due Diligence & Strategy War Room" — 4 phases, ~80h total | REASONING: Gemini-authored Notion concept provided direction; needed concrete build order, time estimates, and resume impact quantification before starting. Fast track (27h/7 days) targets BCG deadline. | CONTEXT: Project plan at `projects/consulting-emulation/README.md`; Notion page updated.

[2026-03-12] DECISION: 100% fit at consulting firms (MBB/Big4) is structurally impossible without prior work experience — honest ceiling set per firm | REASONING: Client engagement experience and case interview performance under pressure cannot be replicated by building projects. Upstage (startup) has the highest achievable ceiling (92%) because they value builders. MBB ceiling: 88-90%. | CONTEXT: Fit ceiling analysis session; firm-specific close actions documented in `projects/consulting-emulation/README.md`.

[2026-03-12] DECISION: Build all consulting-emulation fast-track steps in one session using 5 parallel background agents | REASONING: BCG deadline is open now; parallel agent execution compresses 27h of build time into one session. Each agent works on a non-overlapping module (valuation, RAGAS, hybrid search, pptx, AWS, DART, supervisor, XGBoost). | CONTEXT: Session 3 — consulting-emulation build sprint.

[2026-03-12] DECISION: Supervisor Agent adds a 4th route "valuation" beyond FinAgent's sql_only/rag_only/both | REASONING: DCF and comparable company analysis questions are a distinct class — they need the Valuation Agent, not SQL or RAG. Existing router cannot handle them correctly without a new route. | CONTEXT: agents/supervisor.py build session.

[2026-03-12] DECISION: XGBoost distress model trained on synthetic data, scored on real DB companies | REASONING: FinAgent DB only has 3 companies — insufficient for real training. Synthetic generation with known distress/non-distress labels is standard practice for portfolio/educational demos. Real companies scored for credibility. | CONTEXT: models/distress_model.py build session.
[2026-03-13] CONTEXT UPDATED: current-priorities.md written.

[2026-03-13] DECISION: Rename consulting emulation app to "M&A Due Diligence Suite" | REASONING: "Strategy War Room" was too aggressive/informal for a consulting portfolio; "Suite" signals professional toolset, not a game | CONTEXT: Streamlit app.py UI overhaul session.

[2026-03-13] DECISION: Inter font (Calibri fallback) via Google Fonts for Streamlit app | REASONING: Research confirmed Calibri is the McKinsey/BCG document standard; Inter is the closest open-weight web equivalent and loads reliably on Streamlit Cloud | CONTEXT: Consulting font research, 2026-03-13-consulting-charts-fonts.md.

[2026-03-13] DECISION: Bundle FinAgent code into finagent/ subdirectory for cloud portability | REASONING: Streamlit Cloud cannot access local Windows paths; bundling agent files + SQLite DB into the consulting-emulation repo is simpler than a git submodule and makes the app fully self-contained | CONTEXT: Cloud deploy prep — keonhee-duediligence.streamlit.app target.

[2026-03-13] DECISION: RAGAS benchmark — do not run without explicit user permission | REASONING: Runs 15 OpenAI API calls + a second evaluation round; meaningful cost for a non-urgent benchmark. User flagged cost as a concern. | CONTEXT: Session cost management discussion.

[2026-03-13] DECISION: DART pipeline confirmed live with real data (2026-03-13) | REASONING: Live test returned Samsung FY2023/2024/2025 financials + 5 live disclosures from DART API. Pipeline is production-ready. | CONTEXT: data/dart_pipeline.py test run — search_company + get_financials + get_recent_disclosures all confirmed.

[2026-03-13] DECISION: Use `aws cloudformation package/deploy` instead of SAM CLI for Lambda deployment | REASONING: SAM CLI uses samtranslator which depends on pydantic v1 — incompatible with Python 3.14 (crashes with RuntimeError on model field validation). AWS CLI's cloudformation commands have no such dependency and work fine. | CONTEXT: Lambda deploy session — sam build crashed, cloudformation deploy succeeded.

[2026-03-13] DECISION: Use `pip install --platform manylinux2014_x86_64 --python-version 311 --only-binary=:all:` to package Lambda-compatible wheels without Docker | REASONING: Lambda runs Linux Python 3.11; local system has Windows Python 3.14. Docker not installed. pip 22.3+ supports --platform flag to download wheels for a different platform/version without installing them locally. | CONTEXT: Lambda packaging session — numpy/pandas Linux wheels needed.

[2026-03-13] DECISION: FinAgent Lambda API is live — finagent-prod stack, ap-northeast-2, /health confirmed | REASONING: First production cloud backend for FinAgent. Adds AWS Lambda to portfolio — closes the AWS gap for Deloitte/consulting applications. Stack managed via CloudFormation. | CONTEXT: API URL: https://v7zapdvb10.execute-api.ap-northeast-2.amazonaws.com/

[2026-03-14] DECISION: SDC Grader Q1 rubric — removed requirement to name specific SDC projects | REASONING: SDC's first recruitment cycle; applicants have no prior SDC context to reference. Score on consulting understanding and genuine personal fit instead. | CONTEXT: SDC Grader v2 overhaul session.

[2026-03-14] DECISION: SDC Grader Activities — two-component scoring (breadth 0-12 + skill self-ratings 0-8) replacing single scale | REASONING: Original rubric gave nearly identical scores to 2 vs 20 activities. Two components differentiate activity breadth from technical capability independently. | CONTEXT: User flagged undifferentiated activity scores; PDF has explicit 1-5 skill rating table.

[2026-03-14] DECISION: Sort Applications sheet by Total Score descending after each processNewApplications() run | REASONING: Manual sorting after grading was an extra step; auto-sort on finish means highest-scoring applicants are always at the top without any user action. | CONTEXT: SDC Grader v2 — sortByScore() added and auto-called.

[2026-03-14] DECISION: Add Stop hook (beep 600Hz 150ms) to signal task completion | REASONING: User wants a quiet audio cue when Claude finishes long tasks, without needing to watch the screen. | CONTEXT: .claude/settings.json Stop event hook.

[2026-03-14] DECISION: Second Brain restructured — Goals (5 levels) + Projects (6 bilingual pages) replaces empty PARA template | REASONING: Original Second Brain had mostly empty template databases with no real content. Restructured around actual active projects and a goal hierarchy Keonhee will use daily. | CONTEXT: Notion Second Brain audit + rebuild session.

[2026-03-14] DECISION: Todo updates always trigger Notion sync | REASONING: User wants tasks/todo.md and Notion Active To-Do List to stay in sync without asking twice. | CONTEXT: User preference stated explicitly.
