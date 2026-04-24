# Keonhee Kim — Learning Curriculum Bundle
## For Gemini Gem — AI Tutor Context

**How to use this file:**
Upload to a Gemini Gem as context. Then ask Gemini to:
- Quiz you on any topic
- Explain concepts in different ways
- Give you new exercises
- Check your code solutions
- Connect concepts across tracks

---

## Who You Are (Student Profile)

- **Name:** Keonhee Kim
- **Background:** SKKU Business Administration student, South Korea
- **Level:** Intermediate — built production AI systems, studying formal fundamentals
- **Goal:** AI Engineering career + consulting AI practices

**What you've already built (don't re-explain these):**
- LangGraph 4-node pipeline (SME Diagnostic AI)
- RAG with custom cosine similarity VectorDB (FinAgent)
- Custom MCP server (DART Korean financial data)
- Multi-agent orchestration (7 specialist agents)
- DCF valuation model (Consulting Emulation)
- DART API pipeline + financial ratio analysis
- Samsung stock prediction (Linear Regression + Prophet)
- Text2SQL in FinAgent

**Tools you use daily:** Claude Code, Python, pandas, LangGraph, Streamlit, SQLite, yfinance, DART API

---

## 5-Track Curriculum Overview

| Track | Current Level | Target |
|-------|--------------|--------|
| Track 1: AI Engineering | Intermediate | Advanced (LLMOps, evals, fine-tuning) |
| Track 2: SQL | Beginner-Intermediate | Advanced (window functions, optimization) |
| Track 3: Data Engineering | Beginner | Intermediate (dbt, pipelines) |
| Track 4: ML / Deep Learning | Beginner | Intermediate (PyTorch, CNNs, time series) |
| Track 5: Finance (Quant) | Intermediate | Advanced (factor models, options basics) |

**Rotation schedule:** Mon=AI Engineering, Tue=SQL, Wed=Data Engineering, Thu=ML, Fri=Finance

---

---

# TRACK 1: AI ENGINEERING

## Week 1 Lesson — LLM Evaluation with RAGAS
_Source: learning/outputs/2026-03-24-ai-engineering-llm-evals-ragas.md_

### Concept

RAGAS (Retrieval Augmented Generation Assessment) is a framework for evaluating RAG pipelines without human-labeled ground truth. It computes reference-free metrics using LLMs to judge output quality across four dimensions.

You built a RAG pipeline in FinAgent: `text-embedding-3-small` embeds chunks → cosine similarity retrieves top-k → GPT-4o answers. RAGAS tells you how good that pipeline actually is, beyond "it seems to work."

**The four core metrics:**

1. **Faithfulness** — Does the answer stick to what the retrieved context says? Score = (claims supported by context) / (total claims). Low score = hallucination.

2. **Answer Relevance** — Does the answer actually address the question? Generates synthetic questions from the answer, measures similarity to original. Low score = answer doesn't address the question.

3. **Context Recall** — Did retrieval fetch everything needed? Requires a `ground_truth` answer. Low score = retriever missed relevant chunks.

4. **Context Precision** — Are retrieved chunks actually useful, or is there noise? High score = top-k chunks all relevant.

**Reference-free vs. reference-based:** Faithfulness, Answer Relevance, and Context Precision are reference-free (no ground truth needed). Context Recall needs a reference answer.

### Key Terms
- **RAGAS**: Framework for reference-free RAG evaluation using LLM-as-judge methodology
- **Faithfulness**: Metric measuring whether answer claims are grounded in retrieved context (0-1)
- **Answer Relevance**: Metric measuring whether the answer addresses the original question (0-1)
- **Context Recall**: Metric measuring retriever completeness — requires ground truth (0-1)
- **Context Precision**: Metric measuring retriever precision — ratio of useful to noisy chunks (0-1)
- **LLM-as-judge**: Pattern where an LLM evaluates another LLM's output, scalable proxy for human review
- **Evaluation dataset**: Set of (question, answer, contexts, ground_truth) tuples — RAGAS input

### Working Code

