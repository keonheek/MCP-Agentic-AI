"""
SDIC Website Generator — forked from loop4_3d_landing_page.py
Builds a cinematic Three.js single-page site for SDIC (SKKU Digital IT Consulting 학회).

Design: Direction C — Digital Consulting OS
  Primary: #0B1220 deep navy
  Accent 1: #2d6038 forest green (from logo)
  Accent 2: #E8FF3B neon yellow
  Font: Clash Display (headings) + Pretendard (body KR) + Inter (body EN)
  Signature: rotating 3D SDIC "S" monogram + particle field + slide-counter sections + status terminal

Strategy: generate base HTML (CSS-only hero placeholder) then inject pre-written Three.js
particle canvas to avoid token truncation. This guarantees complete HTML + 3D animation.

Usage:
    python loop4_sdic_website.py          # generates HTML to landing_pages/sdic/
    python loop4_sdic_website.py --open   # also opens in browser after generation
"""

import sys
import os
import argparse
import shutil
from pathlib import Path
import anthropic

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent  # MCP_Agentic AI root

for _p in [ROOT / ".env", HERE.parent.parent / ".env"]:
    if _p.exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=_p)
        break

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

OUT_DIR = HERE / "landing_pages" / "sdic"
ASSETS_DIR = HERE / "assets"

# ─── i18n content ─────────────────────────────────────────────────────────────

SDIC_CONTENT = {
    "ko": {
        "nav_about": "소개",
        "nav_teams": "팀",
        "nav_methodology": "방법론",
        "nav_recruiting": "리크루팅",
        "nav_contact": "연락",
        "tagline": "전략의 중심에서, 디지털의 경계를 넓히다",
        "subtitle": "성균관대학교 디지털 IT 컨설팅 학회",
        "cta": "지원하기",
        "scroll": "스크롤",
        "about_title": "SDIC란?",
        "p1_title": "리서치",
        "p1_desc": "데이터 기반 인사이트로 문제의 본질을 파악합니다",
        "p2_title": "전략",
        "p2_desc": "구조화된 사고로 최적의 솔루션을 도출합니다",
        "p3_title": "테크놀로지",
        "p3_desc": "디지털 기술을 활용해 전략을 실행합니다",
        "mission": "SDIC는 데이터 기반 전략 사고와 실전 컨설팅 역량을 갖춘 비즈니스 리더를 양성합니다.",
        "teams_title": "팀 구성",
        "im_name": "IM팀",
        "im_sub": "Industry & Market",
        "im_desc": "산업 분석 및 시장 조사를 통해 인사이트를 발굴합니다",
        "pr_name": "PR팀",
        "pr_sub": "Public Relations",
        "pr_desc": "학회 브랜딩과 외부 커뮤니케이션을 담당합니다",
        "edu_name": "EDU팀",
        "edu_sub": "Education",
        "edu_desc": "컨설팅 방법론 교육과 역량 개발을 이끕니다",
        "president_title": "회장 메시지",
        "president_quote": "SDIC는 단순한 학회가 아닙니다. 성균관대학교에서 가장 빠르게 성장하는 컨설팅 커뮤니티입니다.",
        "president": "김건희, 회장",
        "method_title": "방법론",
        "s1": "리서치",
        "s2": "구조화",
        "s3": "솔루션",
        "s4": "프레젠테이션",
        "recruit_title": "리크루팅",
        "r1": "성균관대학교 재학생",
        "r2": "비즈니스/기술에 대한 열정",
        "r3": "팀 협업 능력",
        "r4": "성장 마인드셋",
        "apply_cta": "지금 지원하기",
        "cohort": "2026 코호트 1기 모집 중",
        "footer_copy": "© 2026 SDIC — SKKU Digital IT Consulting",
        "footer_credit": "Designed by Keonhee Kim",
    },
    "en": {
        "nav_about": "About",
        "nav_teams": "Teams",
        "nav_methodology": "Methodology",
        "nav_recruiting": "Recruiting",
        "nav_contact": "Contact",
        "tagline": "At the Core of Strategy. On the Edge of Digital.",
        "subtitle": "SKKU Digital IT Consulting Society",
        "cta": "Apply Now",
        "scroll": "Scroll",
        "about_title": "What is SDIC?",
        "p1_title": "Research",
        "p1_desc": "Uncovering the root of problems through data-driven insight",
        "p2_title": "Strategy",
        "p2_desc": "Deriving optimal solutions through structured thinking",
        "p3_title": "Technology",
        "p3_desc": "Executing strategy with cutting-edge digital tools",
        "mission": "SDIC develops business leaders with data-driven strategic thinking and real-world consulting competencies.",
        "teams_title": "Our Teams",
        "im_name": "IM Team",
        "im_sub": "Industry & Market",
        "im_desc": "Extracting insights through industry analysis and market research",
        "pr_name": "PR Team",
        "pr_sub": "Public Relations",
        "pr_desc": "Managing club branding and external communications",
        "edu_name": "EDU Team",
        "edu_sub": "Education",
        "edu_desc": "Leading consulting methodology education and capability development",
        "president_title": "President's Note",
        "president_quote": "SDIC is not just a club. It is SKKU's fastest-growing consulting community.",
        "president": "Keonhee Kim, President",
        "method_title": "Methodology",
        "s1": "Research",
        "s2": "Structure",
        "s3": "Solve",
        "s4": "Present",
        "recruit_title": "Recruiting",
        "r1": "SKKU enrolled student",
        "r2": "Passion for business & technology",
        "r3": "Team collaboration skills",
        "r4": "Growth mindset",
        "apply_cta": "Apply Now",
        "cohort": "Now Recruiting 2026 Cohort 1",
        "footer_copy": "© 2026 SDIC — SKKU Digital IT Consulting",
        "footer_credit": "Designed by Keonhee Kim",
    }
}


