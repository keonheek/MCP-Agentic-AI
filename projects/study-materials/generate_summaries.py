import re
import os

CSS = """
@page { size: A4; margin: 2cm; }
* { box-sizing: border-box; }
body {
    font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', 'NanumGothic', sans-serif;
    font-size: 11.5pt;
    line-height: 1.75;
    color: #212121;
    max-width: 100%;
}
h2 {
    font-size: 17pt;
    color: #1a237e;
    border-bottom: 2.5px solid #1a237e;
    padding-bottom: 6px;
    margin-top: 24px;
    margin-bottom: 12px;
}
h3 {
    font-size: 13pt;
    color: #283593;
    margin-top: 18px;
    margin-bottom: 6px;
    border-left: 3px solid #5c6bc0;
    padding-left: 8px;
}
h4 {
    font-size: 11.5pt;
    color: #37474f;
    margin-top: 12px;
    margin-bottom: 4px;
}
strong { color: #b71c1c; }
p { margin: 5px 0; }
ul, ol { padding-left: 22px; margin: 5px 0; }
li { margin-bottom: 3px; }
table {
    border-collapse: collapse;
    width: 100%;
    margin: 10px 0;
    font-size: 10pt;
}
th, td {
    border: 1px solid #bdbdbd;
    padding: 5px 9px;
    text-align: left;
    vertical-align: top;
}
th { background: #e8eaf6; color: #1a237e; font-weight: bold; }
tr:nth-child(even) td { background: #fafafa; }
pre, code {
    background: #f5f5f5;
    padding: 8px 10px;
    font-size: 9.5pt;
    font-family: 'Courier New', monospace;
    white-space: pre-wrap;
    border-radius: 3px;
    display: block;
    border: 1px solid #e0e0e0;
}
.trap-box {
    background: #fff8e1;
    border-left: 4px solid #f57f17;
    padding: 10px 14px;
    margin: 12px 0;
    border-radius: 2px;
}
.trap-box h3 {
    border-left: none;
    padding-left: 0;
    color: #e65100;
    margin-top: 0;
}
hr { border: none; border-top: 1px solid #e0e0e0; margin: 18px 0; }
"""

