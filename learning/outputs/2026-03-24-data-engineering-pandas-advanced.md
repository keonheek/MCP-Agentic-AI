# Data Engineering — Advanced pandas: Method Chaining
_Track 3 | Week 1 | Date: 2026-03-24_

---

## Concept (10 min read)

Most pandas code written by beginners looks like this: create a dataframe, assign it to a variable, filter it, assign again, transform, assign again. By the time you have five intermediate variables (`df`, `df2`, `df_filtered`, `df_clean`, `df_final`), debugging means checking which version of the dataframe is actually correct.

Method chaining solves this. Instead of saving intermediate state, you build a pipeline — each step flows directly into the next, left to right (or top to bottom with backslash). The result is code that reads like a data transformation recipe.

This matters for three reasons:

**1. Readability.** A chain tells the story of what happened to the data in sequence. An imperative block hides the sequence inside variable names.

**2. Debugging.** You can comment out one step in the chain to see the intermediate state. With scattered variable assignments you have to track down where the mutation happened.

**3. Pipeline thinking.** Method chaining forces you to think in transforms, not states. This is exactly the mental model used in production ETL pipelines, dbt, and LangGraph nodes — each node receives input, outputs something, passes it on.

You already use pandas in FinAgent's DART pipeline (financial statement cleaning, Samsung data normalization) and in Lead Intelligence (screener scoring). Both have multi-step transformations that are currently imperative. Refactoring them to chains would make them easier to maintain and extend.

---

## Key Terms

- **Method chaining**: Calling multiple pandas methods in sequence on the same object without intermediate variable assignment. Each method returns a DataFrame or Series.
- **.assign()**: Adds or overwrites columns without mutating the original. Returns a new DataFrame. Safe for chains because it does not modify in place.
- **.pipe()**: Passes the DataFrame into a function you define. Lets you insert arbitrary logic — including multi-argument functions — into a chain without breaking it.
- **.query()**: Filters rows using a string expression. Cleaner than boolean indexing inside a chain. Supports `@variable` syntax to reference Python variables.
- **.loc[]**: Label-based indexing. Chainable when used to select columns or rows; returns a DataFrame so you can keep chaining.
- **Inplace operations**: Methods with `inplace=True` return `None` — they break chains. Avoid them entirely when chaining.
- **Functional transform**: A pure function that takes a DataFrame and returns a DataFrame. The correct signature for `.pipe()`.

---

## Working Code

### Setup — Korean financial data context

```python
import pandas as pd
import numpy as np

# Sample: DART-style financial statement data for 3 Korean manufacturers
raw_data = {
    "corp_name": ["삼성전자", "LG전자", "SK하이닉스", "삼성전자", "LG전자", "SK하이닉스"],
    "year": [2023, 2023, 2023, 2022, 2022, 2022],
    "revenue": [258_935, 84_178, 66_976, 302_231, 83_467, 44_641],      # 억원
    "operating_profit": [6_567, 1_471, -7_733, 43_376, 794, 18_976],
    "net_income": [15_487, 1_236, -9_144, 55_654, 1_142, 14_966],
    "employees": [267_800, 74_000, 30_000, 270_372, 75_000, 29_000],
}
df = pd.DataFrame(raw_data)
```

---

### Before: imperative style

```python
# Imperative — hard to follow, mutation risk
df2 = df[df["year"] == 2023].copy()
df2["op_margin"] = df2["operating_profit"] / df2["revenue"]
df2["profitable"] = df2["operating_profit"] > 0
df2 = df2.rename(columns={"corp_name": "company"})
df2 = df2.sort_values("op_margin", ascending=False)
df2 = df2.reset_index(drop=True)
result = df2[["company", "revenue", "op_margin", "profitable"]]
```

---

### After: method chaining with .assign() and .query()

```python
result = (
    df
    .query("year == 2023")
    .assign(
        op_margin=lambda x: x["operating_profit"] / x["revenue"],
        profitable=lambda x: x["operating_profit"] > 0,
    )
    .rename(columns={"corp_name": "company"})
    .sort_values("op_margin", ascending=False)
    .reset_index(drop=True)
    [["company", "revenue", "op_margin", "profitable"]]
)
```

Same result. Fewer variables. The transformation sequence is readable top to bottom.

---

### .pipe() — inserting custom logic

Use `.pipe()` when the transformation needs more than a lambda — multi-line logic, parameters, or reuse across pipelines.

```python
def normalize_revenue(df, scale=1_000):
    """Convert 억원 to 조원 for display."""
    return df.assign(revenue_조=lambda x: x["revenue"] / scale)

def flag_distress(df, op_margin_threshold=-0.05):
    """Flag companies with operating margin below threshold."""
    return df.assign(
        distress=lambda x: x["op_margin"] < op_margin_threshold
    )

result = (
    df
    .query("year == 2023")
    .assign(op_margin=lambda x: x["operating_profit"] / x["revenue"])
    .pipe(normalize_revenue, scale=1_000)
    .pipe(flag_distress, op_margin_threshold=-0.05)
    .sort_values("op_margin", ascending=False)
    .reset_index(drop=True)
)

print(result[["corp_name", "revenue_조", "op_margin", "distress"]])
```