```python
# ragas_eval.py — standalone, runs in ~20 min
# pip install ragas openai datasets

import os
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall, context_precision

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "your-key-here")

eval_data = {
    "question": [
        "What was Samsung's revenue in 2023?",
        "How did Samsung's operating profit change from 2022 to 2023?",
    ],
    "answer": [
        "Samsung's revenue in 2023 was approximately 258.9 trillion KRW.",
        "Samsung's operating profit dropped from 43.4 trillion KRW in 2022 to 6.6 trillion KRW in 2023.",
    ],
    "contexts": [
        ["Samsung Electronics reported consolidated revenue of 258.94 trillion KRW for fiscal year 2023."],
        ["Operating profit for FY2023 was 6.57 trillion KRW, down from 43.38 trillion KRW in FY2022."],
    ],
    "ground_truth": [
        "Samsung's 2023 revenue was 258.94 trillion KRW.",
        "Operating profit fell from 43.38 trillion KRW in 2022 to 6.57 trillion KRW in 2023.",
    ],
}

dataset = Dataset.from_dict(eval_data)
result = evaluate(dataset=dataset, metrics=[faithfulness, answer_relevancy, context_recall, context_precision])
print(result.to_pandas())
```

**Note:** RAGAS calls GPT-4o internally — budget ~15-20 API calls per 3 samples.

### Exercises
1. Run RAGAS on 5 real FinAgent queries — identify whether bottleneck is retrieval (context_recall) or generation (faithfulness)
2. Modify one answer to include a claim NOT in its contexts — confirm faithfulness drops
3. Add a RAGAS eval node to SME Diagnostic AI's LangGraph pipeline as a quality gate before deck generation

### Resources
- RAGAS docs: https://docs.ragas.io/en/stable/
- RAGAS GitHub: https://github.com/explodinggradients/ragas

### Cross-apply
- **FinAgent**: context precision/recall gives retrieval quality signal your custom VectorDB currently lacks
- **SME Diagnostic AI**: replace Haiku scorer with RAGAS faithfulness gate
- **Lead Intelligence**: use answer_relevancy as outreach email quality scorer

---

## What's Next (AI Engineering Queue)
- LLMOps: observability with LangSmith
- Prompt caching (Anthropic API)
- Fine-tuning: LoRA on Hugging Face
- Streaming responses in FastAPI + Streamlit
- Agent memory patterns: episodic vs semantic vs procedural
- Tool use reliability: retry patterns, validation loops

---

---

# TRACK 2: SQL

## Week 1 Lesson — Aggregations: GROUP BY, HAVING, COUNT, SUM, AVG
_Source: learning/outputs/2026-03-24-sql-aggregations-group-by.md_

### Concept

You already know SELECT, WHERE, ORDER BY, and JOINs. Aggregations let you collapse many rows into summary numbers — totals, averages, counts — grouped by a category.

**Mental model: pandas groupby in SQL.**

```python
# pandas
df.groupby("industry")["revenue"].sum()
```
```sql
-- SQL equivalent
SELECT industry, SUM(revenue) FROM companies GROUP BY industry;
```

**Execution order (critical):**
```
FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY
```

WHERE filters rows BEFORE grouping. HAVING filters groups AFTER grouping. You cannot use `WHERE SUM(revenue) > 1000` — SUM doesn't exist at the WHERE stage. Use HAVING.

### Key Terms
- **GROUP BY**: Collapses all rows with the same column value into one group
- **COUNT(*)**: Counts rows per group. `COUNT(col)` skips NULLs
- **SUM(column)**: Sums values per group
- **AVG(column)**: Mean per group
- **HAVING**: Filters groups after aggregation — WHERE clause for aggregates
- **Aggregate function**: Takes multiple rows, returns one value (COUNT, SUM, AVG, MIN, MAX)
- **NULL in aggregates**: SUM, AVG, COUNT(col) all skip NULLs. COUNT(*) counts them

### Working Code (SQLite — same engine as FinAgent)