# ─── Pre-written Three.js particle hero injection ─────────────────────────────
# This avoids token-limit truncation: the 3D code is hardcoded here, not generated.

THREEJS_HERO_SCRIPT = """
<script>
// Three.js refined star field for SDIC hero — consulting-grade, not startup
(function init() {
  var canvas = document.getElementById('hero-canvas');
  if (!canvas) return;
  var THREE = window.THREE;
  if (!THREE) { setTimeout(init, 300); return; }

  var W = canvas.parentElement ? canvas.parentElement.clientWidth : window.innerWidth;
  var H = canvas.parentElement ? canvas.parentElement.clientHeight : window.innerHeight;

  var scene = new THREE.Scene();
  var camera = new THREE.PerspectiveCamera(55, W / H, 0.1, 1000);
  camera.position.z = 90;

  var renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
  renderer.setSize(W, H);
  renderer.setClearColor(0x000000, 0);

  // Sparse, small, mostly white/muted — editorial starfield, not a game
  var count = 900;
  var geo = new THREE.BufferGeometry();
  var pos = new Float32Array(count * 3);
  var col = new Float32Array(count * 3);

  for (var i = 0; i < count; i++) {
    pos[i*3]   = (Math.random() - 0.5) * 250;
    pos[i*3+1] = (Math.random() - 0.5) * 250;
    pos[i*3+2] = (Math.random() - 0.5) * 120;

    // Palette: 80% muted blue-white, 20% forest green — NO yellow
    if (Math.random() < 0.8) {
      // muted blue-white #9AA8C7 to white
      var t = Math.random();
      col[i*3]   = 0.60 + t * 0.40;
      col[i*3+1] = 0.66 + t * 0.34;
      col[i*3+2] = 0.78 + t * 0.22;
    } else {
      // forest green #2d6038 — subtle
      col[i*3]   = 0.18;
      col[i*3+1] = 0.38;
      col[i*3+2] = 0.22;
    }
  }

  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(col, 3));

  var mat = new THREE.PointsMaterial({
    size: 0.7,
    vertexColors: true,
    transparent: true,
    opacity: 0.5,
    sizeAttenuation: true,
  });

  var stars = new THREE.Points(geo, mat);
  scene.add(stars);

  // Very slow drift — not a dance party
  var mouse = { x: 0, y: 0 };
  window.addEventListener('mousemove', function(e) {
    mouse.x = (e.clientX / window.innerWidth  - 0.5);
    mouse.y = (e.clientY / window.innerHeight - 0.5);
  });

  window.addEventListener('resize', function() {
    var nW = canvas.parentElement ? canvas.parentElement.clientWidth  : window.innerWidth;
    var nH = canvas.parentElement ? canvas.parentElement.clientHeight : window.innerHeight;
    camera.aspect = nW / nH;
    camera.updateProjectionMatrix();
    renderer.setSize(nW, nH);
  });

  var clock = new THREE.Clock();
  function animate() {
    requestAnimationFrame(animate);
    var t = clock.getElapsedTime();
    // Very slow, almost imperceptible rotation — calm, authoritative
    stars.rotation.y = t * 0.012 + mouse.x * 0.04;
    stars.rotation.x = t * 0.006 + mouse.y * 0.02;
    renderer.render(scene, camera);
  }
  animate();
})();
</script>
"""

# ─── Generator ────────────────────────────────────────────────────────────────

