# Where to Render and Create Diagrams — Cheat-Sheet

_Open this when you need to pick a tool. Use `/diagram` for automatic generation; pick a manual tool below for anything requiring drag-and-drop._

---

## Quick defaults (one line)

- **Auto (code-first):** Run `/diagram` → commit the `.md` → preview in VS Code.
- **Manual whiteboard:** Excalidraw for sketches; draw.io for client-ready output.
- **From prose / AI:** `/diagram` first; Napkin.ai only when it needs to be deck-pretty.

---

## A. Online Mermaid renderers (paste code → image)

| Tool | Free? | Login? | Best for | Export |
|---|---|---|---|---|
| [mermaid.live](https://mermaid.live) | Yes | No | **Default.** Fastest paste-to-PNG/SVG loop; shareable URLs with code embedded | PNG, SVG, URL |
| GitHub native | Yes | No | READMEs, PR descriptions, GitHub issues (renders in-browser) | N/A (inline) |
| Notion `/code mermaid` | Yes | Yes | Embedding live diagrams inside Notion pages | N/A (inline) |
| Obsidian native | Yes | No | Wiki notes, daily journals, jeja tracking | N/A (inline) |
| VS Code Mermaid Preview | Yes | No | Editing `.md` files directly in this repo | PNG (plugin) |
| [Kroki.io](https://kroki.io) | Yes | No | When you also need PlantUML, D2, or Graphviz in the same pipeline | PNG, SVG, PDF |
| [Mermaid Chart](https://www.mermaid-chart.com) | Freemium | Yes | Team version history + AI assist; skip unless sharing with others | PNG, SVG, PDF |

**When to use mermaid.live vs VS Code:**
- Editing in this repo? Use VS Code preview (no tab-switch).
- Sharing a link or exporting a PNG? Use mermaid.live.

---

## B. Manual / GUI creators (drag-and-drop, no code)

| Tool | Free? | Best for | Export | Download |
|---|---|---|---|---|
| [Excalidraw](https://excalidraw.com) | Yes | Hand-drawn aesthetic — YouTube cold-open cards, partner whiteboarding with 영범 | PNG, SVG, JSON | Web (also desktop app) |
| [draw.io / diagrams.net](https://app.diagrams.net) | Yes | **Default for client-ready output.** Professional look, offline capable, no paywall | PNG, SVG, PDF, Visio | Web + desktop |
| [Whimsical](https://whimsical.com) | Freemium | Sticky-note brainstorming with 영범; wireframes | PNG, PDF, JSON | Web |
| [FigJam](https://figma.com/figjam) | Freemium | Real-time collab when a partner is already in Figma | PNG, FigJam file | Web |
| Lucidchart | Paid | Only if a client demands it — draw.io covers the same ground free | PDF, PNG, Visio, CSV | Web |

**Excalidraw vs draw.io — when to pick which:**
| Situation | Tool |
|---|---|
| Cold-open card for a YouTube video (hand-drawn vibe) | Excalidraw |
| Client deliverable or presentation slide (polished) | draw.io |
| Quick whiteboard with 영범 (real-time collab) | Whimsical or Excalidraw |
| Architecture diagram for GitHub README | draw.io → export SVG |

---

## C. AI text-to-diagram (prose → image)

| Tool | Free? | Best for | Notes |
|---|---|---|---|
| `/diagram` (Claude, this repo) | Free | **Default.** Enforces the 5-principle style guide automatically | Run in any Claude Code session |
| [Napkin.ai](https://napkin.ai) | Freemium | Presentation decks, social posts — prettier output than plain Mermaid | Desktop-first; good for LinkedIn visuals |
| [Eraser.io DiagramGPT](https://eraser.io) | Freemium | Cloud architecture diagrams (not process flows) | Code-aware; reads your repo |
| [Whimsical AI](https://whimsical.com) | Freemium | Quick first-draft if already in Whimsical | Less control than `/diagram` |

---

## D. YouTube-first video diagrams (how Nate Herk / Chase AI do it)

**Updated April 2026:** Nate Herk publicly pivoted from n8n to **Claude Code** (March 2026 video: "Stop Learning n8n in 2026...Learn THIS Instead"). Chase Reiner still primarily teaches n8n.

| Creator | Primary tool | As of |
|---|---|---|
| Nate Herk | **Claude Code** | March 2026 |
| Chase Reiner (Shinefy) | n8n canvas | April 2026 (no shift confirmed) |

Both use the same **live-build** video format — the tool canvas IS the diagram. No separate diagramming software during the build segment.

| Segment | Tool | Style |
|---|---|---|
| Cold-open overview card | Excalidraw | 5-node max, hand-drawn, bilingual labels (한/EN) |
| Main build segment | Claude Code (for AI automation) / n8n | Live construction on screen |
| End-of-video recap | Same Excalidraw card + checkmarks | Reuse the cold-open card |

**For First Mover AI Korean channel:** Use Claude Code as the primary build tool (aligns with where Nate Herk is going, differentiates from Chase who stays n8n-heavy).

Template spec: `references/diagrams/youtube-channel-intro-template.md`

---

## File index (this folder)

| File | Use when |
|---|---|
| `_HOW_TO_CRAFT.md` | Style rules and 5 principles — open first |
| `_WHERE_TO_RENDER.md` | Picking a tool — this file |
| `finagent-architecture.md` | Explaining FinAgent to clients, interviewers, SDIC |
| `content-business-pipelines.md` | YouTube pipeline diagrams, 7:3 time split |
| `sdic-curriculum.md` | SDIC teaching, curriculum, weekly session flow |
| `youtube-channel-intro-template.md` | Excalidraw cold-open template for First Mover AI |
