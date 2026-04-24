# Data Engineering: Data Cleaning Patterns
_Date: 2026-04-22 | Level: beginner-intermediate | Time: ~35 min_

---

## Concept

Data cleaning is the process of detecting and fixing problems in raw data before it enters a pipeline. The three categories you'll hit constantly: **missing values** (NaN, None, empty strings), **outliers** (values that are statistically extreme or logically impossible), and **type coercion** (a column that should be float is stored as string because one row had a dash in it).

In production pipelines — and in every project you've already built — bad data causes silent failures. FinAgent's DART pipeline ingests financial statements where some fields are `"-"` instead of 0. If you don't handle that before computing ratios, you get `NaN` in downstream nodes and the LangGraph graph returns garbage without raising an error. Data cleaning is the difference between a pipeline that fails loudly and one that fails silently.

The key insight: cleaning should be a **dedicated, explicit step** in the pipeline, not scattered across every function that touches the data. One `clean()` function that you can test independently is worth more than 10 conditional checks sprinkled through scoring logic.

**Why it matters for your stack:** LangGraph nodes that receive DataFrames assume clean input. If you centralize cleaning into a `.pipe(clean)` step (which you now know from Week 1), every downstream node is protected. This is also the mental model behind dbt's staging layer — raw in, clean out, then transform.

---

## Key Terms

- **NaN (Not a Number)**: pandas' representation of missing numeric data. `pd.isna()` detects it. Arithmetic with NaN propagates NaN.
- **None vs NaN**: `None` is Python null, `NaN` is a float. pandas converts both to `NaN` in numeric columns but keeps `None` as object in string columns.
- **Imputation**: Filling missing values with a substitute — mean, median, forward-fill, or a sentinel like 0.
- **Outlier**: A value that is either statistically extreme (IQR method, z-score) or logically impossible (negative revenue).
- **IQR (Interquartile Range)**: Q3 - Q1. Values outside `[Q1 - 1.5*IQR, Q3 + 1.5*IQR]` are flagged as outliers.
- **Type coercion**: Forcing a column to the correct dtype. `pd.to_numeric(col, errors='coerce')` turns unparseable strings into NaN instead of crashing.
- **Sentinel value**: A placeholder that means "missing" but isn't NaN — e.g., 0, -1, "-", "N/A". Must be converted to NaN before arithmetic.

---

## Code

```python
import pandas as pd
import numpy as np

# Raw DART-style financial data — mimics real problems in the DART API response
raw_data = {
    "corp_name":        ["삼성전자", "LG전자", "SK하이닉스", "카카오", "네이버", "크래프톤"],
    "year":             [2023, 2023, 2023, 2023, 2023, 2023],
    "revenue":          ["258935", "84178", "-", "71967", "98,202", None],   # string, sentinel, comma, null
    "operating_profit": [6567, 1471, -7733, None, 15020, 4200],
    "employees":        [267800, 74000, 30000, 3500, 4800, "N/A"],           # sentinel string
    "founded_year":     [1969, 1958, 1983, 2010, 1999, 2007],
}
df = pd.DataFrame(raw_data)
print("=== RAW ===")
print(df.dtypes)
print(df)
```

---

### Step 1: Handle sentinel values before type conversion

```python
# Sentinels that mean "missing" but aren't NaN
SENTINELS = ["-", "N/A", "NA", "null", "none", ""]

def replace_sentinels(df: pd.DataFrame) -> pd.DataFrame:
    # Replace only in object (string) columns — don't touch numerics
    obj_cols = df.select_dtypes(include="object").columns
    return df.assign(**{
        col: df[col].replace(SENTINELS, np.nan)
        for col in obj_cols
    })
```

---

### Step 2: Type coercion — force columns to correct dtype

