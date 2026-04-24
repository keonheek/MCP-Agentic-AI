---
name: notion
description: Conventions and patterns for all Notion workspace operations. Use whenever creating pages, updating databases, searching notes, or logging to Notion. The Notion MCP tools are available directly in the main session — no agent spawn needed. Trigger phrases: "add this to Notion", "create a Notion page for X", "search Notion for X", "log this in Notion".
---

# Skill: Notion

Notion is connected via MCP (`claude_ai_Notion`). Use the MCP tools directly — no agent spawn needed.

## Operating rules

1. **Search first** — before creating anything, search Notion to avoid duplicates
2. **Right tool** — don't fetch what you can search, don't create what already exists
3. **Keep content structured** — headers, bullet points, clear labels
4. **Confirm the action** — return the page ID or URL of what was created/updated

## Toggle indentation

Every line inside a `{toggle="true"}` block must start with `\t` or content renders outside the toggle. No exceptions — bullets, checkboxes, paragraphs, numbered lists all need the tab.

## Section headers

Top-level numbered sections (e.g. `1. 요약`, `2. 배경`) use `#` (H1). Toggle subheadings inside use `###` (H3).

## Common operations

### Log a decision
- Search for existing "Decision Log" page or database
- Append: `[YYYY-MM-DD] DECISION: ... | REASONING: ... | CONTEXT: ...`

### Create a project tracking page
- Title: `[Project Name] — Status`
- Sections: Overview, Current Status, Next Steps, Blockers

### Store a research report
- Title: `Research: [Topic] — YYYY-MM-DD`
- Body: summary + key findings + sources

### Track a job application
- Fields: Company, Role, Date Applied, Status, Notes

## Available MCP tools

- `notion-search` — search before any create
- `notion-fetch` — fetch a known page by ID
- `notion-create-pages` — create new page
- `notion-update-page` — update existing page
- `notion-create-database` — create a new database
- `notion-duplicate-page` — duplicate
- `notion-move-pages` — move pages
- `notion-get-users` — list workspace users