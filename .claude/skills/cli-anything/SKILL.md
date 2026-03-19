---
name: cli-anything
description: Turn any GUI app, desktop tool, SDK, or web/API surface into a structured agent-usable CLI harness. Use when the user wants to make software agent-native, wrap an existing tool for Claude Code, or build a CLI harness for a new target. Original methodology from CLI-Anything project.
---

# CLI-Anything

Turn any software into an agent-usable CLI. The methodology wraps GUI apps, SDKs, and APIs into structured command-line harnesses that Claude Code can reliably invoke.

**Original:** [CLI-Anything project](https://github.com/anthropics/cli-anything) — methodology for building agent-native CLI harnesses
**Adapted for:** Claude Code (standalone, no OpenClaw dependency)

## When to Use

- User wants to make a GUI app or desktop tool agent-accessible
- User wants to wrap an existing SDK or API as a structured CLI
- User wants to build an agent-native harness for a new software target
- User asks "make X work with Claude Code" where X is a tool without a good CLI

**NOT for:** Tools that already have robust CLIs (git, npm, etc.). Just use them directly.

---

## Core Concept

An **agent harness** is a thin Python CLI wrapper around a target tool that:
1. Exposes structured command groups (not a blob of flags)
2. Returns JSON output for agent parsing
3. Has a TEST.md for verifying the harness works
4. Is installable to PATH via `pip install -e .`

---

## Workflow

### 1. Classify the request

| Request type | Action |
|-------------|--------|
| Make X agent-native | Build a new harness for X |
| Use an existing harness | Locate and validate the harness |
| Understand the methodology | Explain the pattern, show examples |

### 2. Assess feasibility

Before promising a harness, check:
- Does the target have a Python API, REST API, or GUI automation hooks?
- Is the backend software available locally?
- Is there an existing harness to extend instead of building from scratch?

### 3. Analyze the target

For a new harness:
1. Understand the backend engine and data model
2. Identify existing CLI/API hooks
3. Map the logical command groups (what operations does a user want?)
4. Define the state model (what state persists between commands?)

### 4. Build the harness structure

```
{software}/
+-- agent-harness/
    +-- setup.py              # pip install -e .
    +-- {software}_cli/
    |   +-- __init__.py
    |   +-- main.py           # CLI entry point (Click or Typer)
    |   +-- commands/
    |       +-- group1.py
    |       +-- group2.py
    +-- TEST.md               # Verification steps
    +-- README.md             # Usage for agents
```

### 5. CLI design rules

- **Command groups** map to logical domains, not implementation details
- **JSON output** for all commands: `{"status": "ok", "data": {...}}`
- **Error output** on stderr, structured: `{"status": "error", "message": "..."}`
- **No interactive prompts** — agents can't respond to them
- **Idempotent reads** — list/get commands should never modify state
- **Explicit writes** — mutation commands require explicit flags

### 6. Entry point pattern

```python
# main.py
import click
import json

@click.group()
def cli():
    """Agent harness for {software}."""
    pass

@cli.command()
@click.option('--output', default='json', help='Output format')
def list_items(output):
    """List all items."""
    try:
        # ... implementation
        result = {"status": "ok", "data": items}
        click.echo(json.dumps(result))
    except Exception as e:
        import sys
        click.echo(json.dumps({"status": "error", "message": str(e)}), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    cli()
```

### 7. setup.py pattern

```python
from setuptools import setup, find_packages

setup(
    name="{software}-agent-harness",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["click", "{software-sdk}"],
    entry_points={
        "console_scripts": [
            "{software}=software_cli.main:cli",
        ],
    },
)
```

### 8. TEST.md pattern

```markdown
# Harness Test

## Prerequisites
- Python 3.10+
- {software} installed and accessible
- `pip install -e .` run from agent-harness/

## Smoke Tests

Run these in order. Each should return JSON with "status": "ok".

1. List: `{software} list-items`
2. Get: `{software} get-item --id 1`
3. Create: `{software} create-item --name "test"`
4. Delete: `{software} delete-item --id <id from create>`
```

---

## Adaptation for Keonhee's Stack

For tools commonly used in your projects:

| Target | Command groups to build |
|--------|------------------------|
| DART API | search, financials, disclosures, company-info |
| Streamlit Cloud | deploy, status, reboot, secrets |
| AWS Lambda | deploy, invoke, logs, status |
| Notion | pages, databases, search, blocks |

---

## Rules

- Do not claim a harness works until the TEST.md steps pass on real backend
- No mock-only testing — agents will call real commands in production
- Keep harnesses thin — they wrap, they don't reimplement
- If the target already has a good CLI, don't build a harness; just document it
