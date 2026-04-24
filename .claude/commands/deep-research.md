/deep-research — Multi-hop research via sub-agent loop OR Gemini handoff

Run the `research` skill in Mode 3 (Deep Research Loop) on the topic provided in the arguments.

Workflow:
1. Load context from `context/me.md`, `context/work.md`, `context/current-priorities.md`, `context/goals.md`
2. Decompose the topic into 5-8 sub-questions. Print them.
3. Ask Keonhee: "Run the sub-agent loop (free, ~5 min) or generate a Gemini 3.1 Pro Deep Research prompt for you to paste?"
4. **If sub-agent loop (default):**
   - Spawn a single `general-purpose` sub-agent with the sub-questions + clear instructions
   - Sub-agent runs Round 1 (WebSearch each sub-question, WebFetch top 2 results), synthesizes partials with `[GAP: ...]` markers, runs Round 2 on gaps, returns a condensed synthesis + source list (NOT raw search results)
   - Main session receives the synthesis, writes the final structured report to `research/YYYY-MM-DD-[slug]-deep.md`, and shows the chat summary (5 bullets + file link)
   - This isolates the search context burn in the sub-agent — main session stays clean
5. **If Gemini handoff:**
   - Fill the prompt template from `.claude/skills/research/SKILL.md` (Gemini handoff section)
   - Output the prompt in a code block for easy copy
   - Do NOT run anything — wait for Keonhee to paste back results, then integrate into `research/`

Sub-agent prompt template (for step 4):

```
Run a Mode 3 deep research loop on this topic:

[TOPIC]

Sub-questions to answer:
1. [...]
2. [...]
(etc.)

Method:
- Round 1: WebSearch each sub-question, WebFetch top 2 results per search
- After Round 1: write 1-paragraph partials per sub-question, mark gaps as [GAP: ...]
- Round 2: targeted WebSearch on each gap
- Final: synthesize into a structured report

Budget: 40 WebSearch calls, 30 WebFetches. Raise if genuinely needed.

Return to me:
- Full structured synthesis (sections, findings, caveats)
- Complete source list with URLs
- Any open questions / gaps that remain

Do NOT return raw search result text. I need the distilled output, not the transcript.
```

Hard rules:
- Never call Perplexity. This command is $0 external cost.
- Budget cap inside sub-agent: 40 WebSearches, 30 WebFetches (soft cap — raise if topic warrants)
- Main session token cost stays low because sub-agent context is isolated
- Project scripts (SME Diagnostic, benchmark_research) are untouched — they keep Perplexity