`.pipe(fn, arg)` is equivalent to `fn(df, arg)` — it just keeps the chain unbroken.

---

### .query() with Python variable references

```python
target_year = 2023
min_revenue = 50_000  # 억원

result = (
    df
    .query("year == @target_year and revenue >= @min_revenue")
    .assign(rev_per_employee=lambda x: x["revenue"] / x["employees"])
    .sort_values("rev_per_employee", ascending=False)
)
```

`@variable` inside `.query()` pulls from the local Python scope. Cleaner than f-string injection into query strings.

---

### Full mini-ETL chain

```python
def add_yoy_growth(df):
    """Merge current year with prior year to compute YoY revenue growth."""
    current = df.query("year == 2023")[["corp_name", "revenue"]].rename(columns={"revenue": "rev_2023"})
    prior   = df.query("year == 2022")[["corp_name", "revenue"]].rename(columns={"revenue": "rev_2022"})
    return (
        current
        .merge(prior, on="corp_name", how="left")
        .assign(yoy_growth=lambda x: (x["rev_2023"] - x["rev_2022"]) / x["rev_2022"])
    )

pipeline_result = (
    df
    .query("year == 2023")
    .assign(
        op_margin=lambda x: x["operating_profit"] / x["revenue"],
        net_margin=lambda x: x["net_income"] / x["revenue"],
    )
    .pipe(normalize_revenue, scale=1_000)
    .pipe(flag_distress)
    .merge(
        df.pipe(add_yoy_growth)[["corp_name", "yoy_growth"]],
        on="corp_name",
        how="left"
    )
    .sort_values("op_margin", ascending=False)
    .reset_index(drop=True)
)

print(pipeline_result[["corp_name", "revenue_조", "op_margin", "net_margin", "yoy_growth", "distress"]])
```

---

## Exercises

**Exercise 1 — Refactor an imperative block**

The DART pipeline in Lead Intelligence has a scoring section that looks like this:

```python
df = raw_df.copy()
df = df[df["revenue"] > 10_000]
df["score"] = df["operating_profit"] / df["revenue"] * 100
df["rank"] = df["score"].rank(ascending=False)
df = df.sort_values("rank")
df = df.reset_index(drop=True)
```

Rewrite this as a single method chain. No intermediate assignments.

---

**Exercise 2 — Add .pipe() for a custom transform**

You need to add a "financial health tier" label (A / B / C) based on operating margin thresholds:
- A: op_margin >= 0.10
- B: 0.0 <= op_margin < 0.10
- C: op_margin < 0.0

Write a `add_health_tier(df)` function and insert it into the chain from Exercise 1 using `.pipe()`.

---

**Exercise 3 — Challenge: full ETL mini-pipeline**

Using only method chaining (no intermediate variable assignments after the initial `df = pd.DataFrame(...)`), build a pipeline that:

1. Filters to year == 2023
2. Computes op_margin, net_margin, rev_per_employee
3. Normalizes revenue to 조원 via `.pipe()`
4. Flags distressed companies (op_margin < 0) via `.pipe()`
5. Assigns a health tier via `.pipe()`
6. Sorts by op_margin descending
7. Selects only: corp_name, revenue_조, op_margin, net_margin, health_tier, distress
8. Exports to `dart_screener_2023.csv` via `.to_csv()` at the end of the chain

The final pipeline should be readable as a single expression (use parentheses for multi-line).

---

## Resources

- Primary: pandas docs, Method Chaining section — https://pandas.pydata.org/docs/user_guide/basics.html#tablewise-function-application
- `.pipe()` docs — https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.pipe.html
- Video: Matt Harrison, "Method Chaining in pandas" — search YouTube
- Pyjanitor library (optional, advanced) — extends pandas with more chainable verbs

---

## Cross-apply

**DART pipeline (`projects/consulting-emulation/data/dart_pipeline.py`)** — the financial statement cleaning steps (rename columns, fill NaN, compute ratios) are currently imperative. Refactor the `clean_financials()` function into a chain. Each cleaning step becomes one line. Add `.pipe(validate_schema)` at the end to assert column types before the data hits the LangGraph node.

**Lead Intelligence screener (`projects/lead-intelligence/dart_screener.py`)** — `_score_company()` builds a score from 4 weighted dimensions. Convert the manual dict-building into `.assign()` calls so the scoring logic is traceable in one chain. Add `.pipe(normalize_scores)` to scale to 0-100 before returning.

**GEO audit data (`projects/geo-agency/`)** — audit results come back as dicts from the scoring engine. When aggregating results across multiple companies (batch audit), load into a DataFrame and use `.assign()` + `.query()` to filter and rank. Keeps the audit summary generation clean without temp variables.

**General pattern for LangGraph nodes** — each node that touches a DataFrame should follow this structure:

```python
def score_node(state: AgentState) -> AgentState:
    result = (
        pd.DataFrame(state["raw_data"])
        .pipe(clean)
        .pipe(score)
        .pipe(rank)
    )
    return {**state, "scored_data": result.to_dict("records")}
```

One chain per node. Easy to test each `.pipe()` step in isolation.