```sql
-- Setup
CREATE TABLE companies (
    id INTEGER PRIMARY KEY, name TEXT, industry TEXT,
    revenue INTEGER, employees INTEGER, founded_year INTEGER
);
INSERT INTO companies VALUES
(1,'Samsung Electronics','Technology',302000,270000,1969),
(2,'SK Hynix','Technology',44000,30000,1983),
(3,'LG Electronics','Technology',62000,74000,1958),
(4,'Hyundai Motor','Automotive',142000,120000,1967),
(5,'Kia','Automotive',89000,52000,1944),
(6,'POSCO','Steel',77000,18000,1968),
(7,'Kakao','Technology',8500,12000,2010),
(8,'Naver','Technology',9800,14000,1999);

-- Q1: COUNT per group
SELECT industry, COUNT(*) AS company_count FROM companies GROUP BY industry;

-- Q2: SUM revenue by industry
SELECT industry, SUM(revenue) AS total_revenue FROM companies GROUP BY industry;

-- Q3: Multiple aggregates
SELECT industry, COUNT(*) AS companies, SUM(revenue) AS total_revenue,
       AVG(revenue) AS avg_revenue, MAX(revenue) AS largest
FROM companies GROUP BY industry ORDER BY total_revenue DESC;

-- Q4: HAVING — only industries with total revenue > 100,000
SELECT industry, SUM(revenue) AS total_revenue
FROM companies GROUP BY industry HAVING SUM(revenue) > 100000;

-- Q5: WHERE + GROUP BY (filter first, then group)
SELECT industry, AVG(revenue) AS avg_revenue
FROM companies WHERE industry != 'Retail'
GROUP BY industry ORDER BY avg_revenue DESC;

-- Q6: CASE-based bucketing (Text2SQL frequently generates this)
SELECT
    CASE WHEN revenue >= 100000 THEN 'Large'
         WHEN revenue >= 30000 THEN 'Mid' ELSE 'Small' END AS size_bucket,
    COUNT(*) AS count, AVG(revenue) AS avg_revenue
FROM companies GROUP BY size_bucket ORDER BY avg_revenue DESC;
```

### Exercises
1. Total employees per industry, ordered by total employees descending
2. Industries where average company revenue > 50,000 (use HAVING)
3. Industries where ≥2 companies founded before 1970 AND total pre-1970 revenue > 100,000

### Resources
- SQLBolt Lesson 10: https://sqlbolt.com/lesson/select_queries_with_aggregates
- LeetCode SQL 50: https://leetcode.com/studyplan/top-sql-50/

### Cross-apply
- **FinAgent Text2SQL**: When GPT-4o generates SQL for "which sector has the highest average revenue?" it writes exactly the GROUP BY + AVG pattern. Knowing this lets you verify the generated SQL is correct.
- **Consulting Emulation**: Dashboard aggregates Samsung financials by year (GROUP BY fiscal_year) — this is the pattern.

---

## What's Next (SQL Queue)
- Week 2: Subqueries and CTEs (WITH clauses)
- Week 3: Window functions (ROW_NUMBER, RANK, LAG, LEAD, PARTITION BY)
- Week 4: Query optimization (indexes, EXPLAIN)
- Week 5: PostgreSQL specifics (JSONB, full-text search)

---

---

# TRACK 3: DATA ENGINEERING

## Week 1 Lesson — Advanced pandas: Method Chaining
_Source: learning/outputs/2026-03-24-data-engineering-pandas-advanced.md_

### Concept

Method chaining builds a pipeline — each step flows into the next. Instead of `df2 = df[...]; df3 = df2.assign(...); df4 = df3.rename(...)`, you write one readable expression.

Three reasons it matters:
1. **Readability** — transformation sequence visible top-to-bottom
2. **Debugging** — comment out one step to inspect intermediate state
3. **Pipeline thinking** — same mental model as LangGraph nodes: input → transform → output

### Key Terms
- **Method chaining**: Calling multiple pandas methods in sequence without intermediate variable assignment
- **.assign()**: Adds/overwrites columns without mutation. Returns new DataFrame. Safe for chains.
- **.pipe()**: Passes DataFrame into a function you define. Inserts arbitrary logic into a chain.
- **.query()**: Filters rows using string expression. Supports `@variable` for Python variables.
- **Inplace operations**: `inplace=True` returns None — breaks chains. Avoid entirely when chaining.

