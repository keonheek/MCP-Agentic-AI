"""
Loop 4 — 3D Landing Page Build Pipeline
Given a business name + URL, builds a Three.js 3D homepage and deploys to Vercel.
Output: landing_pages/<business_name>/index.html + live Vercel URL

Usage:
    python loop4_3d_landing_page.py --name "카페봄봄" --url "https://cafebombom.com"
    python loop4_3d_landing_page.py --name "MyShop" --url "https://myshop.modoo.at"

Prerequisites:
    npm install -g vercel   (one-time)
    vercel login            (one-time — opens browser)
"""

import sys
import os
import re
import subprocess
import argparse
from pathlib import Path
from datetime import date
import anthropic
import requests

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


def scrape_brand_info(url: str) -> str:
    """Fetch homepage text for brand signals (colors, copy, style)."""
    try:
        r = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        text = r.text[:3000]
        # Strip HTML tags roughly
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:1500]
    except Exception as e:
        return f"Could not fetch site ({e}). Use generic design."


def build_threejs_page(business_name: str, url: str, brand_info: str) -> str:
    prompt = f"""
Build a complete, self-contained HTML file with Three.js 3D animation for a Korean local business homepage makeover.

Business: {business_name}
Original site: {url}
Brand signals from their site: {brand_info}

Requirements:
- Single HTML file with embedded CSS and JS (no external imports except CDN)
- Use Three.js via CDN: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js
- 3D hero section: animated geometric shapes (spheres, boxes, particles) that reflect the brand
- Clean, modern Korean-friendly font (Noto Sans KR via Google Fonts)
- Sections: Hero (3D), 서비스 소개, 연락처
- Mobile responsive
- Smooth scroll
- Color palette: derive from brand signals, default to clean white/dark if unclear
- The 3D animation should feel premium — think Apple product page energy, not tech demo
- Footer: "디자인 by 김건희 AI Lab"

Output ONLY the complete HTML file content. No explanation. No markdown fences.
"""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


def deploy_to_vercel(build_dir: Path, project_name: str) -> str:
    """Run vercel deploy and return the URL."""
    slug = re.sub(r"[^a-z0-9-]", "-", project_name.lower())[:28]
    result = subprocess.run(
        ["vercel", "--yes", "--name", slug, str(build_dir)],
        capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        raise RuntimeError(f"Vercel deploy failed:\n{result.stderr}")
    # Extract URL from output
    for line in result.stdout.splitlines():
        if line.startswith("https://"):
            return line.strip()
    return result.stdout.strip().splitlines()[-1]


def generate_comparison_script(business_name: str, score: int, live_url: str) -> str:
    prompt = f"""
Write a 30-second Korean talking script for a before/after comparison video for {business_name}.

Before: their current site (old-looking, low AI visibility, GEO score {score}/100)
After: new 3D site at {live_url}

Format:
- 0-5초: hook (문제 제시)
- 5-20초: before 화면 설명
- 20-25초: after 화면 공개
- 25-30초: CTA ("이런 홈페이지 원하시면 DM 주세요")

Tone: energetic but not pushy. Korean only. Under 100 words.
"""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


def run(business_name: str, url: str):
    slug = re.sub(r"\s+", "_", business_name.lower())
    out_dir = HERE / "landing_pages" / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[Loop 4] Building 3D landing page for: {business_name}")

    # Step 1 — Scrape brand
    print("  Step 1/4: Fetching brand signals...")
    brand_info = scrape_brand_info(url)

    # Step 2 — Build HTML
    print("  Step 2/4: Generating Three.js page...")
    html = build_threejs_page(business_name, url, brand_info)
    html_path = out_dir / "index.html"
    html_path.write_text(html, encoding="utf-8")
    print(f"    HTML saved: {html_path}")

    # Step 3 — Deploy
    print("  Step 3/4: Deploying to Vercel...")
    try:
        live_url = deploy_to_vercel(out_dir, f"geo-demo-{slug}")
        print(f"    Live URL: {live_url}")
    except RuntimeError as e:
        print(f"    Vercel deploy failed (run 'vercel login' first): {e}")
        live_url = f"[deploy manually: vercel {out_dir}]"

    # Step 4 — Comparison script
    print("  Step 4/4: Generating comparison script...")
    script = generate_comparison_script(business_name, 40, live_url)
    script_path = out_dir / "comparison_script.md"
    script_path.write_text(
        f"# 30-Second Script — {business_name}\n\n{script}\n\n---\nGenerated: {date.today()}\nLive URL: {live_url}\n",
        encoding="utf-8"
    )

    print(f"\n[Loop 4] Done.")
    print(f"  Live URL: {live_url}")
    print(f"  HTML:     {html_path}")
    print(f"  Script:   {script_path}")
    print(f"\n  DM template: '안녕하세요! {business_name} 홈페이지를 새롭게 만들어봤어요: {live_url} 무료로 드릴게요, 후기만 부탁드려요 :)'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Business name (Korean OK)")
    parser.add_argument("--url", required=True, help="Their current website URL")
    args = parser.parse_args()
    run(args.name, args.url)
