# Lessons — Self-Improvement Log

After any correction, mistake, or pattern worth remembering, append here.
Claude reads this at session start to avoid repeating the same errors.

Format: `[YYYY-MM-DD] MISTAKE/PATTERN: ... | FIX: ... | RULE: ...`

---

[2026-03-09] MISTAKE: Tried to Write a file without reading it first, causing tool error. | FIX: Always Read before Write or Edit. | RULE: Read → Edit/Write. Never Write cold.

[2026-03-09] MISTAKE: Put Korean characters (바탕 화면) directly in a JSON hook command string — caused encoding fragility. | FIX: Extract the logic to a .py helper script and call the script path instead. | RULE: Never embed multi-byte paths in inline JSON strings. Use a script file.

[2026-03-09] MISTAKE: Attributed ChromaDB failure to "MCP compatibility" in mock interview context. | FIX: Correct explanation is Python 3.14 + Pydantic v1 runtime type inference issue. | RULE: ChromaDB fails on Python 3.14 due to Pydantic v1, not MCP. State this precisely.

[2026-03-09] PATTERN: Wispr Flow voice-to-text causes phonetic typos in Korean/English tech terms (e.g. "link chain" → LangChain). | RULE: Interpret tech term typos charitably. Always confirm before correcting.

[2026-03-09] PATTERN: User prefers to keep moving — flag human-in-loop blockers and skip, don't stop. | RULE: Note blocked items in a queue, continue to next task automatically.

[2026-03-12] CORRECTION: "Cover letters" do not exist in Korean job applications. The correct format is 자기소개서 (자소서) — structured responses to company-specific prompts (지원동기, 성장과정, 직무 경험, 장단점 etc.). What was created in `projects/next-ai-role/cover-letter-*.md` are 자소서 narrative drafts, not ready-to-submit documents. Each company's actual 자소서 questions must be pulled from their application portal first, then the narrative content mapped to those prompts.