### Working Code

```python
import pandas as pd

raw_data = {
    "corp_name": ["삼성전자", "LG전자", "SK하이닉스", "삼성전자", "LG전자", "SK하이닉스"],
    "year": [2023, 2023, 2023, 2022, 2022, 2022],
    "revenue": [258_935, 84_178, 66_976, 302_231, 83_467, 44_641],
    "operating_profit": [6_567, 1_471, -7_733, 43_376, 794, 18_976],
    "employees": [267_800, 74_000, 30_000, 270_372, 75_000, 29_000],
}
df = pd.DataFrame(raw_data)

# Before: imperative
df2 = df[df["year"] == 2023].copy()
df2["op_margin"] = df2["operating_profit"] / df2["revenue"]
df2 = df2.sort_values("op_margin", ascending=False)

# After: method chaining
result = (
    df
    .query("year == 2023")
    .assign(
        op_margin=lambda x: x["operating_profit"] / x["revenue"],
        profitable=lambda x: x["operating_profit"] > 0,
    )
    .sort_values("op_margin", ascending=False)
    .reset_index(drop=True)
)

# .pipe() — insert custom logic
def normalize_revenue(df, scale=1_000):
    return df.assign(revenue_조=lambda x: x["revenue"] / scale)

def flag_distress(df, threshold=-0.05):
    return df.assign(distress=lambda x: x["op_margin"] < threshold)

result = (
    df
    .query("year == 2023")
    .assign(op_margin=lambda x: x["operating_profit"] / x["revenue"])
    .pipe(normalize_revenue, scale=1_000)
    .pipe(flag_distress)
    .sort_values("op_margin", ascending=False)
)
```

### Exercises
1. Refactor a 6-step imperative pandas block into a single method chain
2. Add `.pipe()` for a custom `add_health_tier(df)` function (A/B/C based on op_margin)
3. Build a full ETL mini-pipeline using only method chaining — filter, compute, normalize, flag, sort, export to CSV

### Resources
- pandas docs: https://pandas.pydata.org/docs/user_guide/basics.html#tablewise-function-application
- `.pipe()` docs: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.pipe.html

### Cross-apply
- **DART pipeline** (consulting-emulation): refactor `clean_financials()` into a chain
- **Lead Intelligence screener**: convert `_score_company()` to `.assign()` calls
- **LangGraph nodes**: each node that touches a DataFrame → one `.pipe()` chain

---

## What's Next (Data Engineering Queue)
- Week 2: Data cleaning patterns (missing values, outliers, type coercion)
- Week 3: dbt fundamentals
- Week 4: Simple ETL pipeline (DART → SQLite → pandas → report)
- Week 5: Polars (faster pandas alternative)

---

---

# TRACK 4: ML / DEEP LEARNING

## Week 1 Lesson — Bias-Variance, Train/Val/Test, Cross-Validation
_Source: learning/outputs/2026-03-24-ml-bias-variance-cross-validation.md_

### Concept

Your Samsung stock prediction model trained and evaluated on the same data — that accuracy is fake. This lesson fixes that.

**Bias vs. Variance:**
- **Bias** = model too simple. High error on both train and new data. Underfitting. Example: straight line on a curved trend.
- **Variance** = model too complex, chases noise. Low train error, high new-data error. Overfitting. Example: 15-degree polynomial on Samsung prices.

