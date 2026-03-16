# SQL Practice — Consulting Interview Prep

_Priority: McKinsey QuantumBlack (requires SQL) + BCG Gamma (quantitative analysis)_
_Target completion: before submitting McKinsey/BCG applications_

---

## Why This Matters

McKinsey QuantumBlack job descriptions explicitly require:
- SQL (required, core skill)
- Data manipulation and query optimization
- Analytical thinking on messy data

BCG Gamma: quantitative problem-solving with data. SQL questions appear in technical screens.

---

## Skill Gaps to Close

| Skill | Status | Source |
|-------|--------|--------|
| Basic SELECT, JOIN, WHERE, GROUP BY | ✅ Built (FinAgent Text2SQL) | — |
| Subqueries, CTEs | Partial — used in FinAgent | Practice needed |
| Window functions: LAG, LEAD, RANK, PARTITION BY | Gap | Mode Analytics advanced SQL |
| Query optimization: indexes, explain plans | Gap | Not yet encountered |
| Handling NULLs, COALESCE, CASE WHEN | Partial | Practice needed |

---

## Window Functions — Quick Reference

Window functions compute over a "window" of rows related to the current row, without collapsing them (unlike GROUP BY).

```sql
-- Syntax
function_name(...) OVER (
    [PARTITION BY column]
    [ORDER BY column]
    [ROWS/RANGE frame]
)
```

### ROW_NUMBER / RANK / DENSE_RANK

```sql
-- Rank companies by revenue within each sector
SELECT
    company_name,
    sector,
    revenue,
    RANK() OVER (PARTITION BY sector ORDER BY revenue DESC) AS revenue_rank,
    ROW_NUMBER() OVER (PARTITION BY sector ORDER BY revenue DESC) AS row_num,
    DENSE_RANK() OVER (PARTITION BY sector ORDER BY revenue DESC) AS dense_rank
FROM financials;

-- Difference:
-- RANK: gaps after ties (1,1,3)
-- DENSE_RANK: no gaps (1,1,2)
-- ROW_NUMBER: always unique (1,2,3)
```

### LAG / LEAD — Year-over-Year Analysis

```sql
-- Quarter-over-quarter revenue change (consulting case staple)
SELECT
    company_name,
    quarter,
    revenue,
    LAG(revenue, 1) OVER (PARTITION BY company_name ORDER BY quarter) AS prev_quarter_revenue,
    revenue - LAG(revenue, 1) OVER (PARTITION BY company_name ORDER BY quarter) AS qoq_change,
    ROUND(
        100.0 * (revenue - LAG(revenue, 1) OVER (PARTITION BY company_name ORDER BY quarter))
        / LAG(revenue, 1) OVER (PARTITION BY company_name ORDER BY quarter),
        2
    ) AS qoq_pct_change
FROM financials
ORDER BY company_name, quarter;
```

### Running Totals / Moving Averages

```sql
-- Cumulative revenue by year
SELECT
    company_name,
    year,
    revenue,
    SUM(revenue) OVER (PARTITION BY company_name ORDER BY year) AS cumulative_revenue,
    AVG(revenue) OVER (
        PARTITION BY company_name
        ORDER BY year
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS rolling_3yr_avg
FROM financials;
```

### NTILE — Quartile / Percentile Bucketing

```sql
-- Bucket companies into performance quartiles
SELECT
    company_name,
    revenue,
    NTILE(4) OVER (ORDER BY revenue DESC) AS quartile,
    NTILE(10) OVER (ORDER BY revenue DESC) AS decile
FROM financials;
```

### FIRST_VALUE / LAST_VALUE

```sql
-- Compare each quarter to the first quarter (baseline comparison)
SELECT
    company_name,
    quarter,
    revenue,
    FIRST_VALUE(revenue) OVER (
        PARTITION BY company_name
        ORDER BY quarter
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS baseline_revenue,
    revenue / FIRST_VALUE(revenue) OVER (
        PARTITION BY company_name
        ORDER BY quarter
    ) AS growth_vs_baseline
FROM financials;
```

---

## CTEs — Clean Query Structure

CTEs (WITH clauses) make complex queries readable — important for consulting technical screens where clarity matters as much as correctness.

```sql
-- Multi-step analysis: identify top companies, then their year-over-year trend
WITH top_companies AS (
    SELECT company_name
    FROM financials
    GROUP BY company_name
    HAVING AVG(revenue) > 1000000
),
yoy_trend AS (
    SELECT
        f.company_name,
        f.year,
        f.revenue,
        LAG(f.revenue) OVER (PARTITION BY f.company_name ORDER BY f.year) AS prev_year
    FROM financials f
    JOIN top_companies t ON f.company_name = t.company_name
)
SELECT
    company_name,
    year,
    revenue,
    prev_year,
    ROUND(100.0 * (revenue - prev_year) / prev_year, 2) AS yoy_growth
FROM yoy_trend
WHERE prev_year IS NOT NULL
ORDER BY yoy_growth DESC;
```

---

## Practice Exercises — Consulting Context

These mirror the types of analysis McKinsey QuantumBlack does for clients.

### Exercise 1: Profitability Decline Diagnosis

_Context: Client's net margin dropped from 15% to 8% over 3 years. Identify which business unit is responsible._

