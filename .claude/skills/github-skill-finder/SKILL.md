# GitHub Skill Finder

Search GitHub for repositories that can be turned into Claude Code skills or MCP servers. Evaluate repos for quality, and generate a ready-to-use SKILL.md draft.

## When to use this skill
- "Find a GitHub repo for X" / "Is there a skill for X?"
- "Look for MCP servers that do X"
- "Find best practices for X on GitHub"
- "Turn this repo into a skill"

## Search Strategy

### Step 1 — Multi-query search
Run 3 searches in parallel using `mcp__github__search_repositories`:
1. Primary: exact tool name + "mcp" or "claude" (e.g., "obsidian mcp server")
2. Broad: tool name + "python" or "api" (e.g., "obsidian python")
3. Pattern: "claude-code skill" or "claude code hook" + topic

Then use `mcp__github__search_code` to find:
- `SKILL.md` files in any repo (shows existing skill patterns)
- `server.py` or `index.ts` files in MCP-tagged repos

### Step 2 — Evaluate each repo on these criteria

| Criterion | Weight | What to check |
|-----------|--------|---------------|
| Stars | 20% | >100 stars = proven; >500 = established |
| Last commit | 20% | <3 months ago = active; >1 year = risky |
| README quality | 20% | Clear install, usage examples, API docs |
| MCP compatibility | 20% | Uses `@modelcontextprotocol/sdk` or `mcp` Python package |
| Skill-ability | 20% | Can it be wrapped in a SKILL.md with clear trigger phrases? |

Score each repo 1-5 per criterion. Total max = 25.

### Step 3 — Read top repo
Use `mcp__github__get_file_contents` to read:
- `README.md`
- `package.json` or `pyproject.toml` (check dependencies)
- Main entry file (`server.py`, `index.ts`, `main.py`)

### Step 4 — Generate SKILL.md draft
Based on the repo, write a complete SKILL.md following this template:

```markdown
# [Tool Name] Skill

[One-line description of what this skill does]

## Installation (if needed)
[pip install / npm install command]
[Any auth steps]

## When to use this skill
[Trigger phrases — specific phrases Keonhee might say]

## Capabilities

### 1. [Primary capability]
[Code example or step-by-step]

### 2. [Secondary capability]
[Code example or step-by-step]

## Key Notes
- [Gotcha 1]
- [Gotcha 2]
- [Rate limits or costs if any]

## Common Trigger Phrases
- "[example phrase 1]"
- "[example phrase 2]"
```

### Step 5 — Output
Return:
1. Ranked repo list (top 5, with scores)
2. Recommendation: which repo to build from + why
3. Draft SKILL.md for the top repo
4. Any MCP server registration snippet for `.mcp.json` if applicable

## Key Rules
- Always check `last_push` date — stale repos are risky for skills
- Prefer Python repos (Keonhee's stack) over Node.js unless Node is the only option
- If no repo exists: say so clearly and suggest building from scratch with the `cli-anything` skill
- Never recommend a repo without reading its README first
- Flag any repos with no license (can't be used commercially)

## MCP Server Pattern (Python)
If building a new MCP server from a repo:

```python
# server.py skeleton
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

app = Server("tool-name")

@app.list_tools()
async def list_tools():
    return [types.Tool(name="tool_action", description="...", inputSchema={...})]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    # wrap the repo's functionality here
    pass

async def main():
    async with stdio_server() as streams:
        await app.run(*streams, app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

Register in `.mcp.json`:
```json
"tool-name": {
  "command": "python",
  "args": ["path/to/server.py"],
  "env": {"API_KEY": "..."}
}
```