```python
NUMERIC_COLS = ["revenue", "operating_profit", "employees"]

def coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    for col in NUMERIC_COLS:
        if col in cleaned.columns:
            # Strip commas (e.g. "98,202" -> "98202"), then convert
            if cleaned[col].dtype == object:
                cleaned[col] = cleaned[col].str.replace(",", "", regex=False)
            # errors='coerce': unparseable values become NaN instead of raising
            cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")
    return cleaned
```

---

### Step 3: Handle missing values — impute or drop

```python
def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df
        # Revenue missing = can't use the row at all
        .dropna(subset=["revenue"])
        # Operating profit missing: impute with 0 (conservative — treat as breakeven)
        .assign(operating_profit=lambda x: x["operating_profit"].fillna(0))
        # Employees missing: impute with column median
        .assign(employees=lambda x: x["employees"].fillna(x["employees"].median()))
    )
```

---

### Step 4: Detect and handle outliers (IQR method)

```python
def flag_outliers(df: pd.DataFrame, col: str) -> pd.DataFrame:
    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return df.assign(**{f"{col}_outlier": ~df[col].between(lower, upper)})

def flag_logical_errors(df: pd.DataFrame) -> pd.DataFrame:
    # Revenue must be positive (negative revenue is logically impossible)
    return df.assign(revenue_invalid=lambda x: x["revenue"] <= 0)
```

---

### Step 5: Combine into a single clean() pipeline

```python
def clean(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df
        .pipe(replace_sentinels)
        .pipe(coerce_types)
        .pipe(handle_missing)
        .pipe(flag_logical_errors)
        .pipe(flag_outliers, col="revenue")
    )

cleaned = clean(df)
print("\n=== CLEANED ===")
print(cleaned.dtypes)
print(cleaned[["corp_name", "revenue", "operating_profit", "employees", "revenue_invalid", "revenue_outlier"]])
```

---

### Validation: assert your clean data meets expectations

```python
def validate(df: pd.DataFrame) -> pd.DataFrame:
    assert df["revenue"].isna().sum() == 0, "revenue has nulls after cleaning"
    assert (df["revenue"] > 0).all(), "revenue has non-positive values"
    assert df["operating_profit"].isna().sum() == 0, "operating_profit has nulls"
    assert df["employees"].isna().sum() == 0, "employees has nulls"
    return df  # return df so it can stay in the chain

result = (
    df
    .pipe(clean)
    .pipe(validate)
    .assign(op_margin=lambda x: x["operating_profit"] / x["revenue"])
    .sort_values("op_margin", ascending=False)
    .reset_index(drop=True)
)

print("\n=== FINAL PIPELINE RESULT ===")
print(result[["corp_name", "revenue", "op_margin"]])
```

Adding `validate()` at the end of the clean step means bad data raises an `AssertionError` loudly instead of propagating silently into downstream nodes.

---

## Exercises

1. **Fix the DART pipeline.** Open [projects/consulting-emulation/](projects/consulting-emulation/) and find where financial statement data is loaded. Add a `clean()` function using the patterns above. At minimum: handle `"-"` sentinels, coerce revenue/profit to numeric, and assert no NaN before ratio computation.

2. **Add outlier flagging to FinAgent.** The Samsung stock data from yfinance sometimes has extreme volume spikes. In [projects/](projects/) find where yfinance data is fetched and add `flag_outliers(df, col="Volume")` to flag anomalous days without dropping them.

3. **Write a parametric cleaner.** Refactor `handle_missing()` so it accepts a dict: `{col: fill_strategy}` where `fill_strategy` can be `"drop"`, `"zero"`, `"median"`, or `"mean"`. This makes the cleaner reusable across all your projects without hardcoding column names.

---

## Go Deeper

Pandera — declarative schema validation for pandas DataFrames (stricter than assert statements, generates error reports):
https://pandera.readthedocs.io/en/stable/

---

## Did it click? (fill in after doing the exercises)
- [ ] Yes — move to next topic
- [ ] Partially — needs revisit
- [ ] No — add to curriculum.md "Needs Revisit"
