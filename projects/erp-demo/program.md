# Auto Research Program — ERP Demo Import Speed

## Goal
Minimize the import time of `app_optimized.py`, measured by `benchmark.py`.
This is a proxy for cold-start latency — how fast the ERP demo loads on first open.
Faster demo = more credible client presentation.

**Baseline:** Run `python benchmark.py` to get the current metric before starting.

## The ONE file you may edit
`app_optimized.py` — restructure imports, defer heavy loading, remove unused code.
Do NOT modify anything else.

## Files you may NEVER touch
- `benchmark.py` — the eval. Immutable. Do not touch.
- `program.md` — this file.
- `db.py`, `seed.py`, `ai_engine.py`, `pdf_gen.py` — source files. Read-only.
- `pages/` — read-only.

## Experiment loop (repeat forever until told to stop)

1. **Hypothesize** — form one specific hypothesis: "If I make import X lazy, it will reduce load time because X is heavy."
2. **Edit** — apply ONLY that one change to `app_optimized.py`
3. **Eval** — run: `python benchmark.py`
4. **Record** — append to `results.tsv` (tab-separated): `timestamp\thypothesis\tmetric_seconds`
5. **Decide:**
   - If metric improved (lower): `git add app_optimized.py results.tsv && git commit -m "IMPROVE [hypothesis]: [old]s -> [new]s"`
   - If metric stayed same or worsened: `git checkout app_optimized.py` (revert only this file)
6. **Repeat.** Do not stop. Do not ask questions.

## Time budget
Each experiment: run benchmark 3 times (already built into benchmark.py), take median. Max 3 minutes per experiment.

## What "better" means
Lower METRIC value (seconds) is better. Any improvement ≥ 0.005s is worth committing.

## Techniques to try (not exhaustive — be creative)
- Convert top-level imports to lazy imports inside functions
- Use `importlib.import_module()` for optional heavy deps
- Remove imports that are only needed in specific pages (move to page files)
- Use `TYPE_CHECKING` guard for type-only imports
- Cache expensive module-level computations
- Reduce the number of db calls at import time

## Constraints
- `main()` must still be callable and produce the same app behavior
- Do not fake the benchmark (no sleep(), no hardcoded returns)
- Each experiment must be one clean hypothesis — no bundling 5 changes at once
- Commit message format: `IMPROVE [hypothesis]: [old_time]s -> [new_time]s`
- Revert message: handled by git checkout (no commit needed)

## Results format (results.tsv)
```
timestamp	hypothesis	metric_seconds
2026-04-07T10:00:00	baseline	0.842
2026-04-07T10:03:00	lazy import streamlit	0.612
```