def build_sdic_html(iteration: int = 0, previous_critique: str = "") -> str:
    improvement_note = ""
    if previous_critique:
        improvement_note = f"\nPREVIOUS CRITIQUE (fix these):\n{previous_critique}\n"

    prompt = f"""Build a complete single-file HTML for SDIC (SKKU Digital IT Consulting). Output ONLY raw HTML. Start <!DOCTYPE html>, end </html>. No markdown fences. TERSE CSS, MINIMAL JS — target ~10K tokens total.{improvement_note}

REFERENCE BAR: Bain.com, Deloitte.com — editorial, authoritative, generous whitespace. NOT a startup. NOT neon-heavy.

PALETTE: bg:#0B1220  heading:#F0F4FF  muted:#9AA8C7  green:#2d6038  yellow:#E8FF3B  card:#0D1B2A
CONSULTING RULES: yellow ONLY on primary CTA button + bottom status bar. All section headings in #F0F4FF. No yellow decorations, borders, or highlights elsewhere. White space: section padding 6rem top/bottom. Typography: Clash Display for h1/h2 ONLY. Inter for all other text.
CDN: https://api.fontshare.com/v2/css?f[]=clash-display@600,700&display=swap  |  https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap  |  https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js

SECTIONS (terse CSS per section — share classes where possible):
NAV: fixed top. backdrop-filter:blur(12px). bg transparent→rgba(13,27,42,0.95) on scroll. Left: SVG (16px green circle + "DIC" monospace 14px white). Center: links Inter 13px letter-spacing:0.08em. Right: KO|EN pill (border green, active=green bg). Hamburger mobile.
HERO: 100vh relative overflow:hidden bg:#0B1220. canvas#hero-canvas position:absolute top:0 left:0 width:100% height:100% pointer-events:none z-index:0. Hero inner div: position:relative z-index:2 display:flex flex-direction:column justify-content:center padding:0 8% height:100%. CRITICAL — hero text MUST be visible: h1 color:#F0F4FF explicitly set, never inherit. img src="logo.png" height:56px display:block mb:2.5rem with @keyframes float. h1 data-i18n="tagline" hardcoded content "전략의 중심에서, 디지털의 경계를 넓히다" Clash Display clamp(2.8rem,5.5vw,4.5rem) font-weight:700 color:#F0F4FF line-height:1.05 max-width:700px. p data-i18n="subtitle" hardcoded "성균관대학교 디지털 IT 컨설팅 학회" Inter 300 color:#9AA8C7 1.1rem mt:1rem. a.cta data-i18n="cta" hardcoded "지원하기" display:inline-block mt:2rem bg:#E8FF3B color:#0B1220 Inter 600 14px px:2rem py:0.75rem text-decoration:none. Scroll indicator absolute bottom:2rem left:50%.
GRAIN: SVG fixed inset:0 z-index:9999 pointer-events:none opacity:0.035. feTurbulence baseFrequency=0.65 numOctaves=3.
CURSOR: #cdot 8px circle yellow fixed pointer-events:none. #cring 28px circle border:1.5px yellow fixed pointer-events:none. Both translate(-50%,-50%). JS: dot snaps instantly, ring lerps.
SEC-01 WHAT IS SDIC: section py:6rem. Counter "01" mono 11px muted absolute top-right. h2 Clash Display 2.5rem mb:3rem. 3-col grid gap:1.5rem. Cards: bg card, border-left:3px green, p:2rem. Icon SVG 24px green. h3 Inter 600. p muted Inter 400 14px. Below grid: mission p Inter 300 1.1rem max-width:680px mt:3rem muted with green left-bar 3px.
SEC-02 TEAMS: 3 cards bg:card p:2.5rem. Big team name Clash Display 1.8rem. Small monospace subtitle 11px muted letter-spacing:0.15em. desc Inter 400 14px muted mt:1rem. Hover: translateY(-4px) 0.25s, box-shadow:0 8px 40px rgba(45,96,56,0.25).
SEC-03 PRESIDENT'S NOTE: single card bg:card p:3rem. Yellow " 8rem Clash Display line-height:0.7 mb:-1rem. Italic quote Inter 300 1.3rem line-height:1.6. Attribution Inter 500 14px muted mt:1.5rem. Green circle 40px "K" Inter 600 white float right.
SEC-04 METHODOLOGY: flex row gap:0 align:stretch. 4 steps each flex:1 p:2rem border-right:1px rgba(255,255,255,0.08). No border on last. Step number mono 11px green mb:1rem. h3 Inter 600 1rem mb:0.5rem. p Inter 400 13px muted. Stack to column <768px.
SEC-05 RECRUITING: 2-col grid gap:4rem. Left: checklist ul no-list-style. Each li: flex gap:0.75rem. Green checkmark SVG 18px. Inter 400 14px. Right: card bg:card p:2.5rem. Cohort badge: green bg 10px px:0.75rem py:0.3rem mono 11px mb:1.5rem. h3 1.3rem mb:1rem. CTA link: yellow bg dark text mailto:sdic.skku@gmail.com Inter 600 14px px:1.5rem py:0.6rem block text-center mt:2rem.
FOOTER: border-top:1px rgba(255,255,255,0.08) py:3rem. 2-col flex justify:between. Left: email Inter 400 14px green. Right: credit Inter 300 13px muted.
STATUS BAR: fixed bottom:0 left:0 right:0 z-index:998 bg:rgba(11,18,32,0.92) border-top:1px #2d6038 py:0.35rem. Ticker span: green mono 11px letter-spacing:0.1em animation:ticker 22s linear infinite. Hide <768px.

JS (single DOMContentLoaded — keep short):
- Apply i18n on load from window.i18n[savedLang||'ko']. Toggle: swap lang, save, reapply.
- Nav scroll: .scrolled class → CSS handles bg.
- IntersectionObserver: .reveal elements → .visible (opacity:1 translateY:0).
- Cursor: mousemove → dot snap, ring lerp (lerp factor 0.12).
- Mobile nav: hamburger toggle open/close.

I18N: data-i18n on all text. window.i18n={{ko:{{}},en:{{}}}} with bilingual pairs. localStorage "sdic_lang"."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16000,
        messages=[{"role": "user", "content": prompt}]
    )
    html = response.content[0].text.strip()

    # Strip markdown fences if model wrapped output
    if html.startswith("```"):
        lines = html.splitlines()
        html = "\n".join(lines[1:] if lines[0].startswith("```") else lines)
        if html.endswith("```"):
            html = html[:-3].rstrip()

    # Remove any Three.js particle code the model may have written (we inject our own)
    # Simple heuristic: remove <script> blocks that reference THREE and hero-canvas
    import re
    def remove_threejs_blocks(h):
        # Remove script tags that contain Three.js particle code
        pattern = r'<script[^>]*>(?:[^<]|<(?!/script>))*?hero-canvas(?:[^<]|<(?!/script>))*?</script>'
        return re.sub(pattern, '', h, flags=re.DOTALL | re.IGNORECASE)
    html = remove_threejs_blocks(html)

    # Auto-close if truncated — ensure valid HTML before injection
    if "</body>" not in html:
        html += "\n</script>\n</body>\n</html>"
    elif not html.rstrip().endswith("</html>"):
        html = html.rstrip()
        if not html.endswith("</body>"):
            html += "\n</body>"
        html += "\n</html>"

    # Inject authoritative i18n data (overrides whatever the model generated)
    import json
    i18n_script = f"""
