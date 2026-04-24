"""
Screenshot Critique Loop — SDIC Website
Runs the generate → screenshot → Haiku-vision critique → improve loop.

Flow:
  1. Generate HTML via loop4_sdic_website.py (or use existing)
  2. Start local HTTP server on port 8765
  3. Playwright: screenshot hero (1920x1080) + full page + mobile (375x812)
  4. Haiku vision scores all 3 images (cheap, ~$0.008/iter)
  5. If avg < 9.0: pass critique to Sonnet generator, regenerate
  6. Loop up to MAX_ITERATIONS or until avg >= SCORE_THRESHOLD
  7. Save score history to score_history.json
  8. Optionally deploy winner to Vercel

Usage:
    python screenshot_critique_loop.py            # iterate until threshold or max
    python screenshot_critique_loop.py --deploy   # also deploy winning version
    python screenshot_critique_loop.py --skip-gen # skip generation, use existing HTML

Prerequisites:
    pip install playwright anthropic
    playwright install chromium
    vercel login  (only if --deploy)
"""

import sys
import os
import json
import time
import base64
import shutil
import subprocess
import threading
import http.server
import socketserver
import argparse
from pathlib import Path
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent

for _p in [ROOT / ".env", HERE.parent.parent / ".env"]:
    if _p.exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=_p)
        break

import anthropic
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

LANDING_DIR = HERE / "landing_pages" / "sdic"
SCREENSHOTS_DIR = LANDING_DIR / "screenshots"
SCORE_HISTORY_PATH = LANDING_DIR / "score_history.json"

MAX_ITERATIONS = 5
SCORE_THRESHOLD = 9.0
HTTP_PORT = 8766

SCORER_MODEL = "claude-haiku-4-5-20251001"   # cheap vision scorer
GENERATOR_MODULE = HERE / "loop4_sdic_website.py"


# ─── HTTP server (background thread) ─────────────────────────────────────────

class SilentHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass  # suppress request logs

def start_server(directory: Path, port: int):
    os.chdir(directory)
    handler = SilentHandler
    httpd = socketserver.TCPServer(("", port), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


# ─── Screenshot ───────────────────────────────────────────────────────────────

def take_screenshots(iteration: int) -> dict[str, Path]:
    """Take 3 screenshots via Playwright: hero, full, mobile."""
    from playwright.sync_api import sync_playwright

    iter_dir = SCREENSHOTS_DIR / f"iter-{iteration:02d}"
    iter_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "hero":   iter_dir / "hero.png",
        "full":   iter_dir / "full.png",
        "mobile": iter_dir / "mobile.png",
    }

    url = f"http://localhost:{HTTP_PORT}/index.html"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            args=["--enable-webgl", "--use-gl=swiftshader", "--no-sandbox"]
        )

        # Desktop hero (1280x800 — smaller viewport keeps file under 5MB)
        ctx_desktop = browser.new_context(viewport={"width": 1280, "height": 800})
        page = ctx_desktop.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(2)  # let Three.js render
        page.screenshot(path=str(paths["hero"]), full_page=False)

        # Full page — cap at 1280 wide, JPEG via temp then convert to keep under 5MB
        page.screenshot(path=str(paths["full"]), full_page=True, clip={"x": 0, "y": 0, "width": 1280, "height": 4000})
        ctx_desktop.close()

        # Mobile (375x812)
        ctx_mobile = browser.new_context(viewport={"width": 375, "height": 812})
        page_m = ctx_mobile.new_page()
        page_m.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(1)
        page_m.screenshot(path=str(paths["mobile"]), full_page=False)
        ctx_mobile.close()

        browser.close()

    return paths


# ─── Haiku vision scorer ──────────────────────────────────────────────────────

def encode_image(path: Path) -> str:
    """Encode image as base64, compressing if over 4MB to stay under Haiku's 5MB limit."""
    MAX_BYTES = 4 * 1024 * 1024  # 4MB safe limit
    data = path.read_bytes()
    if len(data) <= MAX_BYTES:
        return base64.standard_b64encode(data).decode("utf-8")
    # Compress using Pillow if available, else just truncate to safe size via resize
    try:
        from PIL import Image
        import io
        img = Image.open(path)
        # Halve dimensions until under limit
        while True:
            img = img.resize((img.width // 2, img.height // 2), Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="PNG", optimize=True)
            if buf.tell() <= MAX_BYTES:
                return base64.standard_b64encode(buf.getvalue()).decode("utf-8")
    except ImportError:
        # Pillow not installed — read raw and hope for the best
        return base64.standard_b64encode(data[:MAX_BYTES]).decode("utf-8")


def score_screenshots(paths: dict[str, Path]) -> dict:
    """Score 3 screenshots with Haiku vision. Returns dict with scores + feedback."""

    images_content = []
    for label, path in paths.items():
        images_content.append({
            "type": "text",
            "text": f"[{label.upper()} SCREENSHOT]"
        })
        images_content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": encode_image(path),
            }
        })

    images_content.append({
        "type": "text",
        "text": """
You are scoring a student consulting club website (SDIC — SKKU Digital IT Consulting).
Reference quality bar: Bain.com / Deloitte.com (score 9/10). Target: match or exceed.

Score each dimension 0-10. Return ONLY valid JSON, no other text:

{
  "visual_polish": <0-10>,
  "typography_hierarchy": <0-10>,
  "color_harmony": <0-10>,
  "animation_sophistication": <0-10>,
  "info_density_balance": <0-10>,
  "mobile_experience": <0-10>,
  "consulting_credibility": <0-10>,
  "feedback": "<2-3 sentences: what's working, what's broken, top 3 concrete fixes>"
}

Be strict. A generic template site scores 5. Bain.com scores 9. Only give 9+ if it genuinely looks world-class.
"""
    })

    resp = client.messages.create(
        model=SCORER_MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": images_content}]
    )

    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.splitlines()[1:-1])

    scores = json.loads(raw)
    dims = [k for k in scores if k != "feedback"]
    scores["avg"] = round(sum(scores[d] for d in dims) / len(dims), 2)
    return scores


