# Claude Code Agent Teams — Keonhee's Implementation Playbook

_Enabled: 2026-03-25. Feature flag: `CLAUDE_CODE_ENABLE_AGENT_TEAMS=1` in `.claude/settings.local.json`_

---

## What Agent Teams Are (vs. Sub-Agents)

| | Sub-Agents | Agent Teams |
|---|---|---|
| Communication | Reports back to main session | Direct peer-to-peer messaging |
| Execution | Sequential (one at a time) | Parallel |
| Shared state | No | Shared task list |
| Best for | Single focused tasks | Multi-role, interdependent work |

---

## TMUX Assessment — You Don't Need It

**Conclusion: Skip tmux. VS Code is sufficient.**

Tmux is a terminal multiplexer that splits your terminal into panes so you can watch multiple agent sessions simultaneously. The use case in the video:
- Watch all agents "thinking" in real-time in split panes
- Manually `message` individual sub-agents from the terminal

**Why you don't need it:**
- You work entirely in VS Code, which already surfaces agent updates inline
- You're on Windows — tmux is a Linux/Mac tool. The Windows equivalent (Windows Terminal with split panes) works but adds complexity for minimal gain
- Your projects are small enough (3-4 agents max) that you don't need a dedicated monitoring setup
- If you ever want visibility, `wt` (Windows Terminal) split panes can replicate this without installing anything

**Verdict:** Tmux = nice-to-have for power users on Mac/Linux running 5+ agents. Not worth your time right now.

---

## Team Size Assessment

**Recommended cap: 3 agents per pipeline.**

Your projects are focused, not sprawling. Here's why 3 beats 5:

- Each active agent = a full parallel Claude session = token cost multiplied
- Your pipelines already have well-defined sequential nodes (LangGraph pattern)
- The value-add of agent teams for your work is the **Researcher + Analyst + Critic** triangle
- Adding a 4th or 5th agent would require inventing roles that don't add quality

Use 5 agents only for a full-stack build (Frontend + Backend + DB + QA + Orchestrator).

---

## Implementation: GEO Agency Agent Team

### Goal
Produce a higher-quality GEO audit by having specialized agents audit in parallel, then have a Critic synthesize inconsistencies before the report is generated.

### File Territories (strict ownership)

| Agent | Role | Files it OWNS |
|---|---|---|
| Auditor | Runs geo_audit.py, scores all 10 dimensions | `geo_audit.py`, `audit_output.json` |
| Researcher | Runs before_after.py, pulls Perplexity evidence | `before_after.py`, `evidence_output.json` |
| Critic | Cross-references Auditor + Researcher findings, flags gaps | `critique_output.json` |
| Reporter | Generates final PDF + kit, only after Critic approves | `geo_report_pdf.py`, `geo_deliverables.py`, final PDFs |

### Prompt Template

```
GOAL: Produce a complete, high-quality GEO audit for a Korean SME website.

Team:
- Auditor (Sonnet): You own geo_audit.py and audit_output.json. Run the 10-dimension audit for the target URL and save results to audit_output.json. When done, message the Critic.
- Researcher (Sonnet): You own before_after.py and evidence_output.json. Run the before/after citation analysis and save to evidence_output.json. When done, message the Critic.
- Critic (Sonnet): You own critique_output.json. Wait for messages from both Auditor and Researcher. Cross-reference their outputs — flag any inconsistencies (e.g. high brand score but no Perplexity citations found). Save critique to critique_output.json. Message the Reporter when approved.
- Reporter (Haiku): You own geo_report_pdf.py and geo_deliverables.py. Wait for the Critic's approval. Generate the final PDF report and implementation kit. Do not start until Critic messages you.

Target URL: [URL]
Company name: [NAME]

Auditor and Researcher start simultaneously. Do not modify each other's files.
```

### Team size: 4 (justified — Reporter is Haiku so cost is low)

---

## Implementation: SME Diagnostic AI Agent Team

### Goal
Upgrade the 4-node LangGraph pipeline into a team where Benchmark Research and Autoresearch run in parallel, with a Critic reviewing quality before deck generation.

### File Territories

| Agent | Role | Files it OWNS |
|---|---|---|
| Structurer | Structures the problem (Node 1) | `agents/problem_structurer.py`, `state_structured.json` |
| Benchmarker | Pulls industry benchmarks (Node 2) | `agents/benchmark_research.py`, `state_benchmarks.json` |
| Researcher | Autoresearch loop, scores + improves (Node 3) | `agents/autoresearch.py`, `state_research.json` |
| Deck Generator | Builds final 12-slide deck (Node 4) | `output/deck_generator.py`, final `.pptx` |

**Note:** For this pipeline, the LangGraph graph already handles orchestration. Agent teams add value at the **quality gate** — add a 3-agent version (Benchmarker + Researcher run in parallel, Deck Generator waits for both).

### Simplified 3-Agent Prompt

```
GOAL: Generate a high-quality SME diagnostic deck for a Korean business.

Business context: [REVENUE] KRW revenue, [EMPLOYEES] employees, [INDUSTRY] industry, founded [YEAR].
Problem statement: [PROBLEM]

Team:
- Benchmarker (Sonnet): You own agents/benchmark_research.py and state_benchmarks.json. Research industry benchmarks for this business using Perplexity. Save to state_benchmarks.json. Message DeckGenerator when done.
- Researcher (Haiku): You own agents/autoresearch.py and state_research.json. Run the autoresearch loop (max 8 iterations, threshold 7.5) on the problem. Save best output to state_research.json. Message DeckGenerator when done.
- DeckGenerator (Sonnet): You own output/deck_generator.py and all .pptx files. Wait for messages from both Benchmarker and Researcher. Read both JSON files and generate the 12-slide deck. Do not start early.

Benchmarker and Researcher start simultaneously.
```

### Team size: 3

---

## When to Use Agent Teams vs. Sub-Agents (Decision Rule)

```
Is the task multi-role AND do agents need to react to each other's output?
├── YES → Agent Team
│   ├── GEO audit (Auditor + Researcher + Critic + Reporter)
│   ├── SME Diagnostic (Benchmarker + Researcher + DeckGenerator)
│   └── Full-stack build (Frontend + Backend + QA)
└── NO → Sub-Agent (current approach)
    ├── Single research task
    ├── Writing a cover letter
    ├── Notion CRUD
    └── Code review
```

---

## Enabling / Disabling

**Already enabled.** Flag is in `.claude/settings.local.json`.

To disable: remove or set `"CLAUDE_CODE_ENABLE_AGENT_TEAMS": "0"`.

---

## Cost Warning

Each active agent = a full parallel token stream. A 4-agent team running Sonnet costs ~4x a single session. Use Haiku for non-reasoning roles (Reporter, DeckGenerator) to cut costs.

Rule of thumb: If total agent-minutes > 10, switch non-critical agents to Haiku.
