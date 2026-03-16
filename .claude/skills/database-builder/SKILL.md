# Skill: Database Builder

Scaffold databases for projects — in Notion (via MCP), Supabase, SQLite, or as local structured files.

Updated 2026-03-11: Added Supabase support, SQL schema generation, and SQLite patterns from Keonhee's stack.

## Trigger phrases
- "create a database for X"
- "set up a project tracker for X"
- "build a Notion database for X"
- "scaffold a data structure for X"
- "design a schema for X"

---

## How to use

Describe what you need to track:
- "Create a Notion database to track my job applications"
- "Build a SQLite schema for storing DART financial data"
- "Set up a Supabase table for conversation history"
- "Scaffold a local JSON structure for storing research reports"

---

## What Claude does

1. **Clarify if needed** — What are you tracking? What queries will you run? Read vs. write heavy?
2. **Design the schema** — fields, types, relationships, indexes
3. **Create it** — via Notion MCP, generate SQL DDL, or output local file structure
4. **Add usage note** — how to insert, query, and maintain

---

## Supported backends

### Notion (via MCP)
- Best for: project tracking, decision logs, application tracking, content management
- Use when: you need a human-readable UI + Claude integration
- MCP tool: `notion-create-database`

### Supabase (Postgres)
- Best for: production data, conversation history, user data
- Connection: `SUPABASE_URL` + `SUPABASE_API_KEY` from `.env`
- Current tables: conversation_history (RAG demo)
- Use when: data needs to persist across sessions and be queried at scale

### SQLite (local)
- Best for: project data stores, offline analysis, FinAgent-style financial data
- Pattern from FinAgent: `sqlite3` + `pandas.read_sql_query()`
- Use when: data is local, small-medium scale, no web access needed

### Local file (JSON/CSV/Markdown)
- Best for: lightweight trackers, config files, one-time analysis
- Use when: structure is simple and persistence via git is fine

---

## Output format

**Schema:**
| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| ... | ... | ... | ... |

**DDL (for SQL backends):**
```sql
CREATE TABLE ... (
  ...
);
CREATE INDEX ...;
```

**Usage:**
- Insert: `INSERT INTO ...`
- Query: `SELECT ...`
- Update: `UPDATE ...`

---

## Keonhee's existing schemas (reference before creating new ones)

### FinAgent SQLite — financials table
```sql
-- Fields: company, year, revenue, operating_profit, net_income, total_assets, total_liabilities, equity
-- Companies: Samsung Electronics, SK Hynix, LG Electronics
-- Years: 2020-2024
```

### Supabase — conversation_history (RAG demo)
```sql
-- Fields: id, session_id, role, content, timestamp
-- Used for: multi-turn conversation memory in RAG demo
```

---

## Notes
- For Notion: requires Notion MCP to be active in Claude Code
- For Supabase: use anon key for reads, service key for writes — check `.env`
- Say "make it simple" for minimal version, "make it comprehensive" for full production structure
- Always add an index on fields you'll query frequently (company, date, session_id, etc.)
