# VS Code → Obsidian: Extraction Workflow

Extract key information from VS Code sessions into Obsidian for long-term knowledge retention.

---

## When to extract

| Trigger | What to extract | Obsidian folder |
|---------|----------------|-----------------|
| New project decision | Architecture, rationale, trade-offs | `Projects/` |
| Debugging session | Root cause, fix pattern, what not to do | `Learning/` |
| Research finding | Key insight, source, applicability | `Learning/` |
| Meeting / SDC | Summary, decisions, next steps | `Contacts/` |
| Code pattern learned | Snippet, when to use, gotchas | `Learning/` |
| Daily priorities | What's in flight, blockers | `Daily Notes/` |

---

## Method 1: Manual (fastest)

At the end of a session, tell Claude:
> "Extract today's key learnings to Obsidian"

Claude will call `mcp__obsidian__create_note` or `mcp__obsidian__append_to_note` with structured content.

---

## Method 2: `/session-end` auto-extract

The `/session-end` command already saves a session summary to `templates/session-summary.md`.
Extension: add this line to `.claude/commands/session-end.md`:

```
After writing the session summary, extract the 3 most important learnings
to Obsidian under Learning/YYYY-MM-DD-session.md using create_note.
```

---

## Method 3: Tag-based capture

During a session, say:
> "#obsidian: LangGraph checkpointer v3 requires explicit thread_id in config"

At session end, Claude scans the conversation for `#obsidian:` tags and bulk-creates notes.

---

## Folder structure in Claude_obs vault

```
Claude_obs/
  Daily Notes/       ← YYYY-MM-DD.md (created by /today)
  Projects/          ← one note per project, links to GitHub
  Learning/          ← AI concepts, code patterns, debugging fixes
  Contacts/          ← SDC members, leads, people met
  Archive/           ← old notes, completed projects
```

---

## Quick commands (once VS Code reloads MCP)

```
# Check vault
"show me my vault structure"

# Today's note
"open today's note"

# Save a learning
"add this to Obsidian: <insight>"

# Find old notes
"what did I write about LangGraph"
```

---

## Current status

- Vault path: `C:/Users/keonh/OneDrive/바탕 화면/Claude_obs`
- MCP config: updated in `.mcp.json`
- **Action needed: restart VS Code** to reload the MCP server with the new vault path
- After restart: test with `"show me my vault structure"`
