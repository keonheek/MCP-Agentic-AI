---
name: research-pipeline
description: Post-research automation — after any research completes, auto-ingest the report into Obsidian wiki. If YouTube URLs are found, extract transcripts and ingest those too. Update Notion only if research is explicitly tied to a project.
---

# Skill: Research-to-Knowledge Pipeline

Runs automatically after any Mode 2 or Mode 3 research completes, or when triggered manually on an existing report file.

## Trigger phrases
- "ingest this research"
- "add to wiki"
- After any research skill run (chain automatically)

---

## Pipeline Steps

### Step 1 — Identify the report
- If just completed a research run: use the saved `research/YYYY-MM-DD-[slug].md` path
- If triggered manually: ask for the file path

### Step 2 — Ingest into Obsidian wiki
Call the `obsidian` skill with `/wiki-ingest` on the report file.
- This adds the report to the LLM wiki system as a queryable knowledge entry
- If Obsidian MCP is not connected, skip and note it silently

### Step 3 — Extract YouTube URLs (if any)
Scan the report file for YouTube URLs (pattern: `youtube.com/watch` or `youtu.be/`).
- For each URL found, call `mcp__youtube_transcript__get_transcript` to extract the transcript
- Summarize the transcript into key findings (5-10 bullets)
- Save to `research/transcripts/YYYY-MM-DD-[video-slug].md`
- Ingest the transcript summary into Obsidian wiki via `/wiki-ingest`

### Step 4 — Notion update (conditional)
Only update Notion if the research is explicitly tied to a project.
- Check if the user mentioned a specific project (e.g., "research for GEO agency", "for SME Diagnostic")
- If yes: use the `notion` skill to update the relevant project page with a 3-bullet summary + link to the report
- If no: skip silently

### Step 5 — Confirm
Output one line: "Ingested to Obsidian wiki. [X YouTube transcripts extracted.]" — only mention what actually ran.

---

## Rules
- Never re-ingest a report already in the wiki — check for duplicates by filename before ingesting
- YouTube transcript extraction is best-effort — if a video is unavailable, log the URL and continue
- Do not summarize the research again in chat — the research skill already did that
- Notion update is opt-in, not default
