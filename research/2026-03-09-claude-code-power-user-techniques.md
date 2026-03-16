# Claude Code Power User Techniques — 2026
_Research date: 2026-03-09_
_Queries: Claude Code advanced features, hook patterns, underused capabilities_

---

## Key Findings

### CLAUDE.md Best Practices
- Include: project overview, tech stack, style rules, avoided patterns
- Update periodically — pair with context files for per-session alignment
- Develop workflows first, document in CLAUDE.md before scaling to skills

### Hook Patterns (Power User Patterns)
- **Prefer `updatedInput` over blocking** — silently corrects tool inputs without generating errors to Claude
- **Block-at-Submit pattern** — validate at UserPromptSubmit or pre-commit, not mid-flow
- **Scope hooks narrowly** — `Edit|Write|MultiEdit` not broad categories, reduces false positives
- **PostToolUse for auto-formatting** — use `|| true` for graceful degradation if formatter missing
- **Minimal hooks = stability** — fewer hooks reduce context bloat

### Agent Subagent Orchestration
- Treat Claude as pair programmer: detailed specs first, then build
- Incremental development (homepage → login → sidebar) for context reliability in long sessions
- Skills for recurring tasks > one-off prompts
- Selective context activation per project — not global enables

### Underused Features (Confirmed)
- **Automatic sub-agents for codebase analysis** — spins up without manual setup
- **Built-in clarifying questions** — post-analysis, 3-5 targeted questions for iterative refinement
- **Plan mode + incremental scaffolding** — handles Git, CI/CD integration
- **Image + PDF input** — document handling, not widely used by devs

### Power User Techniques Most Miss
- `updatedInput` in hooks for invisible fixes
- End-of-plan validation (not mid-plan interrupts)
- Spec shaping via Q&A before build — boosts code gen success to ~90%+
- Regular `/context` reviews to prune bloat
- Write skills only when used 3+ times (not prematurely)

### Best MCP Servers for Productivity (2026)
- **Notion** — already connected ✅
- **GitHub** — pending Node.js install
- **Slack** — team communications (solo operator — lower priority)
- **Google Drive** — potential, listed in CLAUDE.md

---

## Actionable Gaps in Current System

| Gap | Action |
|-----|--------|
| `updatedInput` hook pattern not implemented | Consider updating .env protection hook to use `updatedInput` instead of stderr warning |
| No `/compact` or `/cost` tracking | Add these as quick references in session workflow SOP |
| Spec-first Q&A pattern not enforced | Add to CLAUDE.md Workflow Rules: "For new features, ask 3 clarifying questions before building" |
| No progressive disclosure in skills | Large skills (financial-analyst, data-analyst) could split main + helper files |

---

## Sources
- Perplexity sonar search — Claude Code features, early 2026
- Ryan Lewis hook pattern recommendations
- Anthropic Claude Code VS Code 1.109 release notes
