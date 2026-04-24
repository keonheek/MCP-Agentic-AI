# Tool Integrations

## MCP Servers (active)
- **obsidian** — Obsidian vault at `Claude_obs/`. Read/write daily notes, search tags.
- **context-mode** — SQLite-backed session sandbox. Stores tool outputs, retrieves only relevant events via BM25 on compaction. ~98% context reduction. (`context-mode` on npm)
- **youtube-transcript** — YouTube transcript extraction. Feed any YouTube URL, get full transcript instantly. 25K token limit per video. Use for single-video learning. (`@fabriqa.ai/youtube-transcript-mcp`)

## MCP Servers (disabled — re-enable as needed)
- **Notion** — MCP for notes, databases, project tracking. Re-enable: uncomment in `.mcp.json`.
- **notion-sdc** — SDC workspace (separate Notion token). Re-enable for SDC ops.
- **github** — GitHub API. Re-enable for PR/issue work.
- **dart** — DART Korean financial data. Server: `c:/Users/keonh/OneDrive/바탕 화면/dart-mcp-server/server.py`. Tools: search_company, get_financials, get_company_info, get_disclosures.
- **slack** — Placeholder (no real token configured).
- **n8n** — Deferred until 3+ active clients.

## Other Tools
- **Claude Code** — Primary workspace.
- **ngrok** — `ngrok http 8000` to expose local backend for demos.
- **Wispr Flow** — Voice-to-text. Typos and awkward phrasing are Wispr artifacts — interpret charitably.
- **Perplexity API** — Use instead of Gemini (blocked in South Korea).
- **Google Drive** — Potential MCP. Check `.claude/settings.json` for current state.