**Train / Val / Test Split:**
- Train (70-80%): what model learns from
- Validation (10-15%): tune hyperparameters, compare models (you look at this)
- Test (10-15%): report final performance exactly once (don't look until the end)

For time series (stock prices): split by time, NOT random shuffle.

**Cross-Validation:**
K-Fold: split into K folds, train on K-1, validate on 1, rotate K times, average scores. For time series: use `TimeSeriesSplit`.

### Key Terms
- **Bias**: error from model being too simple. High bias = underfitting
- **Variance**: error from model being too sensitive to training noise. High variance = overfitting
- **Generalization**: performance on unseen data
- **K-Fold cross-validation**: rotating validation scheme across K subsets
- **TimeSeriesSplit**: sklearn CV that preserves temporal order — required for financial data
- **Learning curve**: plot of train vs. val error as training size grows — diagnoses bias/variance

### Working Code

```python
import yfinance as yf
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

df = yf.download("005930.KS", start="2020-01-01", end="2024-12-31")[["Close"]].dropna()
for lag in [1, 5, 10, 20]:
    df[f"lag_{lag}"] = df["Close"].shift(lag)
df.dropna(inplace=True)

X, y = df.drop(columns=["Close"]).values, df["Close"].values

# Time-aware split (NO shuffle)
split_idx = int(len(X) * 0.8)
X_train, X_test = X[:split_idx], X[split_idx:]
y_train, y_test = y[:split_idx], y[split_idx:]

model = LinearRegression()
model.fit(X_train, y_train)
print(f"Train RMSE: {mean_squared_error(y_train, model.predict(X_train), squared=False):,.0f}")
print(f"Test  RMSE: {mean_squared_error(y_test,  model.predict(X_test),  squared=False):,.0f}")

# TimeSeriesSplit CV
tscv = TimeSeriesSplit(n_splits=5)
pipe = make_pipeline(StandardScaler(), LinearRegression())
cv_scores = -cross_val_score(pipe, X, y, cv=tscv, scoring="neg_root_mean_squared_error")
print(f"Mean CV RMSE: {cv_scores.mean():,.0f} ± {cv_scores.std():,.0f}")
```

### Exercises
1. Rerun your Samsung model with proper chronological split — compare RMSE to original
2. Compare single holdout RMSE vs. TimeSeriesSplit CV RMSE — identify if single split was misleading
3. Add PolynomialFeatures(degree=3) and plot learning curve — find sweet spot degree

### Resources
- ML Zoomcamp: https://github.com/DataTalks-Club/machine-learning-zoomcamp
- sklearn TimeSeriesSplit: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html

### Cross-apply
- **Consulting Emulation distress model**: use StratifiedKFold (preserves class balance), switch to regularized LR
- **Samsung project**: this lesson directly improves your existing model

---

## What's Next (ML Queue)
- Week 2: Classification (logistic regression, decision trees, random forest)
- Week 3: Model evaluation (precision, recall, F1, ROC-AUC)
- Week 4: PyTorch fundamentals (tensors, autograd, nn.Module)
- Week 5: Simple neural network from scratch in PyTorch

---

---

# TRACK 5: FINANCE (QUANTITATIVE)

## Week 1 Lesson — Time Value of Money: NPV and IRR in Python
_Source: learning/outputs/2026-03-24-finance-npv-irr-python.md_

### Concept

You already built a DCF model. The DCF IS time value of money — you discounted future cash flows back to present value. This lesson makes the mechanism explicit and gives you clean Python tools.

**NPV — Net Present Value:**
```
NPV = sum( CF_t / (1 + r)^t ) for t = 0, 1, ..., n
```
- NPV > 0 → accept (creates value)
- NPV < 0 → reject (destroys value)

In consulting M&A: run NPV on target company's projected free cash flows. Discount rate = WACC (8-12% for Korean mid-cap).

**IRR — Internal Rate of Return:**
The discount rate where NPV = 0. Solved numerically. Decision rule: if IRR > WACC, proceed.

IRR is the headline number clients understand. "IRR of 22% over 5 years" is cleaner than showing NPV with an assumed discount rate.

**Korean context:** Korean SME hurdle rate is typically 10-15% (bank debt ~5-6% + equity risk premium). DART 사업보고서 includes planned capex — you can pull these and compute IRR to evaluate if announced investments make financial sense.

### Key Terms
- **Discount rate (r)**: Rate to convert future cash to present value. M&A: WACC. Projects: hurdle rate
- **WACC**: Blended cost of debt and equity. E.g., 40% debt at 6% + 60% equity at 12% = 9.6%
- **NPV**: Sum of all discounted cash flows including initial outlay
- **IRR**: Discount rate that makes NPV = 0. Solved numerically
- **Hurdle rate**: Minimum acceptable IRR. Project proceeds only if IRR > hurdle rate
- **Sensitivity analysis**: Re-running NPV across discount rate range to test robustness

### Working Code

```python
# pip install numpy-financial numpy pandas
import numpy_financial as npf
import numpy as np
import pandas as pd

# Korean SME: 500M KRW automated packaging line
cash_flows = [-500, 80, 120, 150, 180, 200]  # M KRW, year 0-5
wacc = 0.10

npv = npf.npv(wacc, cash_flows)
irr = npf.irr(cash_flows)

print(f"NPV at {wacc*100:.0f}%: {npv:.1f}M KRW")
print(f"IRR: {irr*100:.2f}%")
print(f"Decision: {'PROCEED' if irr > wacc else 'REJECT'} — IRR {'>' if irr > wacc else '<'} WACC")

# Sensitivity analysis
rates = np.arange(0.05, 0.20, 0.01)
sensitivity = pd.DataFrame({
    "Rate (%)": (rates * 100).round(0).astype(int),
    "NPV (M KRW)": [round(npf.npv(r, cash_flows), 1) for r in rates]
})
print(sensitivity.to_string(index=False))

# Multi-project comparison
projects = {
    "Packaging Line":   [-500, 80, 120, 150, 180, 200],
    "Logistics System": [-300, 60,  90, 100, 110, 120],
    "ERP Upgrade":      [-200, 30,  50,  70,  80,  90],
}
for name, cfs in projects.items():
    pnpv, pirr = npf.npv(0.10, cfs), npf.irr(cfs)
    print(f"{name}: NPV={pnpv:.1f}M | IRR={pirr*100:.1f}% | {'PROCEED' if pirr > 0.10 else 'REJECT'}")
```

### Exercises
1. Calculate NPV for Korean retail chain opening new store — 800M KRW investment, 5-year cash flows, WACC=12%
2. Compare two mutually exclusive capex projects using both IRR and NPV — explain why they might disagree
3. Build 2D sensitivity table: rows=discount rates 6-18%, columns=bear/base/bull scenarios — consulting deck format

### Resources
- PyQuant News: https://pyquantnews.com/
- numpy_financial: https://numpy.org/numpy-financial/

### Cross-apply
- **Consulting Emulation**: replace hardcoded DCF discount rate with WACC from DART financials
- **Lead Intelligence**: layer NPV/IRR on AI readiness score — companies where AI investment IRR > 15% = priority outreach

---

## What's Next (Finance Queue)
- Week 2: Portfolio theory (Markowitz, efficient frontier)
- Week 3: Factor models (Fama-French 3-factor)
- Week 4: Options basics (Black-Scholes)
- Week 5: Korean market specifics (KOSPI, KOSDAQ, sector ETFs)

---

---

# HOW TO STUDY WITH GEMINI

## Suggested prompts to use:

**Quiz mode:**
- "Quiz me on RAGAS metrics — ask me to explain each one in my own words"
- "Give me 3 SQL aggregation exercises harder than the ones in the lesson"
- "What are 5 ways to misuse pandas method chaining?"

**Explain differently:**
- "Explain bias-variance tradeoff using a non-ML analogy"
- "How does IRR relate to the discount rate in a way a business student would understand?"

**Code review:**
- "Here's my pandas chain — what's wrong with it: [paste code]"
- "Here's my SQL query — is the HAVING clause in the right place?"

**Cross-track connections:**
- "How does SQL aggregation connect to pandas groupby? What can SQL do that pandas can't?"
- "How would I use NPV/IRR concepts inside a LangGraph node for the consulting emulation project?"

**New exercises:**
- "Give me a new RAGAS exercise using Korean financial data"
- "Create a SQL challenge that combines GROUP BY with a CASE statement"

---

_Bundle generated: 2026-03-24 | Tracks: 5 | Lessons: 5 | Total content: Week 1 seed lessons_
_Next update: after Week 2 lessons are generated_