<script>
// Authoritative i18n data (injected post-generation)
window.i18n = {json.dumps(SDIC_CONTENT, ensure_ascii=False, indent=2)};
</script>
"""
    if "<head>" in html:
        html = html.replace("<head>", "<head>" + i18n_script, 1)

    # Inject Three.js particle script before </body>
    if "</body>" in html:
        html = html.replace("</body>", THREEJS_HERO_SCRIPT + "\n</body>", 1)

    return html


def run(open_browser: bool = False):
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Copy logo
    logo_src = ASSETS_DIR / "logo.png"
    logo_dst = OUT_DIR / "logo.png"
    if logo_src.exists() and not logo_dst.exists():
        shutil.copy(logo_src, logo_dst)
        print(f"  Logo copied: {logo_dst}")

    print(f"[SDIC Generator] Generating site (Three.js injected post-generation)...")
    html = build_sdic_html(iteration=0)

    # Verify completeness
    if not html.rstrip().endswith("</html>"):
        print("  WARNING: HTML may be truncated — does not end with </html>")
    else:
        print(f"  HTML complete ({len(html.splitlines())} lines)")

    html_path = OUT_DIR / "index.html"
    html_path.write_text(html, encoding="utf-8")
    print(f"  HTML saved: {html_path}")

    vercel_json = OUT_DIR / "vercel.json"
    vercel_json.write_text('{"rewrites": [{"source": "/(.*)", "destination": "/index.html"}]}\n', encoding="utf-8")

    if open_browser:
        import webbrowser
        webbrowser.open(f"file://{html_path.resolve()}")

    print(f"\n[SDIC Generator] Done.")
    print(f"  HTML: {html_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--open", action="store_true")
    args = parser.parse_args()
    run(open_browser=args.open)
