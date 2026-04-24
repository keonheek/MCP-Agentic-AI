# Instagram Feed Sources

Edit this file to tune what the daily pipeline searches for.

## News queries (WebSearch — Step 1)

Literal query strings. The pipeline runs each one and keeps items with a concrete event (release, launch, adoption, benchmark). Opinion pieces are dropped.

1. `agentic AI news past 48 hours`
2. `new LLM release this week`
3. `AI infrastructure launch this week`
4. `enterprise AI implementation case study this week`
5. `AI product launch viral this week`

## X.com handles to track (Step 2 discovery)

The pipeline runs `site:x.com/<handle>` WebSearch for each, then uses Playwright MCP to scrape the actual tweet content + engagement counts.

Curated seed list — AI leaders and builders whose posts regularly go viral:

- `@sama` — Sam Altman, OpenAI
- `@karpathy` — Andrej Karpathy
- `@AnthropicAI` — Anthropic official
- `@OpenAI` — OpenAI official
- `@GoogleDeepMind` — DeepMind official
- `@ylecun` — Yann LeCun, Meta
- `@swyx` — Shawn Wang, AI engineer thought leader
- `@simonw` — Simon Willison, LLM tooling
- `@rauchg` — Guillermo Rauch, Vercel
- `@jerryjliu0` — Jerry Liu, LlamaIndex
- `@LangChainAI` — LangChain official
- `@_akhaliq` — AI paper curator
- `@elder_plinius` — jailbreak / frontier model commentary

Broader discovery queries (run alongside handle searches):
- `site:x.com AI agents viral`
- `site:x.com "just shipped" AI`

Engagement floor: skip anything under 5k likes unless it's from a curated handle above.

## To add

<!-- Append new handles or query strings here. Don't restructure. -->