# ─── Regenerate with critique ─────────────────────────────────────────────────

def regenerate(iteration: int, critique: str):
    """Call the generator with the critique injected."""
    # Import and call directly (faster than subprocess)
    sys.path.insert(0, str(HERE))
    import importlib.util
    spec = importlib.util.spec_from_file_location("loop4_sdic", GENERATOR_MODULE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    html = mod.build_sdic_html(iteration=iteration, previous_critique=critique)
    html_path = LANDING_DIR / "index.html"
    html_path.write_text(html, encoding="utf-8")
    print(f"    HTML regenerated (iter {iteration}): {html_path}")


# ─── Deploy ───────────────────────────────────────────────────────────────────

def deploy_to_vercel() -> str:
    import re
    slug = "sdic-website"
    result = subprocess.run(
        ["vercel", "--yes", "--name", slug, str(LANDING_DIR)],
        capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        raise RuntimeError(f"Vercel deploy failed:\n{result.stderr}")
    for line in result.stdout.splitlines():
        if line.startswith("https://"):
            return line.strip()
    return result.stdout.strip().splitlines()[-1]


# ─── Main loop ────────────────────────────────────────────────────────────────

def run(skip_gen: bool = False, deploy: bool = False):
    LANDING_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    score_history = []

    # Step 0: initial generation (unless skipped)
    if not skip_gen:
        print("[Loop] Step 0: Generating initial HTML...")
        regenerate(iteration=0, critique="")
    else:
        print("[Loop] Skipping generation, using existing HTML.")

    # Start HTTP server
    print(f"[Loop] Starting local HTTP server on port {HTTP_PORT}...")
    httpd = start_server(LANDING_DIR, HTTP_PORT)
    time.sleep(0.5)

    try:
        for i in range(1, MAX_ITERATIONS + 1):
            print(f"\n[Loop] ── Iteration {i}/{MAX_ITERATIONS} ──")

            # Screenshot
            print("  Taking screenshots...")
            try:
                paths = take_screenshots(iteration=i)
            except Exception as e:
                print(f"  Screenshot failed: {e}")
                print("  Tip: run 'playwright install chromium' if not installed.")
                break

            # Score (retry up to 3x on overload)
            print("  Scoring with Haiku vision...")
            scores = None
            for attempt in range(3):
                try:
                    scores = score_screenshots(paths)
                    break
                except Exception as e:
                    if "overloaded" in str(e).lower() and attempt < 2:
                        print(f"  API overloaded, retrying in 15s... (attempt {attempt+1}/3)")
                        time.sleep(15)
                    else:
                        print(f"  Scoring failed: {e}")
                        break
            if scores is None:
                break

            avg = scores["avg"]
            score_history.append({"iteration": i, "scores": scores})
            print(f"  avg={avg:.2f} | {scores['feedback'][:120]}")

            # Save history
            SCORE_HISTORY_PATH.write_text(
                json.dumps({"date": str(date.today()), "history": score_history}, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )

            if avg >= SCORE_THRESHOLD:
                print(f"\n[Loop] Threshold {SCORE_THRESHOLD} reached at iteration {i}. Done.")
                break

            if i < MAX_ITERATIONS:
                print(f"  Regenerating with critique (avg {avg:.2f} < {SCORE_THRESHOLD})...")
                regenerate(iteration=i + 1, critique=scores["feedback"])
                time.sleep(1)  # let file settle

        else:
            print(f"\n[Loop] Max iterations ({MAX_ITERATIONS}) reached.")

    finally:
        httpd.shutdown()
        print("[Loop] HTTP server stopped.")

    # Final summary
    if score_history:
        final = score_history[-1]["scores"]
        print(f"\n[Loop] Final score: {final['avg']:.2f}/10")
        print(f"[Loop] Score history: {[round(h['scores']['avg'], 2) for h in score_history]}")
        print(f"[Loop] HTML: {LANDING_DIR / 'index.html'}")
        print(f"[Loop] Scores: {SCORE_HISTORY_PATH}")

    # Deploy
    if deploy:
        print("\n[Loop] Deploying to Vercel...")
        try:
            url = deploy_to_vercel()
            print(f"[Loop] Live URL: {url}")
        except RuntimeError as e:
            print(f"[Loop] Deploy failed: {e}")
            print(f"       Run manually: vercel --yes --name sdic-website {LANDING_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--deploy", action="store_true", help="Deploy winning version to Vercel")
    parser.add_argument("--skip-gen", action="store_true", help="Use existing HTML, skip generation")
    args = parser.parse_args()
    run(skip_gen=args.skip_gen, deploy=args.deploy)
