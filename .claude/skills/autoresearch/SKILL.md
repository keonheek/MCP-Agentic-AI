---
name: autoresearch
description: Autonomous self-improving research loop based on Andrej Karpathy's autoresearch pattern. Generates outputs, scores them with a cheap model, improves until threshold met or max iterations reached. Use when building iterative content generation, recommendation scoring, outreach emails, or any task that benefits from automated quality improvement. Trigger phrases: "autoresearch loop", "self-improving", "score and improve", "iterate until good enough".
---

# Autoresearch (Karpathy Pattern)

Autonomous generate -> score -> improve loop. Runs until quality threshold is met or max iterations exhausted. Uses a cheap model (Haiku) for scoring to minimize cost.

**Based on:** Andrej Karpathy's autoresearch pattern — generate, evaluate, improve, repeat
**Implemented in:** `projects/sme-diagnostic-ai/agents/autoresearch.py`, `projects/lead-intelligence/outreach_generator.py`

## When to Use

- Generating content that has a measurable quality bar (emails, recommendations, reports)
- Any task where "good enough on first try" is unlikely
- When you want autonomous improvement without human-in-the-loop per iteration

## Core Loop

```
generate(input)
  -> score(output) using cheap model (Haiku)
  -> if avg_score >= threshold: done
  -> else: improve(output, scores, feedback)
  -> repeat up to max_iterations
```

---

## Standard Implementation

```python
import os
import json
import anthropic

# Cheap model for scoring -- keeps cost low
SCORER_MODEL = "claude-haiku-4-5-20251001"
# Smart model for generation + improvement
GENERATOR_MODEL = "claude-sonnet-4-6"

MAX_ITERATIONS = 8       # Project A (SME Diagnostic): 8
SCORE_THRESHOLD = 7.5    # Out of 10. Stop when avg score >= this


def _score(client: anthropic.Anthropic, content: str, context: str) -> dict:
    """Score content on relevance, specificity, actionability (0-10 each)."""
    prompt = f"""Score this content on three dimensions (0-10 each). Return ONLY valid JSON.

Context: {context}

Content to score:
{content}

Return:
{{
  "relevance": <0-10>,
  "specificity": <0-10>,
  "actionability": <0-10>,
  "feedback": "<one sentence on what to improve>"
}}"""

    resp = client.messages.create(
        model=SCORER_MODEL,
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.splitlines()[1:-1])
    return json.loads(raw)


def _improve(client: anthropic.Anthropic, content: str, scores: dict, context: str) -> str:
    """Generate improved version based on score feedback."""
    prompt = f"""Improve this content based on the feedback below.

Context: {context}
Current scores: relevance={scores['relevance']}/10, specificity={scores['specificity']}/10, actionability={scores['actionability']}/10
Feedback: {scores['feedback']}

Original content:
{content}

Return ONLY the improved content, no explanation."""

    resp = client.messages.create(
        model=GENERATOR_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


def run_autoresearch(
    initial_content: str,
    context: str,
    max_iterations: int = MAX_ITERATIONS,
    threshold: float = SCORE_THRESHOLD,
) -> dict:
    """
    Run the autoresearch loop.

    Returns:
        {
            "final_content": str,
            "final_scores": dict,
            "iteration_count": int,
            "score_history": list
        }
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    content = initial_content
    score_history = []

    for i in range(max_iterations):
        scores = _score(client, content, context)
        avg = (scores["relevance"] + scores["specificity"] + scores["actionability"]) / 3
        scores["avg"] = round(avg, 2)
        score_history.append({"iteration": i + 1, "scores": scores})

        print(f"  Iteration {i+1}: avg={avg:.2f} | feedback: {scores['feedback']}")

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

---

## LangGraph Node Wrapper

To use as a LangGraph node:

```python
def run_autoresearch_node(state: dict) -> dict:
    """LangGraph node. Runs autoresearch loop on state['draft_content']."""
    result = run_autoresearch(
        initial_content=state["draft_content"],
        context=state.get("context", ""),
        max_iterations=state.get("max_iterations", MAX_ITERATIONS),
        threshold=state.get("score_threshold", SCORE_THRESHOLD),
    )
    state["final_content"] = result["final_content"]
    state["final_scores"] = result["final_scores"]
    state["iteration_count"] = result["iteration_count"]
    return state
```

---

## Scoring Dimensions

Adapt these to the task. Current defaults:

| Dimension | What it measures |
|-----------|-----------------|
| Relevance | Does it address the actual context/problem? |
| Specificity | Are claims concrete, not generic? |
| Actionability | Can the reader act on this immediately? |

For emails: add `tone` (0-10) — professional and personalized?
For recommendations: add `impact` (0-10) — expected business impact?
For research summaries: add `evidence_quality` (0-10) — grounded in sources?

---

## Tuning

| Parameter | Default | When to change |
|-----------|---------|----------------|
| `MAX_ITERATIONS` | 8 | Lower (3-4) for emails/simple content; higher (10-12) for research |
| `SCORE_THRESHOLD` | 7.5 | Raise to 8.5 for high-stakes output; lower to 6.5 to cut cost |
| `SCORER_MODEL` | Haiku | Never change -- Haiku is fast and cheap enough |
| `GENERATOR_MODEL` | Sonnet | Use Opus for complex strategic content |

---

## Current Usage in Keonhee's Projects

| Project | File | Iterations | Threshold | Scoring dimensions |
|---------|------|-----------|-----------|-------------------|
| SME Diagnostic AI | `projects/sme-diagnostic-ai/agents/autoresearch.py` | 8 | 7.5 | relevance, specificity, actionability |
| Lead Intelligence | `projects/lead-intelligence/outreach_generator.py` | 3 | 7.5 | relevance, personalization, persuasiveness |

---

## Cost Estimate

Haiku scoring: ~$0.0003 per iteration per item
Sonnet generation: ~$0.003 per iteration per item
8 iterations, 10 items: ~$0.03 per full run -- essentially free
