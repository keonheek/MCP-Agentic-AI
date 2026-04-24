---
name: obsidian
description: Read, search, create, and update notes in Keonhee's Obsidian vault. Also manages the LLM wiki system (ingest/query/lint). Trigger phrases: "add this to Obsidian", "find my note about X", "ingest [source]", "/wiki-ingest", "/wiki-query", "/wiki-lint".
---

# Obsidian Skill

Read, search, create, and update notes in Keonhee's Obsidian vault via the local MCP server.
Also manages the LLM wiki system — see Wiki Operations below.

## Setup (one-time)

1. Set vault path in `.mcp.json` → `OBSIDIAN_VAULT_PATH`
2. Install MCP package: `pip install mcp`
3. Restart Claude Code — tools appear automatically

## When to use this skill

| Trigger phrase | Action |
|---------------|--------|
| "add this to Obsidian" | `create_note` in appropriate folder |
| "find my note about X" | `search_notes` |
| "what did I write about X" | `search_notes` + `read_note` |
| "surface old ideas" | `get_recent_notes` with `min_days=14` |
| "open today's note" | `get_daily_note` |
| "tag X notes" / "notes tagged X" | `search_by_tag` |
| "show me my vault structure" | `get_vault_structure` |
| "ingest [source]" / `/wiki-ingest` | Wiki ingest workflow |
| "query the wiki" / `/wiki-query` | Wiki query workflow |
| "lint the wiki" / `/wiki-lint` | Wiki health check |

## Available Tools

### read_note(path)
Read a note by relative path from vault root.
```
read_note("wiki/concepts/autoresearch.md")
```

### create_note(path, content, tags?)
Create a new note. Adds frontmatter with tags + created date automatically.
```
create_note("wiki/concepts/new-concept.md", "# Title\n\nContent here.", tags=["concept"])
```

### update_note(path, content)
Overwrite a note completely.

### append_to_note(path, text)
Add text to the end of an existing note. Use for wiki/log.md entries.

### search_notes(query, limit=20)
Full-text search across all notes. Returns path, title, modified date, and context snippet.

### search_by_tag(tag)
Find all notes tagged with a given tag (checks frontmatter + inline #tags).

### list_notes(folder="", limit=50)
List notes in vault, optionally filtered by folder.

### get_recent_notes(days=7, min_days=0)
Get recently modified notes. Set `min_days=14` to find notes from 2+ weeks ago (for /emerge).

### get_vault_structure()
Show full folder/file tree of vault.

### get_daily_note(date=today, daily_notes_folder="Daily Notes")
Read or create today's daily note.

---

## Wiki Operations

This vault implements Karpathy's LLM wiki pattern. Schema: `CLAUDE.md` (vault root).

### `/wiki-ingest <source>`

Ingest a source document into the wiki.

```
Workflow:
1. Read source file from raw/ (or the provided content/URL)
2. State key takeaways (2-3 sentences)
3. create_note("wiki/sources/[slug].md", ...) — source summary page
4. For each relevant concept (3-8 typical):
   - If page exists: read_note → update_note with new info
   - If new: create_note("wiki/concepts/[slug].md", ...)
5. For each relevant entity:
   - Same pattern as concepts
6. read_note("wiki/index.md") → update_note with new pages added
7. append_to_note("wiki/log.md", log_entry)
```

**Log entry format:**
```
## [YYYY-MM-DD] ingest | Source Title
- New pages: [list]
- Updated pages: [list]
- Key takeaway: [one sentence]
```

**Source page frontmatter:**
```yaml
---
title: "Source: Title"
type: source
tags: [tag1, tag2]
sources: [raw/filename.md]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

---

### `/wiki-query <question>`

Query the wiki for an answer.

```
Workflow:
1. read_note("wiki/index.md") — identify relevant pages
2. read_note each relevant page (concepts, entities, analyses)
3. Synthesize answer with [[wiki link]] citations
4. Ask: "Should I file this as a wiki page?"
5. If yes: create_note("wiki/analyses/[slug].md", ...) + update index + log
```

**Analysis page frontmatter:**
```yaml
---
title: "Analysis: Question Summary"
type: analysis
tags: [tag1, tag2]
sources: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

**Log entry format:**
```
## [YYYY-MM-DD] query | Question summary
- Pages consulted: [list]
- Filed as: wiki/analyses/[slug].md (or: not filed)
```

---

### `/wiki-lint`

Health check the wiki.

```
Workflow:
1. read_note("wiki/index.md") — get all registered pages
2. list_notes("wiki/") — find all actual pages
3. Check for:
   - Orphan pages (in folder but not in index) — fix automatically
   - Pages in index that don't exist — flag
   - Contradictions — search_notes for conflicting claims, flag for human review
   - Missing cross-references — check Related sections, suggest additions
   - Concepts mentioned in multiple pages but lacking own page — list as candidates
   - Data gaps — topics where a web search would fill a real hole
4. Fix what can be fixed automatically (orphans, missing index entries)
5. append_to_note("wiki/log.md", lint_report)
```

**Log entry format:**
```
## [YYYY-MM-DD] lint | Health check
- Orphans fixed: N
- Contradictions flagged: [list or none]
- New page candidates: [list]
- Data gaps: [list]
```

---

## Folder Convention

```
vault/
  raw/                ← immutable source documents (articles, clips, papers)
    assets/           ← downloaded images
  wiki/               ← LLM-maintained wiki (the compiled knowledge base)
    index.md          ← content catalog
    log.md            ← append-only operation log
    overview.md       ← high-level synthesis
    concepts/         ← topic/concept pages
    entities/         ← people, tools, companies
    sources/          ← one page per ingested raw/ document
    analyses/         ← filed query answers
  000 MOC/            ← navigation hub
  Wiki/               ← legacy (migrate into wiki/ as topics come up)
  Business/           ← playbooks and strategy
  Inbox/              ← unprocessed research (ingest candidates)
  Daily Notes/        ← YYYY-MM-DD.md daily notes
  Archive/            ← done / old notes
```

## Integration with /today and /emerge
- `/today` can call `get_daily_note` to open today's note
- `/emerge` calls `get_recent_notes(days=90, min_days=14)` to find ideas from 2+ weeks ago
- Both commands check vault AND the filesystem context files

## Key Notes
- Vault path must be set in `OBSIDIAN_VAULT_PATH` env var in `.mcp.json`
- Filesystem-based — no Obsidian app or plugin required
- Safe: only reads/writes `.md` files, never touches Obsidian internal files (`.obsidian/`)
- Korean text fully supported (UTF-8)