def inline(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text

def md_to_html(md):
    lines = md.split('\n')
    html = []
    in_ul = False
    in_ol = False
    in_pre = False
    in_table = False
    in_trap = False
    table_rows = []

    def close_list():
        nonlocal in_ul, in_ol
        if in_ul:
            html.append('</ul>')
            in_ul = False
        if in_ol:
            html.append('</ol>')
            in_ol = False

    def close_table():
        nonlocal in_table, table_rows
        if not in_table:
            return
        rows_html = []
        separator_idx = None
        for ri, row in enumerate(table_rows):
            if re.match(r'^[\s|:-]+$', row.replace('|', '').strip() or '-'):
                separator_idx = ri
                break
        for ri, row in enumerate(table_rows):
            if separator_idx is not None and ri == separator_idx:
                continue
            cols = [c.strip() for c in row.strip('|').split('|')]
            if ri == 0:
                rows_html.append('<tr>' + ''.join('<th>' + inline(c) + '</th>' for c in cols) + '</tr>')
            else:
                rows_html.append('<tr>' + ''.join('<td>' + inline(c) + '</td>' for c in cols) + '</tr>')
        html.append('<table>' + ''.join(rows_html) + '</table>')
        in_table = False
        table_rows.clear()

    i = 0
    while i < len(lines):
        line = lines[i]

        # code block fence
        if line.strip().startswith('```'):
            close_list()
            close_table()
            if not in_pre:
                html.append('<pre>')
                in_pre = True
            else:
                html.append('</pre>')
                in_pre = False
            i += 1
            continue

        if in_pre:
            html.append(line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
            i += 1
            continue

        # table row
        if line.strip().startswith('|'):
            close_list()
            in_table = True
            table_rows.append(line.strip())
            i += 1
            continue
        else:
            close_table()

        # headings
        m = re.match(r'^(#{1,4})\s+(.*)', line)
        if m:
            close_list()
            level = len(m.group(1))
            text = inline(m.group(2))
            tag = 'h' + str(level)
            if '함정' in m.group(2):
                if not in_trap:
                    html.append('<div class="trap-box">')
                    in_trap = True
                html.append('<' + tag + '>' + text + '</' + tag + '>')
            else:
                if in_trap:
                    html.append('</div>')
                    in_trap = False
                html.append('<' + tag + '>' + text + '</' + tag + '>')
            i += 1
            continue

        # hr
        if re.match(r'^-{3,}\s*$', line):
            close_list()
            if in_trap:
                html.append('</div>')
                in_trap = False
            html.append('<hr>')
            i += 1
            continue

        # ordered list
        m = re.match(r'^\d+\.\s+(.*)', line)
        if m:
            if not in_ol:
                close_list()
                html.append('<ol>')
                in_ol = True
            html.append('<li>' + inline(m.group(1)) + '</li>')
            i += 1
            continue

        # unordered list (with optional indent)
        m = re.match(r'^\s*[-*]\s+(.*)', line)
        if m:
            if not in_ul:
                close_list()
                html.append('<ul>')
                in_ul = True
            html.append('<li>' + inline(m.group(1)) + '</li>')
            i += 1
            continue

        # blank line
        if not line.strip():
            close_list()
            i += 1
            continue

        # paragraph
        close_list()
        html.append('<p>' + inline(line) + '</p>')
        i += 1

    close_list()
    close_table()
    if in_trap:
        html.append('</div>')
    if in_pre:
        html.append('</pre>')

    return '\n'.join(html)


chapter_titles = {
    1: '제1장: 경제학의 10대 기본원리',
    2: '제2장: 경제학자처럼 생각하기',
    3: '제3장: 상호의존관계와 교역의 이득',
    4: '제4장: 시장의 수요와 공급',
    5: '제5장: 탄력성',
    6: '제6장: 수요, 공급과 정부정책',
    7: '제7장: 소비자, 생산자, 시장의 효율성',
    8: '제8장: 조세의 경제적 비용',
    9: '제9장: 국제무역',
}

base = r'c:/Users/keonh/OneDrive/바탕 화면/MCP_Agentic AI/projects/study-materials'
source_files = [
    os.path.join(base, '경제학개론_chapter_summaries_1-3.md'),
    os.path.join(base, '경제학개론_chapter_summaries_4-6.md'),
    os.path.join(base, '경제학개론_chapter_summaries_7-9.md'),
]
out_dir = os.path.join(base, 'summaries_pdf')
os.makedirs(out_dir, exist_ok=True)

all_chapters = {}
for sf in source_files:
    content = open(sf, encoding='utf-8').read()
    parts = re.split(r'(?=^## 제\d+장)', content, flags=re.MULTILINE)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        m = re.match(r'^## 제(\d+)장', part)
        if m:
            ch = int(m.group(1))
            all_chapters[ch] = part

for ch in sorted(all_chapters.keys()):
    md = all_chapters[ch]
    title = chapter_titles.get(ch, '제' + str(ch) + '장')
    body_html = md_to_html(md)
    html = (
        '<!DOCTYPE html>\n<html lang="ko">\n<head>\n'
        '<meta charset="UTF-8">\n'
        '<title>경제학 개론 — ' + title + '</title>\n'
        '<style>' + CSS + '</style>\n'
        '</head>\n<body>\n'
        + body_html +
        '\n<p style="margin-top:30px; color:#9e9e9e; font-size:9pt; text-align:right;">경제학 개론 요약 | 숙명여자대학교</p>\n'
        '</body>\n</html>'
    )
    fname = os.path.join(out_dir, '경제학개론_제' + str(ch) + '장_요약.html')
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Written: ' + fname)

print('Done. Total chapters:', len(all_chapters))
