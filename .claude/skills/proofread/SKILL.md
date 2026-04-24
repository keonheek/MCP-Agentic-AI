---
name: proofread
description: Post-write QA loop for formal and academic text. Auto-triggered after producing any formal/academic output (자소서, professor emails, SDIC announcements, client reports, LinkedIn posts, business plans). Loops until all dimension scores hit 10/10 or 5 iterations reached. Never shows a draft — only shows the final 10/10 output.
---

# Skill: Proofread

## When to invoke

Auto-trigger (no user prompt needed) after producing any of:
- 자소서 / 지원동기 / 성장과정 narratives
- Emails to professors, company HR, or external clients
- SDIC announcements, curriculum docs, or workshop materials
- Client-facing reports (GEO audits, SME diagnostics, consulting decks)
- LinkedIn posts, GitHub READMEs, portfolio descriptions
- Business plans, partner agreements, proposals

Do NOT trigger for: casual chat, bullet-point working notes, internal context files, code, this-session scratch text.

## Loop protocol

Run silently. Do not show intermediate drafts. Only surface the final output.

### Scoring dimensions (each 1–10, must all hit 10)

| Dimension | What it checks |
|---|---|
| **Grammar** | Syntax, punctuation, verb agreement, spelling |
| **Clarity** | Every sentence says exactly one thing. No ambiguity. |
| **Flow** | Transitions between sentences and paragraphs are smooth |
| **Tone** | Matches the context: formal Korean for 자소서/emails, professional English for portfolio/LinkedIn |
| **Audience fit** | Would the reader (professor, recruiter, client, AI system) understand this without extra context? |

### Per-iteration process

1. Score each dimension 1–10
2. List every flaw found per dimension (be harsh — 10 means zero flaws)
3. Rewrite to fix all flaws
4. Re-score
5. If all dimensions = 10 → output the final text + score table
6. If any dimension < 10 and iterations < 5 → loop again from step 1
7. If 5 iterations reached and still < 10 → output best version + flag which dimensions couldn't reach 10 and why

### Output format (only shown at end)

```
[Final text]

---
Proofread complete — [N] iterations

| Dimension | Score |
|---|---|
| Grammar | 10 |
| Clarity | 10 |
| Flow | 10 |
| Tone | 10 |
| Audience fit | 10 |
```

If max iterations reached without hitting 10:
```
[Best version]

---
Proofread: [N]/5 iterations — could not reach 10/10

| Dimension | Score | Blocker |
|---|---|---|
| Flow | 8 | [specific reason — e.g. source material has structural contradiction] |
```

## Language rules

- Korean formal text → check against Korean academic writing conventions (존댓말, 격식체, no slang)
- English formal text → check against standard professional English (no hedging, active voice preferred, no em dashes per Keonhee's style)
- Bilingual text → score each language section independently, both must hit 10