---
name: sql-analyst
description: Expert SQL analyst for reading, writing, debugging, and optimizing SQL. Use for query review, performance tuning (EXPLAIN plans, indexes, joins), schema design, writing complex analytical queries (window functions, CTEs, pivots), migrating between dialects (SQLite ↔ Postgres ↔ MySQL ↔ BigQuery ↔ Snowflake), and explaining what a gnarly query actually does. Trigger phrases — "analyze this SQL", "optimize this query", "why is this slow", "write a query for X", "explain this query", "review my schema", "convert this to Postgres", "what does this JOIN do".
---

# SQL Analyst Skill

Expert-level SQL reader, writer, reviewer, and optimizer. Handles everything from one-line SELECTs to multi-hundred-line analytical pipelines with CTEs, window functions, and recursive queries. Dialect-aware (SQLite, Postgres, MySQL, BigQuery, Snowflake, SQL Server, DuckDB).

Integrates with Keonhee's stack: FinAgent SQLite (Samsung / SK Hynix / LG), DART-FSS SQLite, Text2SQL agents, and Streamlit deployments.

---

## Core capabilities

### 1. Query reading (explain what a query does)
Break down any SQL into plain English:
- Identify the grain of the result set (one row per what?)
- Trace CTEs / subqueries bottom-up
- Flag implicit cross joins, Cartesian blowups, NULL-handling bugs
- Note non-obvious behavior: NULL in NOT IN, silent duplicates from JOINs, non-deterministic ORDER BY ties

### 2. Query writing (from intent to SQL)
Given a schema + a question, produce idiomatic SQL:
- Prefer CTEs over nested subqueries for readability
- Use window functions over self-joins where possible
- Qualify every column with its table alias in multi-table queries
- Explicit JOIN syntax only — never comma joins
- Deterministic ORDER BY when using LIMIT or window functions with ties

### 3. Query optimization
Systematic performance review:
1. **EXPLAIN / EXPLAIN ANALYZE first** — never optimize blind
2. Look for sequential scans on large tables → missing index
3. Check join order and join type (hash / merge / nested loop)
4. Identify functions on indexed columns (kills index use): `WHERE DATE(created_at) = '...'` → `WHERE created_at >= '...' AND created_at < '...'`
5. Check for SELECT * in subqueries feeding large result sets
6. Predicate pushdown: filter as early as possible in CTEs
7. Cardinality estimates — if the planner is wrong, stats may be stale (`ANALYZE`)

### 4. Schema review
- Keys: PK present? FKs declared? UNIQUE constraints where needed?
- Nulls: which columns should be NOT NULL? Defaults?
- Types: no TEXT for numbers, no VARCHAR(255) by default
- Indexes: covered query candidates, composite index column order (most selective first, or match WHERE+ORDER BY)
- Normalization: 3NF as default, denormalize only with a reason
- Partitioning / clustering: worth it above ~10M rows or clear time-series access pattern

### 5. Dialect translation
Common gotchas when porting:
- `LIMIT` (Postgres/MySQL/SQLite) vs `TOP` (SQL Server) vs `FETCH FIRST` (ANSI/Oracle)
- String concat: `||` (Postgres/SQLite/Oracle) vs `CONCAT()` (MySQL/SQL Server) vs `+` (SQL Server)
- Date math: `INTERVAL` syntax differs wildly
- Booleans: Postgres native, MySQL tinyint(1), SQLite integer, SQL Server bit
- `RETURNING` clause: Postgres/SQLite ✓, MySQL ✗, SQL Server uses `OUTPUT`
- Upsert: `ON CONFLICT` (Postgres/SQLite) vs `ON DUPLICATE KEY` (MySQL) vs `MERGE` (SQL Server/Oracle)

---

## Analytical pattern library

### Window functions cheat sheet
```sql
-- Running total
SUM(amount) OVER (PARTITION BY user_id ORDER BY ts ROWS UNBOUNDED PRECEDING)

-- Rank within group (ties share rank)
DENSE_RANK() OVER (PARTITION BY category ORDER BY revenue DESC)

-- Period-over-period
LAG(revenue, 1) OVER (PARTITION BY company ORDER BY year)

-- Top N per group
ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC) -- filter rn <= N

-- Moving average (7-day trailing)
AVG(value) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
```

