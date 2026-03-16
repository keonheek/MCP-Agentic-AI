# McKinsey QuantumBlack — Interview Prep

_Fit: 72% — biggest gap is ML model training + cloud. Close AWS gap first._
_Language: English (McKinsey interviews often in English, especially for QuantumBlack roles)_
_Note: No Korea-specific QB internship confirmed for 2026 — may need to apply to global program._

---

## QuantumBlack vs. McKinsey Consulting

| Aspect | McKinsey (General) | QuantumBlack (QB) |
|--------|-------------------|-------------------|
| Work | Strategy consulting | AI/ML engineering + data science for clients |
| Interviews | Case + PST/Problem Solving Game | Case + technical Python/SQL/ML screen |
| Background | Business, economics, MBAs | CS, stats, engineering + business |
| Keonhee's angle | Unusual background for McKinsey | Rare: business + AI technical at student level |

---

## Technical Skills QB Looks For (from job descriptions)

| Skill | Keonhee's Status | Gap |
|-------|-----------------|-----|
| Python (core) | ✅ FinAgent, DART MCP — production-grade | None |
| SQL | ✅ Text2SQL pipeline built | Window functions — practice needed |
| Pandas, NumPy | ✅ Used throughout | None |
| Machine learning fundamentals | Partial — applied ML (inference), not trained | No training experience |
| PySpark | Gap | Not encountered |
| Databricks | Gap | Not encountered |
| Airflow | Gap | Not encountered |
| Kedro | Gap | Not encountered |
| LangGraph | ✅ FinAgent is LangGraph — production | None (strength) |
| LLM APIs | ✅ OpenAI + Anthropic | None |
| Cloud (AWS) | Gap | Close via AWS Free Tier project |

**Priority gaps to close before applying:**
1. SQL window functions — 6 hours (see `references/consulting/sql-practice.md`)
2. AWS deployment — 1 day (see `references/consulting/aws-quickstart.md`)
3. PySpark basics — 2 hours (conceptual, enough for talking points)

---

## PySpark — 2-Hour Crash Course (Just Enough)

QuantumBlack uses PySpark for large-scale data processing. You don't need to be an expert — you need to know the mental model.

**Core concept:** PySpark = pandas, but distributed across a cluster. The same operations (filter, groupby, join) but designed for billion-row datasets on multiple machines.

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lag, sum as spark_sum
from pyspark.sql.window import Window

# Initialize Spark
spark = SparkSession.builder.appName("FinancialAnalysis").getOrCreate()

# Load data (equivalent to pd.read_csv but distributed)
df = spark.read.csv("s3://bucket/financials.csv", header=True, inferSchema=True)

# Filter (equivalent to df[df['year'] == 2024])
df_2024 = df.filter(col("year") == 2024)

# GroupBy + aggregation (equivalent to df.groupby().agg())
df_agg = df.groupBy("company").agg({"revenue": "sum", "cost": "avg"})

# Window functions (same concept as SQL PARTITION BY)
window_spec = Window.partitionBy("company").orderBy("quarter")
df_with_lag = df.withColumn("prev_revenue", lag("revenue", 1).over(window_spec))

