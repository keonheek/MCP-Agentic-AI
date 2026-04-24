"""
Obsidian MCP Server — Filesystem-based vault access for Claude Code

Exposes Obsidian vault operations as MCP tools:
- read_note, create_note, update_note, append_to_note
- search_notes (full-text), search_by_tag
- list_notes, get_vault_structure
- get_recent_notes (for /emerge — surfaces old ideas)
- get_today_notes (for /today — daily context)

No Obsidian app or plugin required — reads vault directly from filesystem.

Setup:
  1. Set OBSIDIAN_VAULT_PATH in .mcp.json env
  2. python tools/obsidian-mcp/server.py
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Any

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    import mcp.types as types
except ImportError:
    print("mcp package not installed. Run: pip install mcp")
    import sys; sys.exit(1)

VAULT_PATH = Path(os.environ.get("OBSIDIAN_VAULT_PATH", ""))
app = Server("obsidian-vault")


def _vault() -> Path:
    if not VAULT_PATH or not VAULT_PATH.exists():
        raise ValueError(f"OBSIDIAN_VAULT_PATH not set or does not exist: {VAULT_PATH}")
    return VAULT_PATH


def _all_md_files() -> list[Path]:
    return sorted(_vault().rglob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML frontmatter from note. Returns (metadata_dict, body_text)."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm_raw = text[3:end].strip()
            body = text[end + 4:].strip()
            meta = {}
            for line in fm_raw.splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    meta[k.strip()] = v.strip().strip('"')
            return meta, body
    return {}, text


def _read_note_raw(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _note_summary(path: Path) -> dict:
    rel = str(path.relative_to(_vault()))
    text = _read_note_raw(path)
    meta, body = _parse_frontmatter(text)
    tags = meta.get("tags", "")
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.replace(",", " ").split() if t.strip()]
    preview = body[:200].replace("\n", " ").strip()
    mtime = datetime.fromtimestamp(path.stat().st_mtime).date().isoformat()
    return {"path": rel, "title": path.stem, "tags": tags, "modified": mtime, "preview": preview}


# ---------------------------------------------------------------------------
# Tool: list_notes
# ---------------------------------------------------------------------------
@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="list_notes",
            description="List all notes in the vault, optionally filtered by folder. Returns title, path, tags, last modified.",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder": {"type": "string", "description": "Subfolder to filter by (optional). Use '' for all."},
                    "limit": {"type": "integer", "description": "Max notes to return (default 50)"},
                },
            },
        ),
        types.Tool(
            name="read_note",
            description="Read the full content of a note by its path relative to vault root.",
            inputSchema={
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Relative path like 'Ideas/startup-idea.md'"}},
                "required": ["path"],
            },
        ),
        types.Tool(
            name="create_note",
            description="Create a new note in the vault.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path for new note, e.g. 'Ideas/new-idea.md'"},
                    "content": {"type": "string", "description": "Full markdown content"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Optional list of tags"},
                },
                "required": ["path", "content"],
            },
        ),
        types.Tool(
            name="update_note",
            description="Overwrite a note's content completely.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        ),
        types.Tool(
            name="append_to_note",
            description="Append text to the end of an existing note.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "text": {"type": "string", "description": "Text to append"},
                },
                "required": ["path", "text"],
            },
        ),
        types.Tool(
            name="search_notes",
            description="Full-text search across all notes in the vault. Returns matching notes with context snippets.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term (case-insensitive)"},
                    "limit": {"type": "integer", "description": "Max results (default 20)"},
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="search_by_tag",
            description="Find all notes with a specific tag.",
            inputSchema={
                "type": "object",
                "properties": {"tag": {"type": "string", "description": "Tag to search for (without #)"}},
                "required": ["tag"],
            },
        ),
        types.Tool(
            name="get_recent_notes",
            description="Get notes modified or created in the last N days. Used by /emerge to surface old ideas.",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "How many days back to look (default 7)"},
                    "min_days": {"type": "integer", "description": "Skip notes newer than this many days (for surfacing OLD ideas, set to 14)"},
                },
            },
        ),
        types.Tool(
            name="get_vault_structure",
            description="Get the folder/file tree of the vault. Useful for understanding what's in the vault.",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="get_daily_note",
            description="Read today's daily note if it exists, or create it from a template.",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format (default: today)"},
                    "daily_notes_folder": {"type": "string", "description": "Folder where daily notes live (default: 'Daily Notes')"},
                },
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    vault = _vault()

    if name == "list_notes":
        folder = arguments.get("folder", "")
        limit = arguments.get("limit", 50)
        files = _all_md_files()
        if folder:
            files = [f for f in files if folder.lower() in str(f).lower()]
        results = [_note_summary(f) for f in files[:limit]]
        return [types.TextContent(type="text", text=json.dumps(results, ensure_ascii=False, indent=2))]

    elif name == "read_note":
        path = vault / arguments["path"]
        if not path.exists():
            return [types.TextContent(type="text", text=f"Note not found: {arguments['path']}")]
        return [types.TextContent(type="text", text=_read_note_raw(path))]

    elif name == "create_note":
        path = vault / arguments["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        tags = arguments.get("tags", [])
        content = arguments["content"]
        if tags and not content.startswith("---"):
            tag_line = ", ".join(tags)
            content = f"---\ntags: {tag_line}\ncreated: {date.today().isoformat()}\n---\n\n{content}"
        path.write_text(content, encoding="utf-8")
        return [types.TextContent(type="text", text=f"Created: {arguments['path']}")]

    elif name == "update_note":
        path = vault / arguments["path"]
        if not path.exists():
            return [types.TextContent(type="text", text=f"Note not found: {arguments['path']}")]
        path.write_text(arguments["content"], encoding="utf-8")
        return [types.TextContent(type="text", text=f"Updated: {arguments['path']}")]

    elif name == "append_to_note":
        path = vault / arguments["path"]
        if not path.exists():
            return [types.TextContent(type="text", text=f"Note not found: {arguments['path']}")]
        existing = _read_note_raw(path)
        path.write_text(existing.rstrip() + "\n\n" + arguments["text"], encoding="utf-8")
        return [types.TextContent(type="text", text=f"Appended to: {arguments['path']}")]

    elif name == "search_notes":
        query = arguments["query"].lower()
        limit = arguments.get("limit", 20)
        results = []
        for f in _all_md_files():
            text = _read_note_raw(f)
            if query in text.lower():
                idx = text.lower().find(query)
                snippet = text[max(0, idx - 80):idx + 120].replace("\n", " ").strip()
                results.append({"path": str(f.relative_to(vault)), "title": f.stem,
                                 "modified": datetime.fromtimestamp(f.stat().st_mtime).date().isoformat(),
                                 "snippet": f"...{snippet}..."})
            if len(results) >= limit:
                break
        return [types.TextContent(type="text", text=json.dumps(results, ensure_ascii=False, indent=2))]

    elif name == "search_by_tag":
        tag = arguments["tag"].lower().lstrip("#")
        results = []
        for f in _all_md_files():
            text = _read_note_raw(f)
            meta, _ = _parse_frontmatter(text)
            tags_raw = meta.get("tags", "")
            tags = [t.strip().lower().lstrip("#") for t in str(tags_raw).replace(",", " ").split()]
            # also check inline #tags in body
            inline = re.findall(r"#(\w+)", text)
            all_tags = set(tags + [t.lower() for t in inline])
            if tag in all_tags:
                results.append(_note_summary(f))
        return [types.TextContent(type="text", text=json.dumps(results, ensure_ascii=False, indent=2))]

    elif name == "get_recent_notes":
        days = arguments.get("days", 7)
        min_days = arguments.get("min_days", 0)
        cutoff = datetime.now().timestamp() - days * 86400
        min_cutoff = datetime.now().timestamp() - min_days * 86400 if min_days else None
        results = []
        for f in _all_md_files():
            mtime = f.stat().st_mtime
            if mtime >= cutoff:
                if min_cutoff and mtime > min_cutoff:
                    continue  # too recent — skip for /emerge
                results.append(_note_summary(f))
        return [types.TextContent(type="text", text=json.dumps(results, ensure_ascii=False, indent=2))]

    elif name == "get_vault_structure":
        lines = []
        for p in sorted(vault.rglob("*")):
            rel = p.relative_to(vault)
            depth = len(rel.parts) - 1
            prefix = "  " * depth + ("📁 " if p.is_dir() else "📄 ")
            lines.append(prefix + p.name)
        return [types.TextContent(type="text", text="\n".join(lines[:200]))]

    elif name == "get_daily_note":
        target_date = arguments.get("date", date.today().isoformat())
        folder = arguments.get("daily_notes_folder", "Daily Notes")
        fname = f"{target_date}.md"
        path = vault / folder / fname
        if path.exists():
            return [types.TextContent(type="text", text=_read_note_raw(path))]
        # Create from template
        path.parent.mkdir(parents=True, exist_ok=True)
        template = f"# {target_date}\n\n## Tasks\n- [ ] \n\n## Notes\n\n## Ideas\n"
        path.write_text(template, encoding="utf-8")
        return [types.TextContent(type="text", text=f"Created daily note: {path}\n\n{template}")]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as streams:
        await app.run(*streams, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
