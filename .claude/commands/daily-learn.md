# /daily-learn — Daily Learning Lesson

Run one focused learning lesson across all 5 tracks. Executes autonomously every day.

## Step 1 — Read curriculum state
Read `learning/curriculum.md`. For each track, find the first `[ ]` item marked "In Progress" or the first item in "Queue".

## Step 2 — Pick today's focus track
Rotate through tracks by day of week:
- Monday: AI Engineering
- Tuesday: SQL
- Wednesday: Data Engineering
- Thursday: ML / Deep Learning
- Friday: Finance
- Saturday: Free choice (pick whichever track has fallen most behind)
- Sunday: Review + consolidate (no new topic — review outputs from the week)

## Step 3 — Deliver the lesson

For each day's track, do ALL of the following:

### A. Concept explanation (3-5 minutes to read)
Write a clear, concrete explanation of the topic. No fluff.
- What it is (1 paragraph)
- Why it matters for Keonhee's stack specifically (1 paragraph)
- One analogy that makes it click

### B. Code example
Write working Python code that demonstrates the concept.
- Use Keonhee's existing projects as context where possible (FinAgent, SME Diagnostic, DART)
- Code must run with minimal setup
- Include comments explaining each step

### C. Practice exercise
Give 1-3 exercises to try:
- SQL tracks: write actual queries
- ML tracks: modify the code example
- Finance tracks: apply to a real Korean company (Samsung, Kakao, Naver)
- AI Engineering: extend an existing project file

### D. Resource pointer
Point to the single best resource to go deeper:
- Prefer free resources (YouTube, official docs, Kaggle)
- One link max — don't overwhelm

### E. Save lesson output
Save the full lesson to:
`learning/outputs/YYYY-MM-DD-[track]-[topic-slug].md`

Format:
```markdown
# [Track]: [Topic]
_Date: YYYY-MM-DD | Level: [beginner/intermediate] | Time: ~30 min_

## Concept
[explanation]

## Code
```python
[code]
```

## Exercises
1. [exercise 1]
2. [exercise 2]

## Go Deeper
[one resource link]

## Did it click? (fill in after doing the exercises)
- [ ] Yes — move to next topic
- [ ] Partially — needs revisit
- [ ] No — add to curriculum.md "Needs Revisit"
```

## Step 4 — Update curriculum
Mark the current "In Progress" item as complete `[x]` in `learning/curriculum.md`.
Move the next Queue item to "In Progress".

## Step 5 — Report
Output:
```
Daily Lesson — [DATE]
Track: [track name]
Topic: [topic name]
Lesson saved: learning/outputs/[filename]
Next up: [next topic in this track]
```

## Rules
- Never skip the code example — concepts without code don't stick
- Use Korean companies and Korean market data for Finance examples
- If the topic needs a Python package not installed, note it at the top: `pip install X`
- Sunday review: read the week's output files and write a 200-word synthesis in `learning/outputs/YYYY-MM-DD-weekly-review.md`
