# /emerge — Surface Buried Ideas

Surface ideas Keonhee mentioned in passing but never acted on. Execute these steps:

## Step 1 — Scan for idea signals
Search these locations for idea fragments in parallel:

**File system (always):**
- `decisions/log.md` — look for entries tagged with "IDEA", "MAYBE", "EXPLORE", or speculative language
- `tasks/todo.md` — look for backlog items that were never prioritized
- `context/current-priorities.md` — look for anything marked deferred or conditional
- `research/` — glob all `.md` files, scan "Action Queue" and "Actionable Takeaways" sections for unchecked items
- Memory files at `C:\Users\keonh\.claude\projects\c--Users-keonh-OneDrive-------MCP-Agentic-AI\memory\` — scan for deferred/pending notes

**Obsidian vault (if MCP connected):**
- Call `get_recent_notes(days=90, min_days=14)` — notes touched 2+ weeks to 3 months ago
- Call `search_notes("idea")` and `search_notes("maybe")` and `search_notes("someday")`
- Call `search_by_tag("idea")` and `search_by_tag("backlog")`
- If vault is not connected, skip silently — do not error

## Step 2 — Cluster by theme
Group surfaced ideas into clusters:
- **Business / GEO Agency** — monetization, service expansion, client ideas
- **Technical builds** — new projects, tools, integrations
- **Learning / career** — skills to acquire, courses, reading
- **Quick wins** — things that could be done in <1 day

## Step 3 — Output

Format exactly as:

```
## Emerged Ideas — [DATE]

### [Cluster Name]
- **[Idea title]** — [1-line description] | *First mentioned: [date or "unknown"]* | Effort: [small/medium/large]
  → Why now: [one sentence on why this is worth revisiting]

[repeat per cluster]

### Recommended to Act On This Week
[Top 2-3 ideas to pull into todo.md, with rationale]
```

## Step 4 — Offer to activate
After output, ask: "Want me to pull any of these into the active todo list?"
If yes, append to `tasks/todo.md` under "This Week" and update `context/current-priorities.md` if needed.

## Rules
- Include ideas from at least 2 weeks ago — not just recent ones.
- Don't include items already in "This Week" or marked [x] done.
- If an idea appears multiple times across files, surface it once and note "mentioned [N] times."
- Be opinionated — tell Keonhee which ideas are worth acting on now vs. parking.
