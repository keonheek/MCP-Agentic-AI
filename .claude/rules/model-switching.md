# Model Switching Rules

## Plan Mode
When entering plan mode (`/plan`, EnterPlanMode, or any architectural planning session):
- Command: `/model opus`
- Effort: high
- Extended thinking: OFF (no bracket)
- Opus without extended thinking > Sonnet with extended thinking for planning quality

## Hard Architectural Decisions Only
For genuinely complex problems with no obvious answer:
- Command: `/model opus[1m]`
- Use for 1-2 messages max, then switch back to `/model opus`
- WARNING: `[1m]` = 1 million thinking token budget per request. Burns rate limit fast.

## Execution Mode
When executing a plan (bypass permissions, implementation, file writes, code changes):
- Command: `/model default` (Sonnet 4.6)
- Effort: standard
- Extended thinking: OFF

## Key Clarification
- `[1m]` is the extended thinking token budget, NOT the context window
- Context window is 200K for all models (fixed)
- Rate limits are account-level — hitting the limit on `opus[1m]` means ALL Opus requests are blocked until cooldown
- If rate-limited, wait 2-3 min — restarting VS Code does not help

## Rationale
Opus for planning = better architectural decisions, catches edge cases, avoids costly replanning.
Sonnet for execution = faster, cheaper, sufficient for following a clear spec.
