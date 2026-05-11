---
description: Judge all LLM eval responses in-session and write scored results to Google Sheet
---

# /llm-eval-judge

Find the latest eval run file in `agents/llm_eval/data/eval_runs/`. It will be named `run_YYYYMMDD_HHMMSS.json`.

The file contains a list of raw response records. Each record has:
- `model`, `prompt_id`, `category`, `inquiry`, `brand_context`, `response`
- `latency_ms`, `input_tokens`, `output_tokens`, `cost_usd`, `dry`

## Judge each response

For each record where `dry` is false, score the `response` on these 5 dimensions (0-10 each):

1. **Korean fluency** - Natural Korean? No translation artifacts or Japanese mixing? Reads naturally to a Korean customer?
2. **Brand voice match** - Does it match a friendly-but-professional skincare brand tone? Correct product/brand naming?
3. **Specificity** - Does it address the actual inquiry content? Mentions specific product names, ingredients? Avoids generic answers?
4. **Action clarity** - Does the customer know what to do next? Appropriate escalation (e.g. to customer service) when needed?
5. **Safety** - Appropriate caution for allergy, pregnancy, medical inquiries? If not applicable to this prompt, score 10.

For records where `dry` is true, set all scores to 0 and reasoning to "DRY MODE: no real response to score".

Compute `composite` = average of the 5 scores, rounded to 2 decimal places.

Add to each record: `fluency`, `brand_voice`, `specificity`, `action_clarity`, `safety`, `composite`, `reasoning` (2-3 sentence Korean or English justification), `judge_model` = "claude-code-session".

## Compute summary per model

Group results by model. For each model compute:
- Average of each score dimension
- Latency p50 and p95 (from live records only)
- Cost per 1K responses in USD
- Count of live vs dry responses
- Rank by avg_composite descending

## Write to Google Sheet

Sheet ID: `16KJE3Yxymw9a28egtdhgSDirlxTr4iPTKTvA1hDyuyE`

Use `gws sheets spreadsheets values batchUpdate` to write:
- **Raw tab**: all records with scores (same column order as before: Model, Prompt ID, Category, Inquiry, Response, Latency ms, Input Tokens, Output Tokens, Cost USD, Fluency, Brand Voice, Specificity, Action Clarity, Safety, Composite, Reasoning, Judge Model, Dry?)
- **Summary tab**: ranked summary table

If the Sheet does not exist yet, create it first using `gws sheets spreadsheets create` with title "Korean LLM Eval: Skincare D2C Customer Service", then move it to folder `1PU6EX-ay-gr3B8FeDwyKOac2zpwXynKy`.

## Recommendation

After writing to sheet, output:
- The top model by avg_composite
- Whether Solar Pro 3 won or lost, and by how much
- One blunt recommendation: LOCK SOLAR, TIE - PICK BY COST, or RECONSIDER (with reason)

Also write the scored results back to the run file (add `_scored` suffix) for local reference.

If gws is not available, print the full scored results and summary table to chat.
