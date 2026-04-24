---
name: daily-content-machine
description: Generate one piece of public content per day from active project data. Rotates through Naver Blog, LinkedIn, KakaoTalk templates, and case studies. Scores to 8.0+ via autoresearch loop before saving to drafts/.
---

# Skill: Daily Content Machine

Generates one piece of public-facing content per day from Keonhee's active project data. Runs at 9am via cron, or manually with trigger phrases.

## Trigger phrases
- "generate today's content"
- "daily content"
- "draft something for [platform]"

---

## Content Rotation

Cycle through these types in order, rotating daily:
1. KakaoTalk template (outreach or social proof post)
2. Naver Blog post (Korean, educational — "세무사가 ChatGPT에 안 나오는 이유")
3. LinkedIn post (English, GEO/AI angle)
4. GitHub README update (improve a project's GEO citability)
5. Case study snippet (anonymized client result — before/after)

Check `drafts/` for the most recently generated type and pick the next in rotation.

---

## Steps

### Step 1 — Load context
Read in parallel:
- `context/current-priorities.md` — active business focus
- `tasks/todo.md` — any pending content items
- Latest file in `projects/geo-agency/output/` (for real audit data if available)

### Step 2 — Pick content type
Based on rotation (see above). If user specifies a type, use that instead.

### Step 3 — Generate content
Use source material from Step 1. Do not fabricate data — use real audit scores, real competitor names, real before/after metrics if available. If no real data exists, use the 라라스윗 팝콘 audit as the demo case.

**Platform-specific rules:**
- KakaoTalk: 150 chars max for preview. Hook in first line. End with CTA.
- Naver Blog: 600-1000 words. Korean. Educational tone. Free audit CTA at end.
- LinkedIn: 200-300 words. English. Professional. End with a question to drive comments.
- GitHub README: Update one project README — add business impact framing, GEO keywords.
- Case study: 3 sections — Before (problem), After (result), Quote (fabricated but realistic).

### Step 4 — Autoresearch quality loop
Score on:
- KakaoTalk/LinkedIn: hook_strength, personalization, CTA clarity, brevity
- Naver Blog: educational value, specificity, SEO keyword density, CTA clarity
- Case study: believability, specificity, emotional resonance, proof of result

Threshold: 8.0. Max 5 iterations. Haiku scores, Sonnet rewrites.

### Step 5 — Save draft
Save to `drafts/YYYY-MM-DD-[type]-[slug].md`

### Step 6 — Add human review task
Append to `tasks/todo.md`:
`- [ ] Review and publish [type] draft — drafts/YYYY-MM-DD-[type]-[slug].md (human)`

### Step 7 — Append to Obsidian daily note
Add a one-liner to today's Obsidian note: "Content draft ready: [type] — [slug]"

### Step 8 — Confirm
Output: "Draft saved to drafts/[filename]. Score: [X]/10. Added to todo.md for review."

---

## Rules
- One piece of content per run — do not generate multiple at once
- Never publish directly — always save to drafts/ for human review
- Use real data where available; fall back to 라라스윗 팝콘 demo case otherwise
- Korean content: no emojis, professional tone
- English content: no emojis unless LinkedIn post style warrants it