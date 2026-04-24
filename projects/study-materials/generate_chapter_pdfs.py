"""
Generate one PDF (or HTML fallback) per chapter from Korean economics summaries.
Tries: weasyprint -> pdfkit -> HTML fallback
"""

import os
import re
import sys

# ── paths ─────────────────────────────────────────────────────────────────────
BASE = r"C:\Users\keonh\OneDrive\바탕 화면\MCP_Agentic AI\projects\study-materials"
SOURCES = [
    os.path.join(BASE, "경제학개론_chapter_summaries_1-3.md"),
    os.path.join(BASE, "경제학개론_chapter_summaries_4-6.md"),
    os.path.join(BASE, "경제학개론_chapter_summaries_7-9.md"),
]
OUT_DIR = os.path.join(BASE, "summaries_pdf")
os.makedirs(OUT_DIR, exist_ok=True)

# ── chapter name map ──────────────────────────────────────────────────────────
CHAPTER_NAMES = {
    1: "제1장", 2: "제2장", 3: "제3장",
    4: "제4장", 5: "제5장", 6: "제6장",
    7: "제7장", 8: "제8장", 9: "제9장",
}

# ── CSS ───────────────────────────────────────────────────────────────────────
CSS = """
@page { size: A4; margin: 2cm; }
body {
    font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
    font-size: 11px;
    line-height: 1.6;
    color: #212121;
}
h2 {
    font-size: 18px;
    color: #1a237e;
    border-bottom: 2px solid #1a237e;
    padding-bottom: 6px;
    margin-top: 0;
}
h3 {
    font-size: 14px;
    color: #283593;
    margin-top: 16px;
    margin-bottom: 6px;
}
h4 {
    font-size: 12px;
    color: #37474f;
    margin-top: 12px;
    margin-bottom: 4px;
}
strong { color: #c62828; }
table {
    border-collapse: collapse;
    width: 100%;
    margin: 10px 0;
    font-size: 10px;
}
th, td {
    border: 1px solid #bdbdbd;
    padding: 5px 8px;
    text-align: left;
}
th { background: #e8eaf6; color: #1a237e; font-weight: bold; }
tr:nth-child(even) td { background: #f5f5f5; }
tr:nth-child(odd) td { background: #ffffff; }
pre, code {
    background: #f5f5f5;
    padding: 8px;
    font-size: 10px;
    font-family: 'Courier New', monospace;
    white-space: pre-wrap;
    border-radius: 3px;
}
ul, ol { padding-left: 20px; margin: 6px 0; }
li { margin-bottom: 3px; }
blockquote {
    background: #fff3e0;
    border-left: 4px solid #ff6f00;
    padding: 12px;
    margin: 8px 0;
}
/* trap/caution sections */
.trap-box {
    background: #fff3e0;
    border-left: 4px solid #ff6f00;
    padding: 12px;
    margin: 10px 0;
}
"""

