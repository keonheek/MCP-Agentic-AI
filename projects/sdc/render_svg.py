import os
from playwright.sync_api import sync_playwright

svg_path = os.path.abspath("sdic_logo.svg").replace("\\", "/")
out_path = os.path.abspath("sdic_logo_render.png")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1280, "height": 720})
    page.goto("file:///" + svg_path)
    page.screenshot(path=out_path, full_page=False)
    browser.close()
    print(f"Rendered to: {out_path}")
