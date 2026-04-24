"""
Loop 3 — Soomgo/Kmong Listing Optimizer (autoresearch pattern)
Generates Korean marketplace listings for "AI 검색 최적화 진단".
Scores each draft on 4 dimensions, rewrites until avg >= 8.5 or max 5 iterations.
Output: listings/soomgo-final.md + listings/kmong-final.md

Usage:
    python loop3_listing_optimizer.py
"""

import sys
import os
from pathlib import Path
from datetime import date
import anthropic

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

for _p in [HERE / ".env", ROOT / ".env"]:
    if _p.exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=_p)
        break

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

THRESHOLD = 8.5
MAX_ITER = 5


def generate_listing(platform: str, feedback: str = "") -> str:
    platform_notes = {
        "soomgo": "Soomgo (숨고) — service marketplace. Buyers compare pros by price and reviews. Emphasize speed and results.",
        "kmong": "Kmong (크몽) — freelance marketplace. Buyers look for expertise. Emphasize credentials and methodology."
    }
    prompt = f"""
Write a Korean marketplace service listing for platform: {platform_notes[platform]}

Service: AI 검색 최적화 진단 (GEO Audit)
Price: 500,000원 (무료 진단 제공 후 유료 전환)
Provider: 김건희 (SKKU 경영학과 / AI 컨설팅)

The listing must include:
1. 제목 (title, max 40 chars) — attention-grabbing, keyword-rich
2. 서비스 설명 (description, 150-200 words) — what they get, why it matters
3. 제공 내용 (deliverables, bullet list) — specific outputs
4. 차별점 (USP, 2-3 bullets) — why choose you over others
5. CTA — clear next step

Tone: professional but approachable. Not salesy. Speak to business owners who are worried about being invisible to AI tools like ChatGPT.

{f'Previous feedback to address: {feedback}' if feedback else ''}

Output the full listing in Korean. No English except technical terms (AI, GEO, SEO, ChatGPT).
"""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


def score_listing(listing: str) -> tuple[float, str]:
    prompt = f"""
Score this Korean marketplace listing on 4 dimensions (1-10 each):
1. Clarity — is it immediately clear what the service does and who it's for?
2. Urgency triggers — does it create a sense of need without being pushy?
3. Social proof — does it signal credibility (credentials, methodology, specific results)?
4. CTA strength — is the next step obvious and easy to take?

Listing:
---
{listing}
---

Output exactly this format (numbers only, then feedback):
CLARITY: X
URGENCY: X
SOCIAL_PROOF: X
CTA: X
FEEDBACK: [one sentence on biggest improvement needed]
"""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.content[0].text.strip()

    scores = {}
    feedback = ""
    for line in text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip()
            if k in ("CLARITY", "URGENCY", "SOCIAL_PROOF", "CTA"):
                try:
                    scores[k] = float(v)
                except ValueError:
                    scores[k] = 5.0
            elif k == "FEEDBACK":
                feedback = v

    avg = sum(scores.values()) / len(scores) if scores else 0
    return avg, feedback


def optimize(platform: str) -> str:
    print(f"\n  Optimizing {platform} listing...")
    listing = generate_listing(platform)
    feedback = ""

    for i in range(1, MAX_ITER + 1):
        avg, feedback = score_listing(listing)
        print(f"    Iteration {i}: avg score {avg:.1f}/10 — {feedback}")
        if avg >= THRESHOLD:
            print(f"    Threshold met ({avg:.1f} >= {THRESHOLD})")
            break
        if i < MAX_ITER:
            listing = generate_listing(platform, feedback)

    return listing


def run():
    out_dir = HERE / "listings"
    out_dir.mkdir(exist_ok=True)

    print("[Loop 3] Starting listing optimizer...")

    soomgo = optimize("soomgo")
    kmong = optimize("kmong")

    # Save Soomgo
    soomgo_path = out_dir / "soomgo-final.md"
    soomgo_path.write_text(
        f"# Soomgo Listing — Generated {date.today()}\n\n{soomgo}\n",
        encoding="utf-8"
    )
    print(f"\n  Soomgo listing saved: {soomgo_path}")

    # Save Kmong
    kmong_path = out_dir / "kmong-final.md"
    kmong_path.write_text(
        f"# Kmong Listing — Generated {date.today()}\n\n{kmong}\n",
        encoding="utf-8"
    )
    print(f"  Kmong listing saved: {kmong_path}")

    print("\n[Loop 3] Done. Paste listings into Soomgo + Kmong profiles.")


if __name__ == "__main__":
    run()
