"""
Autoresearch loop for 3D Landing Page Action Plan.
Generates → scores → improves until avg score >= 9.7 or max iterations reached.
Scorer: Haiku (cheap). Generator/Improver: Sonnet.
Output saved to Obsidian vault.
"""

import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

import anthropic
sys.stdout.reconfigure(encoding="utf-8")

SCORER_MODEL = "claude-haiku-4-5-20251001"
GENERATOR_MODEL = "claude-sonnet-4-6"

MAX_ITERATIONS = 12
SCORE_THRESHOLD = 9.7

CONTEXT = """
You are generating a comprehensive, highly actionable action plan for building a cinematic 3D landing page mockup website.

TARGET: 온기 카페 (Korean cafe) — a free portfolio piece to land a testimonial and case study.

MUST FOLLOW — Viktor Oddy's exact workflow from his two Gemini 3.1 videos:
1. Find a reference design to feed to the AI builder (don't start from blank canvas)
2. Generate base hero images (Nano Banana for AI image generation)
3. Animate images into start/end frame pairs using Cling 3.0
4. Convert animation to high-framerate JPEG sequence for scroll-driven backgrounds
5. Paste generated HTML/CSS into Antigravity (or Lovable), add image sequence
6. Use text prompts in Antigravity to script scroll behavior and refine section by section
7. Add CSS transitions, liquid glass effects, animated elements
8. Viral strategy: record short clips in Figma/browser, add noise/grain, post on Twitter

ALSO INCORPORATE — Ryan Mathews' conversion principles:
- Above-the-fold: headline + single CTA + hero visual
- Visual hierarchy (headline → hero → CTA)
- Social proof near every claim
- Copy targeting problem-aware (not solution-aware) Korean SME owners
- Animations support message, never distract

SCORING DIMENSIONS (each 0-10):
1. Completeness — Does the plan cover every step of Viktor Oddy's full workflow with no gaps?
2. Specificity — Are steps concrete with exact tools, commands, time estimates, and deliverables?
3. Actionability — Can Keonhee sit down Monday morning and execute without googling anything?

THRESHOLD: Average of all three dimensions must reach 9.7/10 to stop.
"""

INITIAL_DRAFT = """
# 3D Landing Page Action Plan — 온기 카페 Mockup

## Goal
Build a free cinematic 3D landing page for 온기 카페, deploy to Vercel, DM for testimonial.
Timeline: April 7-13, 2026.

## Tools Required
- Nano Banana (hero image generation)
- Cling 3.0 (video animation)
- Antigravity OR Lovable (Gemini 3.1) — site builder
- Vercel (deployment)
- Screen recorder (30-sec comparison video)

## Steps
1. Find reference design online (premium cafe/restaurant site)
2. Generate hero images with Nano Banana from cafe photos
3. Animate with Cling 3.0 → JPEG sequence
4. Build in Antigravity → add JPEG sequence → prompt scroll behavior
5. Add conversion elements (Ryan Mathews framework)
6. Deploy to Vercel
7. Record before/after video
8. DM 온기 카페 on Instagram

## Viral Strategy
Record clip → add noise → post on Twitter

## Upsell Path
Free → 500K KRW → retainer → ERP
"""


def _score(client: anthropic.Anthropic, content: str) -> dict:
    prompt = f"""Score this action plan on three dimensions (0-10 each). Be rigorous — 9.7+ means world-class, no gaps.

CONTEXT:
{CONTEXT}

ACTION PLAN TO SCORE:
{content}

Return ONLY valid JSON (no markdown, no explanation):
{{
  "completeness": <0-10>,
  "specificity": <0-10>,
  "actionability": <0-10>,
  "feedback": "<one precise sentence on the single most important thing to improve>"
}}"""

    resp = client.messages.create(
        model=SCORER_MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip()
    # Strip markdown code fences if present
    if "```" in raw:
        lines = raw.splitlines()
        start = next((i for i, l in enumerate(lines) if l.strip().startswith("```")), 0)
        end = next((i for i, l in enumerate(lines[start+1:], start+1) if l.strip() == "```"), len(lines))
        raw = "\n".join(lines[start+1:end])
    # Extract first JSON object from the response
    import re
    match = re.search(r'\{[^{}]*\}', raw, re.DOTALL)
    if match:
        raw = match.group(0)
    return json.loads(raw)


def _generate_or_improve(client: anthropic.Anthropic, content: str, scores: dict | None, iteration: int) -> str:
    if scores is None:
        # First generation — expand the initial draft
        prompt = f"""Expand this initial draft into a comprehensive, step-by-step action plan.

CONTEXT:
{CONTEXT}

INITIAL DRAFT:
{content}

Requirements:
- Every step must include: exact tool, exact action, time estimate, expected output
- Viktor Oddy's full workflow must be covered in order (image gen → animation → JPEG sequence → Antigravity/Lovable → CSS refinement → viral clip)
- Ryan Mathews' conversion rules applied to specific sections of the page
- Korean-specific details (Naver Map embed, KakaoTalk DM script, 온기 카페 specific copy)
- Day-by-day schedule for April 7-13
- Troubleshooting notes for the hardest steps

Return ONLY the action plan in Markdown."""
    else:
        prompt = f"""Improve this action plan to score 9.7+/10 on completeness, specificity, and actionability.

CONTEXT:
{CONTEXT}

Current scores: completeness={scores['completeness']}/10, specificity={scores['specificity']}/10, actionability={scores['actionability']}/10
Feedback: {scores['feedback']}

Current plan:
{content}

Make targeted improvements based on the feedback. Do not remove existing good content — only add, clarify, or make more specific.
Return ONLY the improved action plan in Markdown."""

    resp = client.messages.create(
        model=GENERATOR_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


def run_loop():
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    print(f"Starting autoresearch loop — threshold: {SCORE_THRESHOLD}, max iterations: {MAX_ITERATIONS}")
    print("=" * 70)

    content = INITIAL_DRAFT
    scores = None
    score_history = []

    for i in range(MAX_ITERATIONS):
        print(f"\n[Iteration {i+1}/{MAX_ITERATIONS}] Generating...")
        content = _generate_or_improve(client, content, scores, i)

        print(f"[Iteration {i+1}] Scoring...")
        scores = _score(client, content)
        avg = round((scores["completeness"] + scores["specificity"] + scores["actionability"]) / 3, 2)
        scores["avg"] = avg
        score_history.append({"iteration": i + 1, "scores": scores})

        print(f"  completeness={scores['completeness']} | specificity={scores['specificity']} | actionability={scores['actionability']} | avg={avg}")
        print(f"  feedback: {scores['feedback']}")

        if avg >= SCORE_THRESHOLD:
            print(f"\n  THRESHOLD {SCORE_THRESHOLD} REACHED at iteration {i+1}.")
            break
        else:
            print(f"  Need {SCORE_THRESHOLD - avg:.2f} more points. Continuing...")

    # Save final plan
    output_path = Path(__file__).parent / "3d_landing_plan_final.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# 3D Landing Page Action Plan — Final (Score: {scores['avg']}/10)\n\n")
        f.write(f"_Autoresearch loop: {len(score_history)} iterations | completeness={scores['completeness']} | specificity={scores['specificity']} | actionability={scores['actionability']}_\n\n")
        f.write("---\n\n")
        f.write(content)

    print(f"\nFinal plan saved to: {output_path}")
    print(f"Final scores: {scores}")
    return content, scores, score_history


if __name__ == "__main__":
    final_content, final_scores, history = run_loop()
    print("\n" + "=" * 70)
    print(f"DONE — Final avg score: {final_scores['avg']}/10 after {len(history)} iterations")
