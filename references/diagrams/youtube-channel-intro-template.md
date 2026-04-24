# YouTube Channel Intro Template — First Mover AI

_Cold-open flowchart card for every First Mover AI video. Shown for 5–7 seconds at the start. Hand-drawn style via Excalidraw._

_Last updated: 2026-04-23. Based on style study of Nate Herk (now Claude Code-first) and Chase Reiner (n8n-first)._

---

## Video structure

```
AUDIENCE: First Mover AI 시청자 (한국 AI 자동화 입문자)
QUESTION: 이 영상에서 내가 뭘 배울 수 있어?
STATUS: final
```

```
[Cold open — 5초]
    ↓
[Excalidraw 플로차트 카드 — 5–7초]
    ↓
[Live Claude Code / 자동화 빌드 — 영상의 70%]
    ↓
[결과 reveal — 수익 또는 시간 절약 수치]
    ↓
[같은 Excalidraw 카드 + ✓ 체크마크]
```

---

## Cold-open Excalidraw card spec

### Visual rules
- **Tool:** [Excalidraw](https://excalidraw.com) — hand-drawn aesthetic, NOT corporate boxes
- **Background:** off-white (#FFFBE6) or transparent
- **Max nodes:** 5
- **Node style:** Rounded rectangles, hand-drawn stroke
- **Arrow style:** Hand-drawn curved arrows (Excalidraw default)
- **Font:** Virgil (Excalidraw default hand-drawn font)
- **Colors:**
  - Trigger node: sky blue (#74C0FC)
  - AI / Logic node: soft purple (#B197FC)
  - Output node: mint green (#69DB7C)
  - Human step node: peach (#FFA94D)

### Template flowchart (5-node, LR)

```
[트리거] → [AI 분석] → [자동 실행] → [결과] → [수익/절감]
```

In Excalidraw, map to:
- 트리거 (sky blue) — what kicks off the automation
- AI 분석 (soft purple) — Claude / GPT processing step
- 자동 실행 (soft purple) — what the automation does
- 결과 (mint green) — measurable output
- 수익/절감 (mint green, bold text) — the "why it matters" number

### Bilingual label format
Each node label: Korean main + English sub (smaller font below)

Example:
```
AI 분석
(Claude AI)
```

---

## How to build it in Excalidraw

1. Open [excalidraw.com](https://excalidraw.com)
2. Draw 5 rounded rectangles left to right
3. Connect with curved arrows
4. Fill colors per the spec above
5. Add Korean + English labels (Virgil font, Korean 16px / English 11px)
6. Export as PNG (transparent background)
7. Import into video editor (CapCut / DaVinci) as overlay — fade in 0.3s, hold 5s, fade out 0.3s

---

## Creator benchmarks

| Creator | Tool | Format | What Keonhee copies |
|---|---|---|---|
| Nate Herk | **Claude Code** (since March 2026) | Cold open → live Claude Code build → results | Tool choice: Claude Code as the build surface |
| Chase Reiner (Shinefy) | n8n canvas | Cold open → live n8n build → results reveal | Format: live build = the diagram |
| Liam Ottley | Assembly-line analogy diagrams | Overview diagram → step-by-step build | Trigger → Filter → AI → Format → Output template |
| David Ondrej | Multi-agent flowcharts | Conceptual overview → agent architecture | Multi-agent diagrams for advanced episodes |

**Differentiator vs all of them:** Korean narration + Korean business use cases (소상공인, 전자상거래, 크리에이터). Bilingual labels capture Korean + international search.

---

## Episode flowchart variants

For different episode types, use these 5-node patterns:

### Type A — Single automation build
```
문제 발생 → 데이터 수집 → AI 처리 → 자동 실행 → 결과 확인
```

### Type B — Multi-agent system
```
입력 → 분류 에이전트 → 전문 에이전트 → 통합 → 최종 출력
```

### Type C — Content pipeline (First Mover AI channel topic)
```
트렌드 수집 → AI 채점 → 스크립트 생성 → 편집/업로드 → KPI 리포트
```

### Type D — Cost/time saving demo
```
기존 방식 → 병목 지점 → AI 대체 → 새 흐름 → 시간/비용 절감
```

---

## Status tracking per episode

When reusing this template, append the episode info:

| Episode | Type | Mermaid backup file | Status |
|---|---|---|---|
| EP01 - TBD | TBD | TBD | draft |
