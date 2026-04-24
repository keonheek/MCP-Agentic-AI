# SQL — Aggregations: GROUP BY, HAVING, COUNT, SUM, AVG
_Track 2 | Week 1 | Date: 2026-03-24_

---

## Concept (10 min read)

You already know how to filter rows with WHERE and sort them with ORDER BY. Aggregations let you **collapse many rows into summary numbers** — totals, averages, counts — grouped by a category.

**Mental model: it is pandas groupby in SQL.**

In pandas you write:
```python
df.groupby("industry")["revenue"].sum()
```

In SQL you write:
```sql
SELECT industry, SUM(revenue)
FROM companies
GROUP BY industry;
```

Same idea. Group rows by a column, apply a math function to each group, get one output row per group.

**The execution order matters.** SQL runs clauses in this order:

```
FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY
```

The key insight: WHERE filters rows **before** grouping. HAVING filters groups **after** grouping. This is why you cannot write `WHERE SUM(revenue) > 1000` — SUM does not exist yet at the WHERE stage. You use HAVING for that.

---

## Key Terms

- **GROUP BY**: Collapses all rows with the same value in a column into a single group. One output row per group.
- **COUNT(*)**: Counts rows in each group. `COUNT(column)` counts non-NULL values only.
- **SUM(column)**: Adds up all values in the column for each group.
- **AVG(column)**: Calculates the arithmetic mean for each group.
- **HAVING**: Filters groups after aggregation — the WHERE clause for aggregate results.
- **Aggregate function**: Any function that takes multiple rows and returns one value (COUNT, SUM, AVG, MIN, MAX).
- **NULL in aggregates**: SUM, AVG, COUNT(col) all skip NULLs. COUNT(*) counts NULLs.

---

## Working Code

All examples run on SQLite — the same engine FinAgent uses. Paste these into a Python script or SQLite shell with no setup.

**Setup: create the tables**
```sql
CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
    name TEXT,
    industry TEXT,
    revenue INTEGER,
    employees INTEGER,
    founded_year INTEGER
);

INSERT INTO companies VALUES
(1, 'Samsung Electronics', 'Technology', 302000, 270000, 1969),
(2, 'SK Hynix', 'Technology', 44000, 30000, 1983),
(3, 'LG Electronics', 'Technology', 62000, 74000, 1958),
(4, 'Hyundai Motor', 'Automotive', 142000, 120000, 1967),
(5, 'Kia', 'Automotive', 89000, 52000, 1944),
(6, 'POSCO', 'Steel', 77000, 18000, 1968),
(7, 'Lotte', 'Retail', 22000, 90000, 1967),
(8, 'Shinsegae', 'Retail', 19000, 24000, 1930),
(9, 'Kakao', 'Technology', 8500, 12000, 2010),
(10, 'Naver', 'Technology', 9800, 14000, 1999);
```

---

**Query 1 — COUNT rows per group**
```sql
SELECT industry, COUNT(*) AS company_count
FROM companies
GROUP BY industry;
```
Result: one row per industry showing how many companies are in it.

---

**Query 2 — SUM revenue by industry**
```sql
SELECT industry, SUM(revenue) AS total_revenue
FROM companies
GROUP BY industry;
```

---

**Query 3 — AVG employees by industry**
```sql
SELECT industry, AVG(employees) AS avg_headcount
FROM companies
GROUP BY industry;
```

---

**Query 4 — Multiple aggregates in one query**
```sql
SELECT
    industry,
    COUNT(*) AS companies,
    SUM(revenue) AS total_revenue,
    AVG(revenue) AS avg_revenue,
    MAX(revenue) AS largest_company
FROM companies
GROUP BY industry
ORDER BY total_revenue DESC;
```

---

**Query 5 — HAVING: only industries with total revenue above 100,000**
```sql
SELECT industry, SUM(revenue) AS total_revenue
FROM companies
GROUP BY industry
HAVING SUM(revenue) > 100000;
```
Note: you cannot write `WHERE SUM(revenue) > 100000` — that would fail. HAVING is required here.

---

**Query 6 — WHERE + GROUP BY together**

