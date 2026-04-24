# /wiki-lint — Obsidian Wiki Lint

Runs every Sunday at 8:30pm via cron. Cleans orphan pages, fixes broken links, and updates the wiki index in Obsidian.

## Steps

### Step 1 — Load wiki index
Use the `obsidian` skill to read the LLM wiki index file (typically `LLM Wiki/index.md` or equivalent in the vault).
If not found, skip and note silently.

### Step 2 — Check for orphan pages
List all pages under the wiki directory in Obsidian.
Identify pages not referenced in the index — these are orphans.
For each orphan:
- If it has content and looks like a real entry: add it to the index
- If it's empty or a stub: flag for deletion (do NOT delete — list them for Keonhee to review)

### Step 3 — Check for broken internal links
Scan wiki pages for `[[links]]` that reference pages that don't exist.
List all broken links with their source page.

### Step 4 — Update index
Add any newly discovered pages to the index with a one-line description.
Alphabetize or group by topic if the index has a structure.

### Step 5 — Report
Output a short report:
```
## Wiki Lint — [DATE]

### Added to index: [N pages]
[list]

### Orphan pages (review needed): [N]
[list]

### Broken links: [N]
[source page → broken link]

### No action needed: [N pages healthy]
```

If everything is clean, output: "Wiki lint complete — no issues found."

## Rules
- Never delete Obsidian pages autonomously — only flag for review
- Do not rewrite page content — only update the index and report issues
- If Obsidian MCP is not connected, skip and note silently
