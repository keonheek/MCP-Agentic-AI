# Notion MCP — Capabilities Reference

_Last updated: 2026-03-07_

---

## Known Database IDs

| Database | Notion URL | Data Source ID (collection://) |
|---|---|---|
| Projects | https://www.notion.so/2ee4292aa5f981c1b15df4e2eebc35b0 | collection://2ee4292a-a5f9-81f1-b2d0-000b1e3f9825 |
| Skills & Capabilities | https://www.notion.so/bd32376e5f084a9abd234823f7f11753 | collection://38f7ef64-b0cb-47d6-a0de-f1e5f2dab309 |

### Key Pages

| Page | URL / ID |
|---|---|
| Second Brain (workspace root) | https://www.notion.so/2ee4292aa5f980f195c2d7e30a0f312e |
| Home | https://www.notion.so/2ee4292aa5f981b2b693c1d92cde0382 |
| Resources | https://www.notion.so/2ee4292aa5f981eca00df82b47d078d6 |

---

## Available MCP Tools

### notion-search
Semantic search across the workspace and connected sources (Slack, Google Drive, GitHub, etc.).

```
# Search workspace for a topic
query: "LangChain agent patterns"
query_type: "internal"

# Search within a specific database
query: "FinAgent"
data_source_url: "collection://2ee4292a-a5f9-81f1-b2d0-000b1e3f9825"

# Find a user
query: "keonhee"
query_type: "user"
```

---

### notion-fetch
Get full page or database content by URL or ID.

```
# Fetch a page by URL
id: "https://www.notion.so/2ee4292aa5f980f195c2d7e30a0f312e"

# Fetch a page by raw ID
id: "2ee4292a-a5f9-80f1-95c2-d7e30a0f312e"

# Fetch a data source (get schema + contents)
id: "collection://38f7ef64-b0cb-47d6-a0de-f1e5f2dab309"

# Fetch with discussion comments
id: "page-id"
include_discussions: true
```

Returns Notion-flavored Markdown. Always fetch a database before creating pages into it — you need the data source ID and schema.

---

### notion-create-pages
Create one or more pages — either standalone or inside a database.

```
# Create a standalone page
parent: (omit)
pages: [{ properties: { title: "My Page" }, content: "# Section\nContent here" }]

# Create a page inside a database (use data_source_id from fetch results)
parent: { data_source_id: "38f7ef64-b0cb-47d6-a0de-f1e5f2dab309" }
pages: [{ properties: { Name: "web-search", Category: "Skill", Status: "Active" } }]

# Create a page under a parent page
parent: { page_id: "2ee4292a-a5f9-81ec-a00d-f82b47d078d6" }
pages: [{ properties: { title: "Sub-page" }, content: "Content" }]
```

Rules:
- Always include a title/Name property
- Date properties split into `date:{prop}:start`, `date:{prop}:end`, `date:{prop}:is_datetime`
- Checkboxes use `__YES__` / `__NO__`
- Properties named `id` or `url` must be prefixed with `userDefined:`
- Up to 100 pages per call

---

### notion-update-page
Update properties or content on an existing page.

```
# Update a project status
page_id: "page-uuid"
properties: { Status: "Done" }

# Update content
page_id: "page-uuid"
content: "Updated content in Notion markdown"
```

---

### notion-create-database
Create a new database with a custom schema using SQL DDL syntax.

```
# Minimal
schema: "CREATE TABLE (\"Name\" TITLE)"

# Full example
title: "My Database"
parent: { page_id: "parent-page-id" }
schema: """
  CREATE TABLE (
    "Name" TITLE,
    "Status" SELECT('Active':green, 'Pending':yellow, 'Planned':gray),
    "Tags" MULTI_SELECT('ai':blue, 'work':orange),
    "Notes" RICH_TEXT,
    "Due" DATE
  )
"""
```

Type reference: `TITLE`, `RICH_TEXT`, `DATE`, `CHECKBOX`, `URL`, `EMAIL`, `NUMBER`, `STATUS`, `FILES`, `SELECT(...)`, `MULTI_SELECT(...)`, `PEOPLE`, `RELATION(...)`, `ROLLUP(...)`, `FORMULA(...)`, `UNIQUE_ID`, `CREATED_TIME`, `LAST_EDITED_TIME`

---

### notion-duplicate-page
Duplicate any existing page.

```
page_id: "page-uuid-to-duplicate"
parent: { page_id: "destination-parent-id" }  # optional
```

---

### notion-move-pages
Move pages to a different parent.

```
page_ids: ["page-uuid-1", "page-uuid-2"]
parent: { page_id: "new-parent-page-id" }
```

---

### notion-get-comments
Get discussion comments on a page.

```
page_id: "page-uuid"
```

---

### notion-create-comment
Add a comment to a page.

```
page_id: "page-uuid"
content: "Comment text here"
```

---

### notion-get-users
List all users in the workspace. Use to find user IDs for filtering or assigning.

```
# No required params — returns all workspace users
```

---

### notion-get-teams
List all teams in the workspace.

```
# No required params — returns all workspace teams
```

---

### notion-update-data-source
Update a database's data source schema (add/remove columns, change options).

```
data_source_id: "38f7ef64-b0cb-47d6-a0de-f1e5f2dab309"
schema: "ALTER TABLE ... ADD COLUMN ..."
```

---

## How to Trigger the notion-agent

The `notion-agent` (Haiku) handles Notion tasks when invoked from the main session.

**Trigger phrases:**
- "add to Notion"
- "create a Notion page for X"
- "log this in Notion"
- "update the Projects database"
- "save this to the Skills & Capabilities database"

**When to use the agent vs. direct MCP tools:**
- Use direct MCP tools (above) for precise, structured operations in the current session
- Delegate to notion-agent when the task is routine (logging, page creation) and you want to save context window / cost

**Example delegation:**
```
"notion-agent: create a page in the Projects database with Name='LangChain POC', Status='Planned', Start Date=2026-03-10"
```

---

## Workflow Patterns

### Add a project to the Projects database
1. Fetch the database to get the schema: `notion-fetch collection://2ee4292a-a5f9-81f1-b2d0-000b1e3f9825`
2. Create the page: `notion-create-pages` with `data_source_id: "2ee4292a-a5f9-81f1-b2d0-000b1e3f9825"`

### Add a new skill/agent/MCP entry
1. Use `notion-create-pages` directly with `data_source_id: "38f7ef64-b0cb-47d6-a0de-f1e5f2dab309"`
2. Set Name, Category, Trigger, Status, Notes

### Search then update a page
1. `notion-search` to find the page and get its URL
2. `notion-fetch` the page to confirm properties
3. `notion-update-page` with the page ID and new properties

### Find who created a page
1. `notion-search` with `filters.created_by_user_ids` after getting user IDs from `notion-get-users`