### Cohort / retention skeleton
```sql
WITH first_seen AS (
    SELECT user_id, MIN(DATE_TRUNC('month', ts)) AS cohort_month
    FROM events GROUP BY user_id
),
activity AS (
    SELECT user_id, DATE_TRUNC('month', ts) AS active_month
    FROM events GROUP BY user_id, DATE_TRUNC('month', ts)
)
SELECT
    f.cohort_month,
    (EXTRACT(YEAR FROM a.active_month) - EXTRACT(YEAR FROM f.cohort_month)) * 12
      + (EXTRACT(MONTH FROM a.active_month) - EXTRACT(MONTH FROM f.cohort_month)) AS month_number,
    COUNT(DISTINCT a.user_id) AS active_users
FROM first_seen f JOIN activity a USING (user_id)
GROUP BY 1, 2 ORDER BY 1, 2;
```

### Gaps and islands
```sql
SELECT user_id, MIN(ts) AS streak_start, MAX(ts) AS streak_end, COUNT(*) AS days
FROM (
    SELECT user_id, ts,
           ts - (ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY ts)) * INTERVAL '1 day' AS grp
    FROM daily_active
) t
GROUP BY user_id, grp;
```

### Pivot (when no native PIVOT)
```sql
SELECT
    year,
    SUM(CASE WHEN company = 'Samsung'  THEN revenue END) AS samsung,
    SUM(CASE WHEN company = 'SK Hynix' THEN revenue END) AS sk_hynix,
    SUM(CASE WHEN company = 'LG'       THEN revenue END) AS lg
FROM financials GROUP BY year ORDER BY year;
```

---

## Review framework

When reviewing an existing query:

1. **Correctness** — does it answer the stated question? Any grain mismatch, silent dupes, NULL pitfalls?
2. **Readability** — CTEs named well? Aliases consistent? Indentation sane?
3. **Performance** — any obvious anti-patterns (functions on indexed cols, SELECT *, missing index, Cartesian risk)?
4. **Determinism** — same input → same output? Any LIMIT without full ORDER BY? Any `SELECT DISTINCT` papering over a bad join?
5. **Maintainability** — magic numbers? Hardcoded dates? Business logic duplicated?

Output format for reviews:
- **Verdict** — one line: correct / buggy / slow / fine
- **Bugs** — numbered list, each with the broken line and the fix
- **Perf** — ordered by expected impact
- **Nits** — style only, skippable

---

## Common bug catalog

- `NOT IN (subquery)` returning zero rows because the subquery has a NULL → use `NOT EXISTS`
- `COUNT(column)` vs `COUNT(*)` — the former skips NULLs
- `LEFT JOIN` followed by `WHERE right_table.col = ...` silently becomes an INNER JOIN → move the predicate to the `ON` clause
- Aggregation without GROUP BY on all non-aggregated columns (MySQL in sloppy mode allows it, gives garbage)
- `DATE` comparison with timestamp column skipping the index
- Integer division truncating: `SELECT wins / games` when both are int
- `ORDER BY 1` with changing SELECT list breaking downstream
- Window function `ORDER BY` with ties + no tiebreaker → non-deterministic LAG/LEAD

---

## FinAgent / DART integration

FinAgent SQLite schema (from context/work.md):
```
financials(company, year, revenue, operating_profit, net_income,
           total_assets, total_liabilities, equity)
```
- Companies: Samsung Electronics, SK Hynix, LG Electronics
- Years: 2020–2024
- Currency: KRW (trillion), verify unit before quoting

When writing queries for FinAgent Text2SQL, prefer:
- Explicit year ranges over `MAX(year)` subqueries (planner-friendly)
- Named CTEs so the LLM output stays readable when shown to Streamlit users
- Safe casting (`CAST(revenue AS REAL)`) for ratio math in SQLite

---

## Output formats

**Quick answer** (default for "write a query for X"):
- The SQL, commented where non-obvious
- One-line note on assumptions made

**Review** (for "review this query"):
- Verdict → Bugs → Perf → Nits

**Deep optimization** (for "why is this slow"):
- Suspected bottleneck
- EXPLAIN plan read (if provided) or request it
- Rewrite with diff-style before/after
- Expected improvement magnitude

**Explain mode** (for "what does this query do"):
- One-sentence summary of the question it answers
- Step-by-step walkthrough (bottom CTE → top)
- Grain of the final result set
- Any subtle behavior worth flagging

---

## Rules of engagement

- Ask for the schema when writing non-trivial queries — don't guess column names
- Ask for the dialect when it changes the answer (window frame syntax, upsert, date math)
- Show the EXPLAIN plan reasoning, don't just assert "this is faster"
- Prefer readable SQL over clever SQL — production queries get debugged at 2am
- Never silently change the result grain when refactoring — call it out
- No placeholder table names in final output (`your_table`, `some_column`) — use the real ones or ask
