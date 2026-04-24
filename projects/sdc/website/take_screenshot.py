"""
Take screenshots of the SDIC site for Claude to review visually.
No API calls — just Playwright screenshots saved to disk.

Usage:
    python take_screenshot.py
"""
import sys, time, http.server, socketserver, threading
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
LANDING_DIR = HERE / "landing_pages" / "sdic"
OUT_DIR = LANDING_DIR / "screenshots" / "review"
PORT = 8787

class SilentHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass

def start_server():
    import os
    os.chdir(LANDING_DIR)
    httpd = socketserver.TCPServer(("", PORT), SilentHandler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd

def take():
    from playwright.sync_api import sync_playwright
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    url = f"http://localhost:{PORT}/index.html"

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--enable-webgl", "--use-gl=swiftshader", "--no-sandbox"])

        # Desktop hero
        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        page = ctx.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(2)
        page.screenshot(path=str(OUT_DIR / "hero.png"), full_page=False)
        print(f"  hero:   {OUT_DIR / 'hero.png'}")

        # Force-reveal all .reveal elements so sections show in full-page shot
        page.evaluate("""() => {
          document.querySelectorAll('.reveal').forEach(el => el.classList.add('visible'));
        }""")
        time.sleep(0.5)

        # Full page (clipped to 3000px tall max)
        page.screenshot(path=str(OUT_DIR / "full.png"), full_page=True,
                        clip={"x": 0, "y": 0, "width": 1280, "height": 3000})
        print(f"  full:   {OUT_DIR / 'full.png'}")
        ctx.close()

        # Mobile
        ctx_m = browser.new_context(viewport={"width": 390, "height": 844})
        page_m = ctx_m.new_page()
        page_m.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(1)
        page_m.screenshot(path=str(OUT_DIR / "mobile.png"), full_page=False)
        print(f"  mobile: {OUT_DIR / 'mobile.png'}")
        ctx_m.close()

        browser.close()

if __name__ == "__main__":
    print(f"[Screenshot] Starting server on port {PORT}...")
    httpd = start_server()
    time.sleep(0.5)
    print("[Screenshot] Taking screenshots...")
    take()
    httpd.shutdown()
    print("[Screenshot] Done.")
