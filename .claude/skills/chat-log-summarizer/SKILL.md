# Skill: Chat Log Summarizer

Extract decisions, progress, and open items from any conversation — and persist what matters to the right files automatically.

Updated 2026-03-11: Added auto-persistence to decisions/log.md and memory updates.

## Trigger phrases
- "summarize this conversation"
- "what did we cover so far"
- "catch me up"
- "what decisions did we make today"
- "summarize [topic] from our earlier discussion"
- "close out this session"
- "session summary"

---

## How to use
- **Mid-session**: "summarize what we've covered so far" — get a structured snapshot
- **End of session**: "close out this session" — Claude fills `templates/session-summary.md` and logs decisions
- **Cross-session**: Paste a previous chat log and say "summarize this"

---

## What Claude does

1. **Extract signal from the conversation:**
   - What got done (completed tasks, shipped files, decisions made)
   - What's still open (blockers, next actions, deferred work)
   - What to remember (preferences, patterns, corrections)

2. **Persist what matters:**
   - If any decisions were made → append to `decisions/log.md`
   - If any new patterns or preferences emerged → update `memory/MEMORY.md`
   - If end-of-session → write full summary to `templates/session-summary.md`

3. **Return a structured summary:**

---

## Output format

**What Got Done**
- [bullet list — specific file names, tool names, outcomes]

**Decisions Made**
- [bullet list — each one worth logging]

**Open Items / Next Steps**
- [bullet list — prioritized, most time-sensitive first]

**Blockers (human action needed)**
- [anything that requires Keonhee to do something before Claude can continue]

**Anything to Log or Remember**
- Decisions worth adding to `decisions/log.md`
- Preferences or patterns to add to `memory/MEMORY.md`

---

## Auto-persistence rules

When summarizing end-of-session:
- **Always** append any meaningful decision to `decisions/log.md` in format: `[YYYY-MM-DD] DECISION: ... | REASONING: ... | CONTEXT: ...`
- **Check** if any corrections or new patterns should update `memory/MEMORY.md` — update it if yes
- **Write** the session summary to `templates/session-summary.md` with today's date

Do NOT log trivial actions (file edits, debug runs) — only decisions with future implications.

---

## Notes
- Be specific: "edited app.py" is useless in a summary. "Added streaming to FinAgent via graph.stream()" is useful.
- Prioritize open items by urgency: human-blocked items first, then active tasks, then backlog
- If the session touched `context/current-priorities.md`, note whether priorities changed