# Write results back to S3
df_agg.write.parquet("s3://bucket/output/")
```

**Interview talking point:**
> "I haven't used PySpark in production, but I've worked extensively with pandas and SQL window functions. PySpark's distributed model is conceptually similar — the same groupBy/filter/join operations, scaled horizontally. I'd expect a learning curve on the Spark-specific optimizations like caching and partition tuning, but the data manipulation patterns would transfer directly."

---

## McKinsey Interview Format

### Problem Solving Game (PSG)
McKinsey replaced the written case (PST) with the **Problem Solving Game** (Solve / Imbellus):
- Online game-based assessment (30 min)
- Assesses cognitive flexibility, pattern recognition, systems thinking
- No specific preparation — pattern recognition practice helps
- Takes place before case interviews

### Case Interviews (Candidate-Led)
McKinsey uses **candidate-led cases** — you drive the structure:

1. You hear the case premise
2. You ask clarifying questions
3. **You propose the framework** — interviewer doesn't guide you
4. You request data you need
5. You analyze and synthesize
6. You deliver a recommendation

This is harder than BCG's interviewer-led format. You have to know what to ask for.

---

## McKinsey Case — Candidate-Led Template

### Opening
> "Thank you. Before I start, may I ask [1-2 clarifying questions]? ... Thank you. I'd like to take a moment to structure my approach."

*(30 seconds of silence is fine — don't rush)*

### Framework Structure
> "To diagnose [the problem], I'd look at three areas: [Area 1], [Area 2], and [Area 3]. I'd like to start with [Area 1] as I believe that's most likely to explain [the core issue]. Does that approach make sense?"

Always check in — McKinsey interviewers will redirect you if you're off track.

### Requesting Data
Don't wait for the interviewer to give you data. **Ask for it:**
> "To test this hypothesis, I'd need to see the [revenue breakdown / cost structure / market share data]. Do you have that information?"

### Synthesizing
After each section, pause and synthesize:
> "So from the revenue analysis, it looks like [finding]. This suggests [implication]. Let me move to costs to see if that confirms or changes the picture."

### Final Recommendation
> "Based on my analysis, my recommendation is [specific action]. The primary driver is [key finding]. The main risk is [X], and I'd mitigate that by [Y]. The top next step would be [immediate action]."

---

## McKinsey Behavioral Questions

### "Tell me about yourself"

> I'm Keonhee Kim, studying Business Administration at Sungkyunkwan University in Korea. Over the past year, I've been building production agentic AI systems — not tutorials or demos, but live deployed applications. My main project is FinAgent: a multi-agent financial analysis system using LangGraph, Text2SQL, and a custom vector database I built from scratch when standard tools weren't compatible with my setup. I'm one of the rare students who combines business administration training with hands-on AI engineering experience. I'm targeting QuantumBlack because it's where those two things come together at the highest level.

### "Why QuantumBlack specifically?"

> QuantumBlack works at the intersection of AI engineering and client business outcomes — which is exactly where my skills sit. I've built systems that would be considered QB deliverables: multi-agent pipelines, RAG systems, custom data tooling. But I've also studied how business strategy works. Most AI engineers can't explain what their system means for client operations. Most business consultants can't build the system. I can do both, and QuantumBlack is where that combination is most valued.

### "Describe a time you made a technical decision under uncertainty"

STAR format:
> **Situation:** FinAgent needed a vector database for semantic search. ChromaDB was the standard choice, but it was incompatible with Python 3.14 — our production environment.
> **Task:** Find an alternative that wouldn't compromise the deployment timeline.
> **Action:** Analyzed what ChromaDB was actually doing — cosine similarity over high-dimensional vectors. Built a custom implementation in 200 lines of Python using OpenAI embeddings and NumPy, benchmarked it against Pinecone responses on a 100-document corpus, confirmed comparable results.
> **Result:** Deployed on time with no external dependency. The custom VectorDB is now one of the most-discussed technical decisions in the FinAgent GitHub README because it demonstrates understanding of the underlying math, not just library usage.

---

## Technical Interview Prep (QB-Specific)

QB technical screens may ask Python/SQL/ML questions. These are what QB engineers actually do:

### Python: Data Manipulation

```python
# Given a dataframe of quarterly revenues, compute YoY growth per company
import pandas as pd

df = pd.DataFrame({
    'company': ['A', 'A', 'A', 'B', 'B', 'B'],
    'year': [2022, 2023, 2024, 2022, 2023, 2024],
    'revenue': [100, 120, 110, 200, 180, 220]
})

# Sort first — critical for lag calculations
df = df.sort_values(['company', 'year'])

# YoY growth using shift (equivalent to LAG in SQL)
df['prev_revenue'] = df.groupby('company')['revenue'].shift(1)
df['yoy_growth'] = (df['revenue'] - df['prev_revenue']) / df['prev_revenue']

print(df)
```

### ML: Explain Precision vs. Recall

> Precision: of everything I predicted as positive, how many were actually positive? (False positive cost)
> Recall: of everything that was actually positive, how many did I catch? (False negative cost)
>
> In fraud detection: high recall matters (don't miss fraud), even at cost of more false alarms.
> In medical diagnosis: high recall critical (missing cancer is worse than extra follow-ups).
> In FinAgent's loan default case: recall is critical — missing a default is much worse than rejecting a good loan.

### ML: Overfitting

> Model fits training data too closely, fails on new data. Signs: high training accuracy, low validation accuracy. Fix: regularization (L1/L2), dropout, more data, simpler model, cross-validation.

---

## Application Strategy

1. **Check mckinsey.com/careers weekly** for "QuantumBlack Korea 2026" — no Korea-specific listing confirmed yet
2. **Consider global program** — QB global immersion programs (US, UK, Germany) are open for Summer 2026
3. **Email McKinsey Korea** (mckinsey.com/kr) to ask directly about 2026 QB internship availability in Korea
4. **Apply to global program as backup** — being willing to relocate for Summer demonstrates commitment

### Cover Letter: `projects/next-ai-role/cover-letter-mckinsey.md` ✅

---

## Application Checklist

- [ ] Cover letter ready: `projects/next-ai-role/cover-letter-mckinsey.md` ✅
- [ ] Check mckinsey.com/careers for Korea-specific QB listing
- [ ] Close SQL window function gap first (see sql-practice.md)
- [ ] Deploy FinAgent to AWS Lambda (see aws-quickstart.md)
- [ ] Learn PySpark basics (2 hrs) — just enough for talking points
- [ ] Prepare Problem Solving Game — pattern recognition practice
- [ ] Prepare candidate-led case structure — 5+ practice cases