# ── markdown → HTML (minimal, no extra deps) ─────────────────────────────────
def md_to_html(md: str) -> str:
    lines = md.split("\n")
    html_lines = []
    in_table = False
    in_code = False
    table_header_done = False

    for line in lines:
        # fenced code blocks
        if line.strip().startswith("```"):
            if not in_code:
                in_code = True
                html_lines.append("<pre><code>")
            else:
                in_code = False
                html_lines.append("</code></pre>")
            continue
        if in_code:
            html_lines.append(line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
            continue

        # tables
        if line.strip().startswith("|"):
            if not in_table:
                in_table = True
                table_header_done = False
                html_lines.append('<table>')
            # separator row
            if re.match(r'^\|[\s\-|:]+\|$', line.strip()):
                table_header_done = True
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            tag = "th" if not table_header_done else "td"
            row = "".join(f"<{tag}>{apply_inline(c)}</{tag}>" for c in cells)
            html_lines.append(f"<tr>{row}</tr>")
            continue
        else:
            if in_table:
                html_lines.append("</table>")
                in_table = False
                table_header_done = False

        # headings
        if line.startswith("#### "):
            html_lines.append(f"<h4>{apply_inline(line[5:])}</h4>")
        elif line.startswith("### "):
            html_lines.append(f"<h3>{apply_inline(line[4:])}</h3>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{apply_inline(line[3:])}</h2>")
        elif line.startswith("# "):
            html_lines.append(f"<h1>{apply_inline(line[2:])}</h1>")
        # horizontal rule
        elif line.strip() in ("---", "***", "___"):
            html_lines.append("<hr>")
        # list items
        elif re.match(r'^\s{0,3}[-*+] ', line):
            content = re.sub(r'^\s{0,3}[-*+] ', '', line)
            # simple: wrap in <li> (no nested ul handling needed for this content)
            html_lines.append(f"<li>{apply_inline(content)}</li>")
        elif re.match(r'^\s{0,3}\d+\. ', line):
            content = re.sub(r'^\s{0,3}\d+\. ', '', line)
            html_lines.append(f"<li>{apply_inline(content)}</li>")
        # blank line
        elif line.strip() == "":
            html_lines.append("")
        else:
            html_lines.append(f"<p>{apply_inline(line)}</p>")

    if in_table:
        html_lines.append("</table>")
    return "\n".join(html_lines)


def apply_inline(text: str) -> str:
    """Apply inline markdown: bold, italic, code, links."""
    # escape HTML first (except we need to handle ** etc.)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # bold+italic ***text***
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    # bold **text**
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # italic *text*
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    # inline code `text`
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    return text


# ── wrap in full HTML document ────────────────────────────────────────────────
def make_html_doc(body_html: str, title: str) -> str:
    # detect trap/caution sections and wrap them
    # sections whose h3 contains "함정 포인트" get a special box
    body_html = re.sub(
        r'(<h3>[^<]*함정 포인트[^<]*</h3>)',
        r'<div class="trap-box">\1',
        body_html
    )
    # close trap box before next h3 or h2
    body_html = re.sub(
        r'(</div class="trap-box">)?(<h[23]>)',
        lambda m: ('</div>' if '</div class="trap-box">' not in (m.group(0) or '') else '') + m.group(2),
        body_html
    )
    # simpler: just append </div> at end if trap-box was opened
    if 'class="trap-box"' in body_html:
        body_html += "</div>"

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
{CSS}
</style>
</head>
<body>
{body_html}
</body>
</html>
"""


# ── split markdown into chapters ──────────────────────────────────────────────
def split_chapters(md: str) -> dict:
    """Return {chapter_num: markdown_text} dict."""
    # Split on ## 제N장 headers
    pattern = re.compile(r'^(## 제(\d+)장.*)', re.MULTILINE)
    matches = list(pattern.finditer(md))
    chapters = {}
    for i, m in enumerate(matches):
        num = int(m.group(2))
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        chapters[num] = md[start:end].strip()
    return chapters


# ── load all chapters ─────────────────────────────────────────────────────────
all_chapters = {}
for src in SOURCES:
    with open(src, encoding="utf-8") as f:
        content = f.read()
    all_chapters.update(split_chapters(content))

print(f"Loaded {len(all_chapters)} chapters: {sorted(all_chapters.keys())}")


# ── attempt PDF generation ────────────────────────────────────────────────────
def try_weasyprint(html_path: str, pdf_path: str) -> bool:
    try:
        from weasyprint import HTML
        HTML(filename=html_path).write_pdf(pdf_path)
        return True
    except Exception as e:
        print(f"  weasyprint failed: {e}")
        return False


def try_pdfkit(html_path: str, pdf_path: str) -> bool:
    try:
        import pdfkit
        pdfkit.from_file(html_path, pdf_path)
        return True
    except Exception as e:
        print(f"  pdfkit failed: {e}")
        return False


# ── main loop ─────────────────────────────────────────────────────────────────
results = []

for num in sorted(all_chapters.keys()):
    md_text = all_chapters[num]
    title = f"경제학개론 {CHAPTER_NAMES[num]} 요약"
    body_html = md_to_html(md_text)
    full_html = make_html_doc(body_html, title)

    # write HTML temp file
    html_path = os.path.join(OUT_DIR, f"경제학개론_{CHAPTER_NAMES[num]}_요약.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    pdf_path = os.path.join(OUT_DIR, f"경제학개론_{CHAPTER_NAMES[num]}_요약.pdf")

    print(f"\nChapter {num}: {title}")
    print(f"  HTML written: {html_path}")

    # try weasyprint
    if try_weasyprint(html_path, pdf_path):
        print(f"  PDF (weasyprint): {pdf_path}")
        results.append(("pdf", pdf_path))
        os.remove(html_path)  # clean up temp HTML
        continue

    # try pdfkit
    if try_pdfkit(html_path, pdf_path):
        print(f"  PDF (pdfkit): {pdf_path}")
        results.append(("pdf", pdf_path))
        os.remove(html_path)
        continue

    # fallback: keep HTML
    print(f"  Fallback HTML saved: {html_path}")
    results.append(("html", html_path))


# ── summary ───────────────────────────────────────────────────────────────────
print("\n" + "="*60)
fmt_counts = {}
for fmt, _ in results:
    fmt_counts[fmt] = fmt_counts.get(fmt, 0) + 1

print(f"Done. {len(results)} files generated.")
for fmt, count in fmt_counts.items():
    print(f"  {fmt.upper()}: {count} files")
print(f"\nOutput directory: {OUT_DIR}")
print("\nFiles:")
for fmt, path in results:
    print(f"  [{fmt.upper()}] {os.path.basename(path)}")
