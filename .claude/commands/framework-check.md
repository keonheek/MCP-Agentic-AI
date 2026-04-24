# /framework-check — Context7 + Coding Agent

When a framework or library you use has updated, automatically fetch current docs and check your code for breaking changes.

## When to use
- "check if [library] has breaking changes"
- "we updated to [framework] v[X]"
- "does my code work with the latest [library]"

## Steps

### Step 1 — Identify the library
Ask if not specified: "Which library or framework? (e.g. LangGraph, Streamlit, FastAPI, anthropic-sdk)"

### Step 2 — Fetch current docs via context7
Use the context7 MCP tools:
1. Call `resolve-library-id` with the library name to get the context7 library ID
2. Call `get-library-docs` with the resolved ID to fetch current documentation
3. Note the current version and any changelog / migration notes

### Step 3 — Find relevant files in the project
Glob for files that import or use the library:
- Python: grep for `import [library]` or `from [library]`
- JS/TS: grep for `require('[library]')` or `from '[library]'`

### Step 4 — Spawn coding-agent for breaking change check
Pass the agent:
- The library docs from Step 2
- The list of files from Step 3
- This prompt: "Review these files for breaking changes against the current [library] docs. List: (1) confirmed breaking changes with file + line, (2) deprecation warnings, (3) recommended updates. Do not make changes — report only."

### Step 5 — Output migration plan
Format:
```
## [Library] Breaking Change Report — [DATE]

### Confirmed Breaking Changes
[file:line — what changed — fix]

### Deprecation Warnings
[file:line — what's deprecated — replacement]

### Recommended Updates
[optional improvements based on new API]

### Verdict
[Safe to upgrade / Needs changes before upgrading]
```

Save report to `research/YYYY-MM-DD-[library]-migration.md`.

## Rules
- Report only — do not edit code unless user explicitly asks
- If context7 cannot resolve the library, fall back to WebSearch for changelog
- If no breaking changes found, say so in one line and do not save a file
