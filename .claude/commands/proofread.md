# /proofread — Formal Text QA Loop

Run the `proofread` skill on the provided text or file.

Invoke this manually when you have already-written text that needs polishing (e.g., something written in Obsidian, a draft from another tool, or text you wrote yourself).

Usage:
  /proofread [paste text directly]
  /proofread [file path]

The skill will loop silently until all 5 dimensions score 10/10 (max 5 iterations), then return the final result.

Dimensions scored: Grammar, Clarity, Flow, Tone, Audience fit.