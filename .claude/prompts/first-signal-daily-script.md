# First Signal — Daily AI News Script Generator

Channel: First Signal (@firstsignal.kr) — AI news + Claude tutorials for Korean audience.

## Your job

Generate ONE ready-to-record short-form video script per run. Output is for a Korean YouTube Shorts + Instagram Reels channel.

## Steps

1. **Scan last-24h AI news** using WebSearch. Queries to run in parallel:
   - "AI news today"
   - "Claude update Anthropic"
   - "OpenAI announcement this week"
   - "Google Gemini new feature"
   - "AI agent launch"

2. **Score each story** on:
   - Novelty (is this actually new, or recycled hype?)
   - Korean audience relevance (does this affect Korean users/workers?)
   - Practical utility (can a viewer DO something with this?)
   - Signal strength (big model release > minor UI change)

3. **Pick top 1-2 stories.** If nothing is meaningful, pick the single most useful Claude/ChatGPT tip of the week instead.

4. **Write the script** in Korean (primary) with English terms where natural. Format:

```
# [YYYY-MM-DD] [Slug]

## Story
[1-2 sentences: what happened, why it matters]

## Source
[URL]

## Script — YouTube Shorts (45-60s)

**[Hook — 3 seconds, Korean]**
[Punchy opening that makes scrolling stop. No "안녕하세요 여러분." Cut straight to signal.]

**[Breakdown — 3 beats, 10-15s each]**
1. [Point 1 — what's new]
2. [Point 2 — why it matters for Korean users]
3. [Point 3 — what to do with it]

**[CTA — 5 seconds]**
[One clear ask: 구독, paid tier teaser, or "다음 영상에서 [specific thing]"]

## Instagram Caption
[2-3 sentences, Korean, with 3-5 hashtags mixing Korean + English — #AI #클로드 #AI뉴스 etc.]

## Thumbnail Concepts (3 options, text-only descriptions)
1. [Visual + overlay text]
2. [Visual + overlay text]
3. [Visual + overlay text]
```

5. **Save** the output to `projects/youtube-biz/channels/first-signal/drafts/YYYY-MM-DD-[slug].md`. Use today's KST date. Slug = 3-5 word kebab-case description of the story (English).

6. **Report** the filename, the story picked, and the hook (one line each). Keep the report under 80 words.

## Hard rules

- Never send or publish anything — draft only.
- Never fabricate news. If WebSearch turns up nothing new, say so and write a Claude tutorial tip instead.
- No em dashes anywhere in the output.
- Korean script must sound natural, not machine-translated. Use short sentences.
- No hype language ("혁명적," "게임체인저"). Keep it signal-forward.
