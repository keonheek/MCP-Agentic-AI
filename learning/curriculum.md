# Learning Curriculum — Keonhee Kim

_Auto-updated by daily learning cron. Last updated: 2026-03-22_

## Active Tracks (parallel — one lesson per track per week)

| Track | Current Level | Target | Weekly Goal |
|-------|--------------|--------|-------------|
| AI Engineering | Intermediate (LangGraph, RAG, MCP built) | Advanced (LLMOps, evals, fine-tuning) | 1 concept + 1 implementation |
| SQL | Beginner | Advanced (window functions, optimization) | 1 topic + 10 practice queries |
| Data Engineering | Beginner (pandas, numpy) | Intermediate (dbt, pipelines) | 1 concept + 1 notebook |
| ML / Deep Learning | Beginner (linear regression built) | Intermediate (PyTorch, CNNs, time series) | 1 concept + 1 model |
| Finance (Quant) | Intermediate (DART, yfinance, DCF built) | Advanced (factor models, options basics) | 1 concept + 1 Python notebook |

---

## Track 1: AI Engineering

**Primary resource:** [Mastering Agentic Design Patterns with LangGraph](https://github.com/MahendraMedapati27/Mastering-Agentic-Design-Patterns-with-LangGraph) — 7 patterns, working code, Mar 2026
**Video:** [Tech With Tim — LangGraph Advanced](https://www.youtube.com/watch?v=1w5cCXlh7JQ) (46 min)
**Observability:** [LangSmith](https://smith.langchain.com/) (free tier) | [Phoenix](https://github.com/Arize-ai/phoenix) (open-source)
**Evals:** [RAGAS GitHub docs](https://github.com/explodinggradients/ragas) — no course, just docs
**VectorDB:** [PGVector](https://github.com/pgvector/pgvector) | [Chroma](https://github.com/chroma-core/chroma)
**Fine-tuning:** [Hugging Face PEFT](https://github.com/huggingface/peft) | [HF Transformers docs](https://huggingface.co/docs/transformers/)

### Completed
- [x] LangGraph 4-node pipeline (SME Diagnostic AI)
- [x] RAG with custom cosine similarity VectorDB
- [x] MCP server (DART) — custom Python implementation
- [x] Multi-agent orchestration (director + coding + research agents)
- [x] Autoresearch loop (generate → score → improve)

### In Progress
- [ ] LLM evaluation: RAGAS benchmark on FinAgent RAG pipeline
- [ ] Structured outputs with Pydantic + Claude API

### Queue
- [ ] LLMOps: observability with LangSmith (add to SME Diagnostic AI)
- [ ] Prompt caching (Anthropic API) — reduce costs on repeated context
- [ ] Fine-tuning: LoRA on Hugging Face (conceptual + hands-on)
- [ ] Streaming responses in FastAPI + Streamlit
- [ ] Agent memory patterns: episodic vs semantic vs procedural
- [ ] Tool use reliability: retry patterns, validation loops
- [ ] Multi-modal: Claude vision API (image → structured data)

---

## Track 2: SQL

**Primary resource:** [SQLBolt](https://sqlbolt.com/) — interactive, browser-based, 15 lessons, zero setup
**Advanced:** [AlmaBetter](https://almabetter.com/) — window functions, CTEs, PostgreSQL (free tier)
**Practice:** [LeetCode SQL 50](https://leetcode.com/) | [SQL Murder Mystery](https://github.com/NUKnightLab/sql-mysteries)
**Video:** [FreeCodeCamp SQL Tutorial](https://www.youtube.com/watch?v=HXV3zeQKqGY) (4+ hours)
**Reference:** [awesome-sql](https://github.com/danchristensen/awesome-sql)

### Completed
- [x] Basic SELECT, WHERE, ORDER BY (used in FinAgent Text2SQL)
- [x] JOINs (inner, left) — used in consulting emulation

### In Progress
- [ ] Week 1: Aggregations (GROUP BY, HAVING, COUNT, SUM, AVG)

### Queue (in order)
- [ ] Week 2: Subqueries and CTEs (WITH clauses)
- [ ] Week 3: Window functions (ROW_NUMBER, RANK, LAG, LEAD, PARTITION BY)
- [ ] Week 4: Query optimization (indexes, EXPLAIN, query plans)
- [ ] Week 5: PostgreSQL specifics (JSONB, full-text search, pg_trgm)
- [ ] Week 6: SQL for analytics (cohort analysis, funnel queries, retention)
- [ ] Week 7: Practice — LeetCode SQL 50 (medium difficulty)
- [ ] Week 8: Practice — StrataScratch (business SQL problems)

### Practice setup
- Local: SQLite (already used in FinAgent — zero setup)
- Online: [Mode SQL Tutorial](https://mode.com/sql-tutorial/), [SQLZoo](https://sqlzoo.net)

---

## Track 3: Data Engineering

**Primary resource:** [Data Engineering Zoomcamp](https://github.com/DataTalks-Club/data-engineering-zoomcamp) — 9 weeks, free, covers Docker/dbt/Spark/Kafka/BigQuery
**Video:** [DataTalks.Club YouTube](https://www.youtube.com/@DataTalks-Club)
**Spark:** [Dataquest PySpark](https://www.dataquest.io/) (free tier)
**Reference:** [awesome-data-engineering](https://github.com/igorbarinov/awesome-data-engineering)
**Community:** DataTalks.Club Slack (#course-data-engineering)

### Completed
- [x] pandas basics (filtering, groupby, merge)
- [x] numpy arrays and cosine similarity
- [x] SQLite pipelines (FinAgent)
- [x] Week 1: pandas advanced — method chaining, .pipe(), .assign(), .query()

### In Progress
- [ ] Week 2: Data cleaning patterns (missing values, outliers, type coercion)

### Queue (in order)
- [ ] Week 3: dbt fundamentals (models, tests, documentation)
- [ ] Week 4: Building a simple ETL pipeline (DART → SQLite → pandas → report)
- [ ] Week 5: Polars (faster pandas alternative — worth knowing)
- [ ] Week 6: Apache Spark basics (PySpark) — conceptual + small example
- [ ] Week 7: Data quality checks (Great Expectations or pandera)
- [ ] Week 8: Streaming basics (Kafka concepts, not hands-on yet)

---

## Track 4: ML / Deep Learning

**Primary resource:** [ML Zoomcamp](https://github.com/DataTalks-Club/machine-learning-zoomcamp) — code-first, self-paced, free
**Math foundation:** [MIT OpenCourseWare](https://ocw.mit.edu/) — 7 free ML courses
**PyTorch:** [Official tutorials](https://pytorch.org/tutorials/) — CNNs, RNNs, time series
**TensorFlow/Keras:** [keras.io](https://keras.io/) — quick prototyping
**Video:** [Fast.ai / Jeremy Howard](https://www.youtube.com/@FastAIDotOrg) — top-down, code-first
**Fine-tuning:** [DeepLearning.AI: Generative AI with LLMs](https://www.deeplearning.ai/short-courses/generative-ai-with-llms/)
**Repos:** [pytorch/examples](https://github.com/pytorch/examples) | [fastai](https://github.com/fastai/fastai)

### Completed
- [x] Linear Regression (Samsung stock — sklearn)
- [x] Prophet time series forecasting (Samsung)
- [x] Embeddings (OpenAI text-embedding-ada-002 — used in RAG)

### In Progress
- [ ] Week 1: ML fundamentals refresher — bias/variance, train/val/test split, cross-validation

### Queue (in order)
- [ ] Week 2: Classification (logistic regression, decision trees, random forest)
- [ ] Week 3: Model evaluation (precision, recall, F1, ROC-AUC)
- [ ] Week 4: PyTorch fundamentals (tensors, autograd, nn.Module)
- [ ] Week 5: Simple neural network from scratch in PyTorch
- [ ] Week 6: CNNs — image classification (MNIST → CIFAR-10)
- [ ] Week 7: Time series with PyTorch (LSTM for stock prediction — upgrade Samsung project)
- [ ] Week 8: Hugging Face Transformers — fine-tuning a small BERT model
- [ ] Week 9: TensorFlow/Keras — same as PyTorch but different API (1 week overview)
- [ ] Week 10: Reinforcement Learning basics (Q-learning concept)

---

## Track 5: Finance (Quantitative)

**Primary resource:** [PyQuant News](https://pyquantnews.com/) — 13 modules, 134 lessons, 40+ code templates, free core
**Backtesting:** [QuantConnect](https://www.quantconnect.com/learning) — algorithmic trading + LEAN engine
**Korean market:** [OpenDartReader](https://github.com/FinanceData/OpenDartReader) (DART API wrapper) | yfinance tickers: `^KS11`, `005930.KS` (Samsung), `000660.KS` (SK Hynix)
**Video:** [Algovibes YouTube](https://www.youtube.com/@Algovibes) — algo trading + Python
**Reference:** [awesome-quant](https://github.com/wilsonfreitas/awesome-quant)
**Free data:** yfinance | [Alpha Vantage](https://www.alphavantage.co/) | [FRED](https://fred.stlouisfed.org/)

### Completed
- [x] DART API (financial statements, disclosures)
- [x] DCF valuation (consulting emulation project)
- [x] yfinance data fetching (Samsung project)
- [x] Basic financial ratios (P/E, ROE, operating margin)

### In Progress
- [ ] Week 1: Time value of money + NPV/IRR in Python

### Queue (in order)
- [ ] Week 2: Portfolio theory (Markowitz, efficient frontier) — implement in Python
- [ ] Week 3: Factor models (Fama-French 3-factor) — fetch data + run regression
- [ ] Week 4: Options basics (calls/puts, Black-Scholes) — conceptual + Python
- [ ] Week 5: Korean market specifics — KOSPI index, sector ETFs, KOSDAQ dynamics
- [ ] Week 6: Alternative data for finance (news sentiment + stock returns)
- [ ] Week 7: Backtesting a simple momentum strategy (with backtrader or zipline)
- [ ] Week 8: Financial statement analysis — systematize what's in FinAgent

---

## Learning Rules
1. Never spend more than 45 min on one topic per day
2. Always build something — every concept needs a notebook or a code snippet
3. Save outputs to `learning/outputs/YYYY-MM-DD-[track]-[topic].md` or `.ipynb`
4. Link to the resource used — don't repeat same resource twice
5. If a topic is confusing, add it to the "needs revisit" list below
6. Cross-apply learnings: SQL week 3 → improve FinAgent queries; ML week 7 → upgrade Samsung project

## Needs Revisit
_Add here when something didn't click_
- (empty)
