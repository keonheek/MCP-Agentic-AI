# Evolution Loop

Nightly autonomous improvement system. Runs at 2:00am KST while Keonhee sleeps.

Reads state of Service A (5 products) and Service V. Applies 1 improvement per strand.
Commits if tests pass. Pushes Telegram morning report at 7am.

## Architecture

```
2:00am KST (cron 7 2 * * *)
  python agents/evolution_loop/evolve.py
    strands/speed_to_lead.py       -> 1 improvement
    strands/automation_workflows.py -> 1 improvement
    strands/saas_integrations.py   -> 1 improvement
    strands/pipa_tier_p.py         -> 1 improvement
    strands/geo_seo_blog.py        -> 1 improvement
    strands/service_v.py           -> 1 improvement (pre-launch tracking)
  writes: data/evolution_YYYY-MM-DD.json

7:00am KST (cron 13 7 * * *)
  /evolve-report slash command in Claude Code
    reads: data/evolution_YYYY-MM-DD.json
    pushes: Telegram morning summary
```

## Zero API cost

All strands use pre-researched static data banks. No LLM calls, no external APIs.
Synthesis happens in the /evolve and /evolve-report slash commands (in-session).

## Idempotency

Running evolve.py twice on the same night = no-op on second run.
Each strand checks `last_run_date` in its state file before running.

## Budget

Max 6 file changes per strand per night. No runaway commits.

## Protected files

proposal-template.md and pricing.md are NEVER modified by evolution strands.
They are v2-locked. Changes require manual intervention.

## Cron schedule

| Command | Cron | Time (KST) |
|---|---|---|
| python agents/evolution_loop/evolve.py | 7 2 * * * | 2:07am KST |
| /evolve-report | 13 7 * * * | 7:13am KST |

## Run manually

```
cd C:/Users/keonh/Dev/MCP_Agentic_AI
python agents/evolution_loop/evolve.py
```

## Data files written

```
agents/evolution_loop/data/
  evolution_YYYY-MM-DD.json       # master output per night
  strand_state_*.json             # per-strand state (last_run_date, last_improvement)
  pipa_audit_metrics.json         # accumulated PIPA metrics
  kakao_changelog_log.json        # Kakao API notes
  kakao_variants_log.json         # A/B test variants
  e2e_edge_cases_log.json         # automation edge cases
  automation_backlog.json         # flow concept stubs
  platform_changelog_log.json     # SaaS platform API notes
  error_handlers_log.json         # error handler specs
  pipc_news_log.json              # PIPC regulatory news
  pipa_case_studies.json          # breach case studies
  pipa_edge_case_patches.json     # src patch specs
  brand_scan_log.json             # GEO brand scores
  keyword_bank.json               # GEO keyword bank
  query_shift_log.json            # AI query shift observations
  geo_schema_patterns.json        # GEO schema templates
  service_v_changelog_log.json    # V stack tool changelogs
  service_v_ad_observations.json  # Korean ad research
```
