---
name: autoresearch
description: Autonomous self-improving research loop based on Andrej Karpathy's autoresearch pattern. Two modes: (1) Content loop — generate→score→improve for text/emails/reports. (2) True Karpathy loop — hypothesis→edit→eval→git commit/reset for any measurable artifact. Trigger phrases: "autoresearch loop", "self-improving", "score and improve", "iterate until good enough", "run experiments automatically", "optimize until metric improves".
---

# Autoresearch (Karpathy Pattern)

Two modes. Pick the right one for the task.

---

## Mode 1: Content Loop (text, emails, reports)

Generate → score with Haiku → improve until threshold. No git. Best for content quality tasks.

**Use when:** Output is text (emails, recommendations, research summaries, GEO content)

```
generate(input)
  -> score(output) using Haiku (cheap)
  -> if avg_score >= threshold: done
  -> else: improve(output, scores, feedback)
  -> repeat up to max_iterations
```

### Implementation

```python
import os, json
import anthropic

SCORER_MODEL = "claude-haiku-4-5-20251001"   # cheap scorer
GENERATOR_MODEL = "claude-sonnet-4-6"         # smart generator
MAX_ITERATIONS = 8
SCORE_THRESHOLD = 7.5


def _score(client, content, context, dimensions=None):
    """Score content on dimensions (0-10 each). Returns dict with feedback."""
    if dimensions is None:
        dimensions = ["relevance", "specificity", "actionability"]
    dims_str = ", ".join(f'"{d}": <0-10>' for d in dimensions)
    prompt = f"""Score this content (0-10 per dimension). Return ONLY valid JSON.

Context: {context}

Content:
{content}

Return:
{{{dims_str}, "feedback": "<one sentence on what to improve>"}}"""

    resp = client.messages.create(
        model=SCORER_MODEL, max_tokens=256,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.splitlines()[1:-1])
    return json.loads(raw)


def _improve(client, content, scores, context):
    """Generate improved version based on score feedback."""
    prompt = f"""Improve this content based on feedback. Return ONLY the improved content.

Context: {context}
Scores: {scores}
Feedback: {scores['feedback']}

Original:
{content}"""
    resp = client.messages.create(
        model=GENERATOR_MODEL, max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.content[0].text.strip()


def run_autoresearch(initial_content, context, max_iterations=MAX_ITERATIONS,
                     threshold=SCORE_THRESHOLD, dimensions=None):
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    content = initial_content
    score_history = []

    for i in range(max_iterations):
        scores = _score(client, content, context, dimensions)
        num_dims = len([k for k in scores if k not in ("feedback",)])
        avg = sum(scores[k] for k in scores if k != "feedback") / num_dims
        scores["avg"] = round(avg, 2)
        score_history.append({"iteration": i + 1, "scores": scores})
        print(f"  Iter {i+1}: avg={avg:.2f} | {scores['feedback']}")

        if avg >= threshold:
            print(f"  Threshold {threshold} reached at iteration {i+1}.")
            break
        if i < max_iterations - 1:
            content = _improve(client, content, scores, context)

    return {
        "final_content": content,
        "final_scores": score_history[-1]["scores"],
        "iteration_count": len(score_history),
        "score_history": score_history,
    }
```

### LangGraph Node

```python
def run_autoresearch_node(state: dict) -> dict:
    result = run_autoresearch(
        initial_content=state["draft_content"],
        context=state.get("context", ""),
        max_iterations=state.get("max_iterations", MAX_ITERATIONS),
        threshold=state.get("score_threshold", SCORE_THRESHOLD),
        dimensions=state.get("score_dimensions"),
    )
    state["final_content"] = result["final_content"]
    state["final_scores"] = result["final_scores"]
    state["iteration_count"] = result["iteration_count"]
    return state
```

---

## Mode 2: True Karpathy Loop (git-based experiments)

Hypothesis → edit one file → run eval → git commit if better, git reset if worse → repeat.

**Use when:** Output is a measurable artifact (code performance, trading strategy, prompt, config, website speed, model training script)

**Required conditions (all three must hold):**
1. **One scalar metric** — a single number, clear direction (lower/higher = better)
2. **Automated eval** — no human in the loop; eval runs in <5 min
3. **One editable file** — the agent edits exactly one file; eval and goal are immutable

**Three-file architecture:**
- `program.md` — the goal, constraints, rules (written by human, read-only to agent)
- `train.py` (or the target file) — the ONE file the agent can modify
- `prepare.py` / `benchmark.js` — the eval script; NEVER modified by agent

### Setup Template

**Step 1 — Write `program.md`** (adapt this template):

