# AI Engineering — LLM Evaluation with RAGAS
_Track 1 | Week: LLM Evals | Date: 2026-03-24_

---

## Concept (10 min read)

### What is RAGAS?

RAGAS (Retrieval Augmented Generation Assessment) is a framework for evaluating RAG pipelines without human-labeled ground truth. It computes reference-free metrics using LLMs to judge output quality across four dimensions.

You built a RAG pipeline in FinAgent: `text-embedding-3-small` embeds chunks → cosine similarity retrieves top-k → GPT-4o answers. RAGAS tells you how good that pipeline actually is, beyond "it seems to work."

### Why it matters

Before RAGAS, evaluating RAG meant either:
- Human review (slow, expensive, subjective)
- BLEU/ROUGE (word overlap — useless for generative answers)

RAGAS uses LLMs to evaluate LLM outputs — a scalable proxy for human judgment.

### The four core metrics

**1. Faithfulness**
Does the answer stick to what the retrieved context actually says?
- Extracts claims from the answer
- Checks each claim against the context
- Score = (claims supported by context) / (total claims)
- Low score = hallucination

**2. Answer Relevance**
Does the answer actually address the question?
- Generates synthetic questions from the answer
- Measures similarity between synthetic questions and the original
- Low score = answer is on-topic but doesn't answer the question

**3. Context Recall**
Did retrieval fetch everything needed to answer the question?
- Requires a `ground_truth` answer
- Checks how much of the ground truth can be attributed to retrieved context
- Low score = retriever is missing relevant chunks

**4. Context Precision**
Are the retrieved chunks actually useful, or is there noise?
- Measures signal-to-noise ratio of retrieved context
- High score = top-k chunks are all relevant
- Low score = retriever is pulling irrelevant documents

### How it connects to your FinAgent RAG

Your FinAgent retrieves Samsung financial data chunks, then GPT-4o answers analyst queries. The failure modes RAGAS catches:
- Faithfulness failure: GPT-4o invents a revenue figure not in the retrieved chunks
- Context Recall failure: the right chunk (e.g., Q3 operating profit) wasn't retrieved
- Answer Relevance failure: the answer discusses margins when the question was about cash flow

### Reference-free vs. reference-based

Context Recall needs `ground_truth` (a reference answer). The other three metrics are reference-free — you only need the question, answer, and retrieved contexts. In practice, you can evaluate faithfulness and answer relevance on live queries with zero labeling effort.

---

## Key Terms

- **RAGAS**: Framework for reference-free RAG evaluation using LLM-as-judge methodology
- **Faithfulness**: Metric measuring whether answer claims are grounded in retrieved context (0-1, higher is better)
- **Answer Relevance**: Metric measuring whether the answer addresses the original question (0-1)
- **Context Recall**: Metric measuring retriever completeness — requires ground truth (0-1)
- **Context Precision**: Metric measuring retriever precision — ratio of useful to noisy chunks (0-1)
- **LLM-as-judge**: Pattern where an LLM evaluates another LLM's output, used as a scalable proxy for human review
- **Evaluation dataset**: A set of (question, answer, contexts, ground_truth) tuples used as input to RAGAS

---

## Working Code (implementable in 20 min)

This runs standalone using sample FinAgent-style data. No pipeline connection needed to start — swap in real retrieval output later.

```python
# ragas_eval.py
# Evaluates a RAG pipeline using RAGAS metrics
# Requires: pip install ragas openai datasets

import os
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
)

# --- Config ---
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "your-key-here")

# --- Sample data (FinAgent-style Samsung financial queries) ---
# In production: replace with real (query, answer, retrieved_chunks, ground_truth)
eval_data = {
    "question": [
        "What was Samsung's revenue in 2023?",
        "How did Samsung's operating profit change from 2022 to 2023?",
        "What is Samsung's main business segment by revenue?",
    ],
    "answer": [
        "Samsung's revenue in 2023 was approximately 258.9 trillion KRW, a decline from the prior year due to weak semiconductor demand.",
        "Samsung's operating profit dropped sharply from 43.4 trillion KRW in 2022 to 6.6 trillion KRW in 2023, primarily due to the memory chip downcycle.",
        "The Device Solutions (DS) division, which includes semiconductors, is Samsung's largest segment. It accounted for the majority of revenue in peak years.",
    ],
    "contexts": [
        # Each entry is a list of retrieved chunk strings
        [
            "Samsung Electronics reported consolidated revenue of 258.94 trillion KRW for fiscal year 2023.",
            "Revenue declined year-over-year as the global semiconductor market experienced a prolonged downturn.",
            "The DX division (MX + VD/DA) maintained relatively stable revenue compared to DS.",
        ],
        [
            "Operating profit for FY2023 was 6.57 trillion KRW, down from 43.38 trillion KRW in FY2022.",
            "The memory semiconductor business was the primary driver of the profit decline.",
            "DRAM and NAND flash prices fell significantly through H1 2023 before partially recovering.",
        ],
        [
            "Samsung's Device Solutions division includes DRAM, NAND, and System LSI.",
            "In FY2023, DS revenue was lower than historical peak due to chip oversupply.",
            "The DX division (smartphones, TVs, appliances) provides more stable revenue.",
        ],
    ],
    "ground_truth": [
        "Samsung's 2023 revenue was 258.94 trillion KRW.",
        "Operating profit fell from 43.38 trillion KRW in 2022 to 6.57 trillion KRW in 2023.",
        "Samsung's DS (Device Solutions) division, covering semiconductors, is the largest segment by revenue in strong years.",
    ],
}

# --- Build HuggingFace Dataset (RAGAS input format) ---
dataset = Dataset.from_dict(eval_data)

# --- Run evaluation ---
# context_recall and context_precision require ground_truth
# faithfulness and answer_relevancy are reference-free
result = evaluate(
    dataset=dataset,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_recall,
        context_precision,
    ],
)

# --- Print results ---
print("\n=== RAGAS Evaluation Results ===")
df = result.to_pandas()
print(df[["question", "faithfulness", "answer_relevancy", "context_recall", "context_precision"]].to_string())

print("\n=== Aggregate Scores ===")
for metric in ["faithfulness", "answer_relevancy", "context_recall", "context_precision"]:
    print(f"{metric}: {df[metric].mean():.3f}")
```

