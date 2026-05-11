---
description: Run nightly evolution loop across all 5 Service A products + Service V + Service W + Hagwon Stack (8 strands total). Reads service state, applies 1 improvement per strand, commits if green.
---

# /evolve

Run the nightly autonomous evolution loop. Each strand picks one improvement from its menu, applies it, and commits if tests pass.

## Step 1: Run the data collector

```python
import subprocess, sys
result = subprocess.run(
    [sys.executable, "agents/evolution_loop/evolve.py"],
    cwd="C:/Users/keonh/Dev/MCP_Agentic_AI",
    capture_output=False,
    text=True
)
```

If the script is not runnable (permission or path issue), execute each strand manually:

```python
import sys
sys.path.insert(0, "C:/Users/keonh/Dev/MCP_Agentic_AI/agents/evolution_loop")
from pathlib import Path
DATA_DIR = Path("C:/Users/keonh/Dev/MCP_Agentic_AI/agents/evolution_loop/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

from strands import speed_to_lead, automation_workflows, saas_integrations, pipa_tier_p, geo_seo_blog, service_v, service_w, hagwon_stack

results = {}
for name, fn in [
    ("speed_to_lead", speed_to_lead.run),
    ("automation_workflows", automation_workflows.run),
    ("saas_integrations", saas_integrations.run),
    ("pipa_tier_p", pipa_tier_p.run),
    ("geo_seo_blog", geo_seo_blog.run),
    ("service_v", service_v.run),
    ("service_w", service_w.run),
    ("hagwon_stack", hagwon_stack.run),
]:
    results[name] = fn(DATA_DIR)
    print(f"{name}: {results[name].get('summary', results[name])}")
```

## Step 2: Read the output JSON

After the script runs, read:
`agents/evolution_loop/data/evolution_<today's date>.json`

Report what each strand did:
- improvement_type
- summary
- tests_passed
- committed
- flag_for_report (anything flagged = mention explicitly)

## Step 3: Flag items

Items where `flag_for_report: true` need attention:
- PIPC news with action_required: true
- Kakao changelog with action_required: true
- SaaS breaking changes
- Service V changelog (always report - pre-launch tracking)

Print a clean summary to chat. Format:

```
Evolution ran: <date>

[Speed-to-Lead] <summary> (<status>)
[Automation Workflows] <summary> (<status>)
[SaaS Integrations] <summary> (<status>)
[PIPA Tier P] <summary> (<status>)
[GEO/SEO Blog] <summary> (<status>)
[Service V] <summary> (<status>)
[Service W] <summary> (<status>)
[Hagwon Stack] <summary> (<status>)

Flagged items requiring your attention:
- <list only if flag_for_report=true>
```

## Notes
- Idempotent: running twice same night = no-op on second run
- Budget: max 6 file changes per strand
- proposal-template.md and pricing.md are NEVER modified by evolution (v2-locked)
- If tests fail for any strand, the improvement is NOT committed (data file still written for report)
