# SQL Window Functions — Practice Sheet

_Generated 2026-03-24 for Keonhee's stack: FinAgent Text2SQL, DART financial data, SQLite_

---

## What window functions do

Unlike GROUP BY (which collapses rows), window functions compute a value **across a set of rows related to the current row** — without collapsing. Every row is preserved.

```sql
FUNCTION() OVER (
  PARTITION BY <group>   -- like GROUP BY but keeps rows
  ORDER BY <col>         -- defines order within partition
  ROWS/RANGE BETWEEN ... -- optional frame
)
```

---

## 1. Ranking functions

```sql
-- Rank companies by revenue within each industry
SELECT
  corp_name,
  industry,
  revenue,
  ROW_NUMBER() OVER (PARTITION BY industry ORDER BY revenue DESC) AS row_num,
  RANK()       OVER (PARTITION BY industry ORDER BY revenue DESC) AS rank,
  DENSE_RANK() OVER (PARTITION BY industry ORDER BY revenue DESC) AS dense_rank
FROM financials;
```

| Difference | ROW_NUMBER | RANK | DENSE_RANK |
|---|---|---|---|
| Ties | No ties (always unique) | Skips numbers (1,1,3) | No skip (1,1,2) |

**FinAgent use case**: rank Samsung subsidiaries by operating profit within each business segment.

---

## 2. Offset functions

```sql
-- YoY revenue growth per company
SELECT
  corp_name,
  year,
  revenue,
  LAG(revenue, 1)  OVER (PARTITION BY corp_name ORDER BY year) AS prev_year,
  LEAD(revenue, 1) OVER (PARTITION BY corp_name ORDER BY year) AS next_year,
  revenue - LAG(revenue, 1) OVER (PARTITION BY corp_name ORDER BY year) AS yoy_change
FROM financials;
```

**DART use case**: compare FY2024 vs FY2023 net income for each corp in the screener.

---

## 3. Aggregate window functions

```sql
-- Running total revenue + % of total within year
SELECT
  corp_name,
  year,
  revenue,
  SUM(revenue) OVER (PARTITION BY year ORDER BY revenue DESC
                     ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total,
  SUM(revenue) OVER (PARTITION BY year) AS year_total,
  ROUND(revenue * 100.0 / SUM(revenue) OVER (PARTITION BY year), 2) AS pct_of_year
FROM financials;
```

---

## 4. NTILE — bucketing

```sql
-- Split companies into quartiles by AI readiness score
SELECT
  corp_name,
  ai_score,
  NTILE(4) OVER (ORDER BY ai_score DESC) AS quartile
FROM lead_intelligence;
-- quartile 1 = top 25%, quartile 4 = bottom 25%
```

**Lead Intelligence use case**: segment the 20 screened companies into quartiles for prioritized outreach.

---

## 5. FIRST_VALUE / LAST_VALUE

```sql
-- Best and worst revenue year per company
SELECT
  corp_name,
  year,
  revenue,
  FIRST_VALUE(revenue) OVER (PARTITION BY corp_name ORDER BY revenue DESC) AS best_year_rev,
  LAST_VALUE(revenue)  OVER (PARTITION BY corp_name ORDER BY revenue DESC
                              ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS worst_year_rev
FROM financials;
-- Note: LAST_VALUE needs explicit frame or it defaults to current row only
```

---

## 6. Frame clauses (common gotcha)

```sql
-- Default frame when ORDER BY is present:
RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW  -- includes all tied rows up to current

-- Explicit rolling 3-quarter average:
AVG(revenue) OVER (
  PARTITION BY corp_name
  ORDER BY quarter
  ROWS BETWEEN 2 PRECEDING AND CURRENT ROW  -- exactly 3 rows
)
```

**Rule**: always use `ROWS BETWEEN` for financial time series — `RANGE BETWEEN` can include unexpected tied rows.

---

## SQLite compatibility note

SQLite supports window functions since v3.25.0 (2018). All functions above work in FinAgent's SQLite backend **except**:

- `PERCENTILE_CONT` / `PERCENTILE_DISC` — not supported in SQLite (use NTILE as workaround)
- `CUME_DIST` / `PERCENT_RANK` — supported in SQLite 3.25+

---

## Quick reference for Text2SQL prompting

When writing natural language → SQL for FinAgent, these phrasings reliably trigger window functions:

| Natural language | Window function |
|---|---|
| "rank by X within Y" | RANK() / DENSE_RANK() OVER (PARTITION BY Y ORDER BY X) |
| "running total of X" | SUM(X) OVER (ORDER BY date ROWS UNBOUNDED PRECEDING) |
| "compared to previous year" | LAG(X, 1) OVER (PARTITION BY corp ORDER BY year) |
| "top N per group" | ROW_NUMBER() OVER (...) with WHERE row_num <= N |
| "% of total" | X / SUM(X) OVER (PARTITION BY group) |
| "moving average" | AVG(X) OVER (ROWS BETWEEN N PRECEDING AND CURRENT ROW) |