```sql
-- Step 1: Calculate margin per business unit per year
SELECT
    business_unit,
    year,
    revenue,
    operating_cost,
    revenue - operating_cost AS gross_profit,
    ROUND(100.0 * (revenue - operating_cost) / revenue, 2) AS margin_pct
FROM business_financials
ORDER BY business_unit, year;

-- Step 2: Rank units by margin deterioration
WITH margin_calc AS (
    SELECT
        business_unit,
        year,
        ROUND(100.0 * (revenue - operating_cost) / revenue, 2) AS margin_pct
    FROM business_financials
),
margin_change AS (
    SELECT
        business_unit,
        year,
        margin_pct,
        LAG(margin_pct) OVER (PARTITION BY business_unit ORDER BY year) AS prev_margin,
        margin_pct - LAG(margin_pct) OVER (PARTITION BY business_unit ORDER BY year) AS delta
    FROM margin_calc
)
SELECT business_unit, year, margin_pct, prev_margin, delta
FROM margin_change
WHERE delta IS NOT NULL
ORDER BY delta ASC;  -- Worst decline first
```

### Exercise 2: Customer Cohort Retention

_Context: SaaS client wants to understand if customers acquired recently churn faster._

```sql
-- Cohort analysis: retention rate by acquisition month
WITH cohorts AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', first_purchase_date) AS cohort_month
    FROM customers
),
activity AS (
    SELECT
        c.customer_id,
        c.cohort_month,
        DATE_TRUNC('month', t.transaction_date) AS activity_month
    FROM cohorts c
    JOIN transactions t ON c.customer_id = t.customer_id
),
cohort_size AS (
    SELECT cohort_month, COUNT(DISTINCT customer_id) AS cohort_count
    FROM cohorts
    GROUP BY cohort_month
),
retention AS (
    SELECT
        a.cohort_month,
        EXTRACT(MONTH FROM AGE(a.activity_month, a.cohort_month)) AS months_since_acquisition,
        COUNT(DISTINCT a.customer_id) AS active_customers
    FROM activity a
    GROUP BY a.cohort_month, months_since_acquisition
)
SELECT
    r.cohort_month,
    r.months_since_acquisition,
    r.active_customers,
    cs.cohort_count,
    ROUND(100.0 * r.active_customers / cs.cohort_count, 1) AS retention_rate
FROM retention r
JOIN cohort_size cs ON r.cohort_month = cs.cohort_month
ORDER BY r.cohort_month, r.months_since_acquisition;
```

### Exercise 3: Market Share Shift

_Context: Determine which competitor gained share during our client's revenue decline._

```sql
-- Market share by company by quarter
WITH market_totals AS (
    SELECT
        quarter,
        SUM(revenue) AS total_market_revenue
    FROM market_data
    GROUP BY quarter
),
share_calc AS (
    SELECT
        m.company,
        m.quarter,
        m.revenue,
        t.total_market_revenue,
        ROUND(100.0 * m.revenue / t.total_market_revenue, 2) AS market_share_pct,
        LAG(ROUND(100.0 * m.revenue / t.total_market_revenue, 2))
            OVER (PARTITION BY m.company ORDER BY m.quarter) AS prev_share
    FROM market_data m
    JOIN market_totals t ON m.quarter = t.quarter
)
SELECT
    company,
    quarter,
    revenue,
    market_share_pct,
    prev_share,
    ROUND(market_share_pct - prev_share, 2) AS share_change
FROM share_calc
WHERE prev_share IS NOT NULL
ORDER BY quarter, share_change ASC;
```

---

## NULL Handling — Common Patterns

```sql
-- COALESCE: first non-null value
SELECT COALESCE(revenue_2025, revenue_2024, 0) AS best_revenue_estimate FROM financials;

-- NULLIF: prevent division by zero
SELECT revenue / NULLIF(cost, 0) AS ratio FROM financials;

-- IS NULL / IS NOT NULL in window functions
SELECT
    company,
    year,
    revenue,
    COALESCE(LAG(revenue) OVER (ORDER BY year), revenue) AS prev_or_self
FROM financials;
```

---

## CASE WHEN — Conditional Logic

```sql
-- Segment companies by performance tier
SELECT
    company_name,
    revenue,
    CASE
        WHEN revenue > 10000000 THEN 'Large Cap'
        WHEN revenue > 1000000 THEN 'Mid Cap'
        WHEN revenue > 100000 THEN 'Small Cap'
        ELSE 'Micro Cap'
    END AS tier,
    CASE
        WHEN yoy_growth > 0.20 THEN 'High Growth'
        WHEN yoy_growth > 0.05 THEN 'Moderate Growth'
        WHEN yoy_growth >= 0 THEN 'Stagnant'
        ELSE 'Declining'
    END AS growth_category
FROM company_metrics;
```

---

## Quick Study Path

1. **Mode Analytics SQL Tutorial** — Free. Do the advanced section: window functions, CTEs, subqueries. (~6 hours)
   - mode.com/sql-tutorial
2. **StrataScratch** — Real SQL questions from McKinsey, BCG, Deloitte (free tier has many). Practice company-tagged problems.
   - platform.stratascratch.com
3. **LeetCode SQL** — Medium difficulty problems: 197, 181, 184, 177 (window functions). (~2 hours)
4. **Apply to FinAgent** — Add window functions to FinAgent's Text2SQL output validation. Practical, builds portfolio simultaneously.

---

## Interview Tips

- **Talk through your approach first** — consulting firms assess structured thinking, not just whether you get the right answer
- **Name the framework** — "I'd use a window function here to avoid aggregation loss"
- **Check for NULLs** — always mention NULL handling; it signals production awareness
- **PARTITION BY vs GROUP BY** — know the difference cold:
  - `GROUP BY` collapses rows
  - `PARTITION BY` in window function keeps all rows, computes over partition