Filter first (WHERE excludes Retail), then group:
```sql
SELECT industry, AVG(revenue) AS avg_revenue
FROM companies
WHERE industry != 'Retail'
GROUP BY industry
ORDER BY avg_revenue DESC;
```

---

**Query 7 — COUNT with a condition: companies founded after 1990**
```sql
SELECT industry, COUNT(*) AS post_1990_companies
FROM companies
WHERE founded_year > 1990
GROUP BY industry;
```

---

**Query 8 — HAVING with COUNT: industries with 3 or more companies**
```sql
SELECT industry, COUNT(*) AS company_count
FROM companies
GROUP BY industry
HAVING COUNT(*) >= 3;
```

---

**Query 9 — Revenue per employee (efficiency metric)**
```sql
SELECT
    name,
    industry,
    revenue / employees AS revenue_per_employee
FROM companies
ORDER BY revenue_per_employee DESC;
```
This is not an aggregation, but it shows a derived metric — useful for consulting scorecards.

---

**Query 10 — GROUP BY with a CASE expression (segment bucketing)**
```sql
SELECT
    CASE
        WHEN revenue >= 100000 THEN 'Large'
        WHEN revenue >= 30000 THEN 'Mid'
        ELSE 'Small'
    END AS size_bucket,
    COUNT(*) AS count,
    AVG(revenue) AS avg_revenue
FROM companies
GROUP BY size_bucket
ORDER BY avg_revenue DESC;
```
This is a pattern FinAgent's Text2SQL regularly needs — grouping by a computed category, not a raw column.

---

## Exercises

**1. Beginner — Simple GROUP BY**

Write a query that returns the total number of employees per industry, ordered by total employees descending.

Expected columns: `industry`, `total_employees`

<details>
<summary>Answer</summary>

```sql
SELECT industry, SUM(employees) AS total_employees
FROM companies
GROUP BY industry
ORDER BY total_employees DESC;
```
</details>

---

**2. Intermediate — HAVING clause**

Write a query that returns industries where the average company revenue is above 50,000. Show the industry name, number of companies, and average revenue.

Expected columns: `industry`, `company_count`, `avg_revenue`

<details>
<summary>Answer</summary>

```sql
SELECT
    industry,
    COUNT(*) AS company_count,
    AVG(revenue) AS avg_revenue
FROM companies
GROUP BY industry
HAVING AVG(revenue) > 50000
ORDER BY avg_revenue DESC;
```
</details>

---

**3. Challenge — Multi-condition aggregation**

Write a query that finds industries where:
- At least 2 companies were founded before 1970
- The total revenue of those pre-1970 companies is above 100,000

Return: `industry`, `old_company_count`, `pre_1970_revenue`

Hint: filter in WHERE first, then use HAVING on the aggregate.

<details>
<summary>Answer</summary>

```sql
SELECT
    industry,
    COUNT(*) AS old_company_count,
    SUM(revenue) AS pre_1970_revenue
FROM companies
WHERE founded_year < 1970
GROUP BY industry
HAVING COUNT(*) >= 2 AND SUM(revenue) > 100000
ORDER BY pre_1970_revenue DESC;
```
</details>

---

## Resources

- **Primary:** SQLBolt Lesson 10 — https://sqlbolt.com/lesson/select_queries_with_aggregates
- **Practice:** LeetCode SQL 50 — https://leetcode.com/studyplan/top-sql-50/ (problems 1-10 cover GROUP BY + HAVING)

---

## Cross-apply

**FinAgent Text2SQL** — When GPT-4o generates SQL from a natural language query like "which sector has the highest average revenue?", it writes exactly the GROUP BY + AVG pattern from Query 2. Knowing this lets you verify the generated SQL is correct, catch bad HAVING/WHERE ordering, and debug when the LLM produces a malformed query.

**Consulting Emulation (M&A Due Diligence)** — The dashboard aggregates Samsung's financials by year (`GROUP BY fiscal_year`) and computes margin trends (`AVG(operating_income / revenue)`). Query 4's multi-aggregate pattern is directly what that pipeline runs against the DART SQLite database.

**SME Diagnostic AI** — If you extend it to compare a client against benchmark peers, the benchmark lookup is a `GROUP BY industry HAVING COUNT(*) >= 5` query to ensure the comparison set is large enough to be meaningful.
