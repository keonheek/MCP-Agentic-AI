---
name: data-analyst
description: Adapted from Anthropic's open-source Cowork data plugin. Use for data analysis tasks — interpreting datasets, writing pandas/numpy code, building visualizations, SQL queries, explaining statistical concepts, and debugging data pipelines. Trigger phrases: "analyze this data", "write me a SQL query for X", "debug this pandas code", "explain this chart", "clean this dataset", "what does this metric mean statistically".
---

# Data Analyst Skill

Adapted from Anthropic's knowledge-work-plugins/data. Specialized for Keonhee's stack: Python, pandas, numpy, SQLite, OpenAI embeddings, Streamlit.

Updated 2026-03-11: Added consulting case framing, advanced SQL patterns, and QuantumBlack/BCG prep context.

---

## What you know about Keonhee's data stack

- **Python** — primary language. numpy, pandas, standard library.
- **SQLite** — FinAgent DB (Samsung, SK Hynix, LG Electronics financial data, 2020-2024). Table: `financials`.
- **OpenAI Embeddings** — `text-embedding-3-small` (1536 dims). Used for custom VectorDB in RAG pipelines.
- **Pinecone** — vector DB in RAG demo (kearney-demo index, cosine similarity, AWS us-east-1)
- **Supabase** — conversation history storage in RAG demo. Postgres under the hood.
- **Streamlit** — data visualization and frontend. Use `@st.cache_resource` for expensive objects.
- **yfinance** — stock price data (Samsung Forecast project)

---

## Analysis workflow

1. **Understand the data** — what is each column? What's the unit? What time range? Any NULLs?
2. **Frame the question** — what decision does this analysis inform?
3. **Choose the right tool** — SQL for structured queries, pandas for transformation, numpy for math
4. **Validate** — check for duplicates, nulls, outliers before drawing conclusions
5. **Communicate clearly** — lead with the finding, support with the numbers

---

## Standard patterns

### SQLite query (FinAgent pattern)
```python
import sqlite3, pandas as pd

conn = sqlite3.connect("data/finagent.db")
df = pd.read_sql_query(
    "SELECT * FROM financials WHERE company = 'Samsung Electronics' ORDER BY year",
    conn
)
conn.close()
```

### Advanced SQL patterns (McKinsey QuantumBlack prep — practice these)
```sql
-- YoY growth rate
SELECT year,
       revenue,
       LAG(revenue) OVER (PARTITION BY company ORDER BY year) AS prev_revenue,
       ROUND((revenue - LAG(revenue) OVER (PARTITION BY company ORDER BY year))
             / LAG(revenue) OVER (PARTITION BY company ORDER BY year) * 100, 2) AS yoy_pct
FROM financials
WHERE company = 'Samsung Electronics';

-- Rank companies by margin in each year
SELECT company, year,
       ROUND(operating_profit / revenue * 100, 2) AS op_margin,
       RANK() OVER (PARTITION BY year ORDER BY operating_profit / revenue DESC) AS margin_rank
FROM financials;

-- Cumulative revenue
SELECT company, year, revenue,
       SUM(revenue) OVER (PARTITION BY company ORDER BY year) AS cumulative_revenue
FROM financials;
```

### Pandas quick profile
```python
print(df.shape)
print(df.dtypes)
print(df.isnull().sum())
print(df.describe())
```

### Cosine similarity (custom VectorDB pattern)
```python
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

---

## Consulting case framing

When producing analysis for interview prep or case practice, format output as a consulting deliverable:
- Lead with the "so what" (insight), not the numbers
- Support with 2-3 data points
- End with a recommendation or next question to investigate

Example:
> "Samsung's operating margin fell 8pp in 2023 — driven by the memory downcycle (revenue -20% while fixed costs held). Recovery in 2024 suggests the trough has passed. Key question: is the margin recovery structural (new HBM capacity) or cyclical (restocking)?"

---

## Output formats

**Data summary** (default when given a raw dataset):
- Row count, column count, data types, null counts
- 3 key observations
- One recommendation or next step

**SQL query output:**
- The query, clearly formatted
- What it returns (column names + data types)
- One-line "so what" — what does this result mean?

**Analysis report:**
- Findings first, code second
- Include the "so what" — not just the numbers, but what they imply

---

## Slash commands

- `/data-analyst:profile` — quick profile of a dataset (shape, types, nulls, summary stats)
- `/data-analyst:query` — write a SQL query for a described question
- `/data-analyst:clean` — identify and fix data quality issues in a dataset
- `/data-analyst:visualize` — write Streamlit or matplotlib code to visualize data
- `/data-analyst:explain` — explain a statistical concept or metric in plain language
- `/data-analyst:case` — format a data insight as a consulting case answer

---

## Notes
- Default to pandas + SQLite for Keonhee's projects — no Spark, no Dask unless asked
- Prefer readable code over clever one-liners — it needs to be explainable in an interview
- If given messy data, always check for duplicates and nulls before analysis
- For embedding-related tasks, always use `text-embedding-3-small` (1536 dims) unless asked otherwise
- SQL window functions (LAG, RANK, SUM OVER) are key for QuantumBlack/BCG interviews — practice these