```markdown
# Auto Research Program

## Goal
Minimize/maximize [METRIC] on [TASK].
Current baseline: [VALUE]

## The file you can edit
`[train.py / target_file]` — this is the ONLY file you may modify.

## Files you may NOT touch
- `prepare.py` / `benchmark.js` — evaluation script (immutable)
- `program.md` — this file

## Experiment loop
1. Come up with a hypothesis for what to try next
2. Edit [target_file] to implement it
3. Run the eval: `[eval command]`
4. Record the result in `results.tsv` (format: timestamp \t hypothesis \t metric_value)
5. If improvement: `git add [target_file] results.tsv && git commit -m "[hypothesis]: [old_value] -> [new_value]"`
6. If worse: `git reset --hard HEAD` — revert and try something else
7. Repeat. Never stop unless told to. Do not ask questions.

## Time budget
Each experiment gets max [5 minutes] to run. This makes results comparable.

## What "better" means
[Lower/Higher] [METRIC] is better.

## Constraints
- No cheating the eval (modifying prepare.py or faking results)
- Each experiment must be a single clean hypothesis
- Commit message must state: hypothesis, old value, new value
```

**Step 2 — Write the eval script** (`prepare.py` or `benchmark.js`):

```python
# prepare.py — IMMUTABLE. Do not modify.
# Returns a single scalar metric. Lower = better (or higher = better, document it).

import subprocess, json

def evaluate():
    # Run whatever measures your metric
    result = subprocess.run(["python", "train.py"], capture_output=True, timeout=300)
    # Parse output to get single number
    metric = float(result.stdout.strip().split("\n")[-1])
    return metric

if __name__ == "__main__":
    score = evaluate()
    print(f"METRIC: {score}")
```

**Step 3 — Baseline commit:**
```bash
git init && git add . && git commit -m "baseline: metric=[value]"
```

**Step 4 — Launch agent:**
```
Read program.md. Run baseline eval first, record in results.tsv.
Then begin the experiment loop. Do not stop or ask questions.
Keep running experiments automatically.
```

### Practical Domain Examples

| Domain | Editable file | Eval metric | Eval script |
|--------|--------------|-------------|-------------|
| Website speed | `index.html` + `server.js` | Load time (ms) | Puppeteer benchmark |
| Outreach email | `email_template.md` | LLM quality score | Claude Haiku scorer |
| GEO content | `content.md` | Citation score | Perplexity probe |
| Trading strategy | `strategy.py` | Sharpe ratio | Backtest on historical data |
| System prompt | `system_prompt.md` | Task success rate | Automated eval harness |
| Model training | `train.py` | Val loss | Training run (5-min budget) |
| SME diagnostic | `problem_structurer_prompt.md` | Haiku quality score | Mode 1 scorer |

### When Karpathy Loop Fails

- **Subjective quality** — UX, brand design, pricing feel: loop has no ground truth
- **Slow eval** (>30 min) — iterations take too long, not worth automating
- **No baseline** — can't measure improvement without a starting point
- **Bad metric** — agent will confidently optimize the wrong thing

---

## Mode Selection Guide

| Situation | Use |
|-----------|-----|
| Writing GEO content, emails, reports | Mode 1 (content loop) |
| Optimizing code performance | Mode 2 (git loop) |
| Fine-tuning a system prompt | Mode 2 (git loop) |
| Improving LangGraph pipeline quality | Mode 1 (content loop) |
| Website speed / load time | Mode 2 (git loop) |
| SME diagnostic slide quality | Mode 1 (content loop) |
| Any text with LLM quality bar | Mode 1 (content loop) |
| Any artifact with numeric metric | Mode 2 (git loop) |

---

## Tuning (Mode 1)

| Parameter | Default | When to change |
|-----------|---------|----------------|
| `MAX_ITERATIONS` | 8 | Lower (3-4) for emails; higher (10-12) for research |
| `SCORE_THRESHOLD` | 7.5 | Raise to 8.5 for high-stakes; lower to 6.5 to cut cost |
| `SCORER_MODEL` | Haiku | Never change |
| `GENERATOR_MODEL` | Sonnet | Use Opus for complex strategic content |
| `dimensions` | relevance, specificity, actionability | Customize per task (see below) |

### Custom Scoring Dimensions

```python
# Emails
dimensions = ["relevance", "personalization", "persuasiveness", "tone"]

# Research summaries
dimensions = ["accuracy", "completeness", "clarity", "evidence_quality"]

# GEO content
dimensions = ["citability", "specificity", "authority", "keyword_density"]

# Business recommendations
dimensions = ["relevance", "feasibility", "impact", "specificity"]
```

---

## Current Usage in Keonhee's Projects

| Project | File | Mode | Iterations | Threshold |
|---------|------|------|-----------|-----------|
| SME Diagnostic AI | `projects/sme-diagnostic-ai/agents/autoresearch.py` | 1 | 8 | 7.5 |
| Lead Intelligence | `projects/lead-intelligence/outreach_generator.py` | 1 | 3 | 7.5 |

---

## Cost Estimate (Mode 1)

Haiku scoring: ~$0.0003/iteration/item
Sonnet generation: ~$0.003/iteration/item
8 iterations, 10 items: ~$0.03 per full run

## Cost Estimate (Mode 2)

Depends entirely on eval runtime and number of experiments.
Typical: 100 experiments overnight = ~$5-20 in agent tokens (mostly cheap models).
