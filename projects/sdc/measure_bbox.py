from playwright.sync_api import sync_playwright

html = """
<html><body style="margin:0;padding:0;background:white;">
<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="600">
  <text id="s" x="100" y="300" font-family="Georgia, serif" font-size="240" font-weight="bold">S</text>
  <text id="dic" x="100" y="300" font-family="Georgia, serif" font-size="240" font-weight="bold">DIC</text>
  <text id="sub" x="100" y="400" font-family="Georgia, serif" font-size="29" font-weight="bold">SKKU Digital IT Consulting</text>
</svg>
</body></html>
"""

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1400, "height": 600})
    page.set_content(html)
    s = page.eval_on_selector("#s", "el => { const b = el.getBBox(); return {x:b.x,y:b.y,w:b.width,h:b.height}; }")
    dic = page.eval_on_selector("#dic", "el => { const b = el.getBBox(); return {x:b.x,y:b.y,w:b.width,h:b.height}; }")
    sub = page.eval_on_selector("#sub", "el => { const b = el.getBBox(); return {x:b.x,y:b.y,w:b.width,h:b.height}; }")
    print("S (anchored at x=100):", s)
    print("DIC (anchored at x=100):", dic)
    print("Subtitle:", sub)
    # S visual left edge = s.x, visual right edge = s.x + s.w
    # If S anchored at x=100, visual left = s['x'], right = s['x']+s['w']
    # S advance width = s['x'] - 100 + s['w']  (includes right bearing to next char)
    print(f"\nS: visual left={s['x']:.1f}, visual right={s['x']+s['w']:.1f}")
    print(f"S advance (x=100 anchor): left bearing={s['x']-100:.1f}, width={s['w']:.1f}")
    print(f"DIC: visual left={dic['x']:.1f}, visual right={dic['x']+dic['w']:.1f}")
    browser.close()
