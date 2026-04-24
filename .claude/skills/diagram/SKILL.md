# Skill: diagram

Auto-generate a business-style Mermaid flowchart from any prose description, topic, or file path. Output is saved directly to `references/diagrams/` following the 5-principle style guide in `_HOW_TO_CRAFT.md`.

## Trigger

Invoked via `/diagram <input>`. Also callable inline: "create a diagram for X", "draw the flowchart for X".

---

## Execution steps

### Step 1 — Load the style guide
Read `references/diagrams/_HOW_TO_CRAFT.md` in full. Internalize:
- The 5 legibility principles (one verb per node, LR for pipelines, max 9 nodes, color = state, 3-line caption)
- The approved color legend (green = built/done, yellow = in-progress, red = blocked/not-started, blue = human step, gray = AI/automated)
- The 3 Mermaid templates (Pipeline LR, Branching TB, Sequence)

### Step 2 — Understand the input
Parse what the user gave:
- If a **file path** → read the file, extract the process or system it describes
- If **prose** → treat it as the process description directly
- If a **topic keyword** (e.g. "SDIC session flow") → infer from context files

Ask one clarifying question ONLY if audience and question are both completely unknown. Otherwise infer from context:
- Keonhee talking to 영범 → AUDIENCE: 영범
- SDIC teaching context → AUDIENCE: SDIC 멤버
- Client / pitch deck → AUDIENCE: Client
- Personal planning → AUDIENCE: 나

### Step 3 — Generate the diagram
Choose the right template:
- Linear process → `flowchart LR`
- Decision / branching → `flowchart TB` with `{diamond}`
- Who-does-what timing → `sequenceDiagram`

Apply these rules without exception:
- One verb per node (no noun-only labels)
- Max 9 nodes — if more are needed, split into Overview + Zoom-in
- Color every node using the approved `classDef` color legend
- Use `subgraph` to group related nodes when the diagram has 6+ nodes

Write the full Mermaid block including `classDef` declarations at the bottom.

### Step 4 — Self-validate
Before writing the file, check each of the 5 principles explicitly:
1. Every node label starts with a verb? (Fix any that don't)
2. Direction is consistent (LR or TB, not mixed)?
3. Node count ≤ 9? (If over, split)
4. Every node has a color from the legend?
5. The 3-line header is present?

If any check fails, fix it before proceeding.

### Step 5 — Derive the filename and write
- Filename: `references/diagrams/<topic-slug>.md` (lowercase, hyphens, max 4 words)
- Examples: `sdic-onboarding-flow.md`, `youtube-short-pipeline.md`, `finagent-architecture.md`
- Do NOT overwrite an existing file with the same name — append a suffix: `-v2`, `-v3`

File format:
```
# <Title>

_<one-sentence description of when to use this diagram>_

---

## <Diagram title>

```
AUDIENCE: <who>
QUESTION: <the one question this answers>
STATUS: draft
```

```mermaid
<generated diagram>
```

**Use this for:** <2-3 specific situations where this diagram is useful>
```

### Step 6 — Update the file index
Append a new row to the file index table at the bottom of `references/diagrams/_WHERE_TO_RENDER.md`:
```
| `<filename>.md` | <one-line use case> |
```

Also confirm the entry appears in the File Index section of `_HOW_TO_CRAFT.md` if it is not already listed.

### Step 7 — Report back
Tell Keonhee:
- The file path created
- How to preview: "Open in VS Code — Mermaid preview renders inline"
- Whether to export: "Use mermaid.live if you need a PNG/SVG — paste the code block"
- Any principle violations found and fixed in Step 4

---

## Rules
- Never produce a diagram with node labels that are nouns only
- Never produce a diagram with more than 9 nodes without splitting
- Never skip the 3-line header
- Never write to a location other than `references/diagrams/`
- STATUS starts as `draft` — Keonhee upgrades it to `agreed with partner` or `final`
- Do NOT open a browser, render PNG, or call any MCP — the output is raw Mermaid markdown only