**Installation:**
```bash
pip install ragas datasets openai
```

**Expected output structure:**
```
=== RAGAS Evaluation Results ===
   question                              faithfulness  answer_relevancy  context_recall  context_precision
0  What was Samsung's revenue...         0.95          0.88              1.00            0.92
1  How did operating profit change...    1.00          0.91              1.00            0.95
2  What is Samsung's main segment...     0.80          0.85              0.85            0.78

=== Aggregate Scores ===
faithfulness: 0.917
answer_relevancy: 0.880
context_recall: 0.950
context_precision: 0.883
```

Note: RAGAS uses GPT-4o internally to judge outputs. Each `evaluate()` call makes multiple API calls — budget ~15-20 calls for 3 samples.

---

## Exercises

**1. Evaluate your actual FinAgent RAG output**

Connect RAGAS to your real pipeline. In `FinAgent/`, your RAG query function returns an answer and retrieved chunks. Capture 5-10 real query/answer pairs and run them through RAGAS.

Steps:
- Run 5 FinAgent queries manually
- Save each as `(question, answer, contexts)` — contexts = the chunk strings your VectorDB returned
- Write 5 `ground_truth` entries yourself (this is the only manual step)
- Run `evaluate()` and find the weakest metric

Target: identify whether your FinAgent bottleneck is retrieval quality (context_recall) or generation quality (faithfulness).

**2. Diagnose a low-faithfulness answer**

Intentionally create a failure case:
- Modify one answer in `eval_data` to include a claim NOT in its contexts (e.g., invent a net profit figure)
- Re-run RAGAS and confirm faithfulness drops for that entry
- Inspect `df` to see per-row scores

Goal: understand what faithfulness is actually measuring, not just the aggregate score.

**3. Integrate RAGAS as a pipeline node in SME Diagnostic AI**

In `projects/sme-diagnostic-ai/graph.py`, add an `eval_node` that runs after the answer is generated:

```python
def eval_node(state: AgentState) -> AgentState:
    """Runs RAGAS faithfulness check on the generated report."""
    from datasets import Dataset
    from ragas import evaluate
    from ragas.metrics import faithfulness

    dataset = Dataset.from_dict({
        "question": [state["query"]],
        "answer": [state["report"]],
        "contexts": [state["retrieved_chunks"]],  # add this field to AgentState
        "ground_truth": [state.get("ground_truth", state["report"])],
    })
    result = evaluate(dataset, metrics=[faithfulness])
    state["eval_score"] = result["faithfulness"]
    return state
```

Wire it: `autoresearch_loop` -> `eval_node` -> `deck_generator`. Gate deck generation on `eval_score >= 0.8`.

This turns RAGAS from an offline tool into a live quality gate.

---

## Resources

- Primary: https://docs.ragas.io/en/stable/ — official docs, metric definitions, advanced usage
- Related: https://github.com/explodinggradients/ragas — source code, examples, and the `testset_generation` module (auto-generates eval datasets from your documents)

---

## Cross-apply

**SME Diagnostic AI** — Your autoresearch loop already scores outputs with Claude Haiku and iterates until the score hits 7.5. RAGAS is the same pattern applied to retrieval quality. The eval_node exercise above shows how to gate the deck generator on a faithfulness threshold instead of (or in addition to) the current Haiku scorer.

**Lead Intelligence** — The outreach email pipeline runs 3 iterations with a Haiku quality scorer. Answer relevance from RAGAS is a more principled scorer for emails: does this email actually address what a Korean SME owner cares about? Swap the Haiku scorer for RAGAS answer_relevancy and compare convergence behavior.

**FinAgent** — The most direct target. Your custom VectorDB has no retrieval quality signal. Context precision and context recall give you that signal. Low context precision = too many irrelevant chunks in top-k = GPT-4o gets confused. Fix: tighten similarity threshold or reduce top-k.
