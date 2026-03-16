import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

F = 'Times New Roman'
doc = Document()

for section in doc.sections:
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

doc.styles['Normal'].font.name = F
doc.styles['Normal'].font.size = Pt(11)
doc.styles['Normal'].paragraph_format.space_before = Pt(0)
doc.styles['Normal'].paragraph_format.space_after = Pt(0)


def p_right_tab(doc, space_before=0, space_after=0):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    pPr = p._p.get_or_add_pPr()
    tabs = OxmlElement('w:tabs')
    tab = OxmlElement('w:tab')
    tab.set(qn('w:val'), 'right')
    tab.set(qn('w:pos'), '8640')
    tabs.append(tab)
    pPr.append(tabs)
    return p


def add_bottom_border(p):
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    pBdr.append(bottom)
    pPr.append(pBdr)


def add_top_border(p):
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    top = OxmlElement('w:top')
    top.set(qn('w:val'), 'single')
    top.set(qn('w:sz'), '6')
    top.set(qn('w:space'), '1')
    pBdr.append(top)
    pPr.append(pBdr)


def run(p, text, bold=False, italic=False, size=11):
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    r.font.name = F
    r.font.size = Pt(size)
    return r


def hyperlink(para, text, url, size=10.5):
    part = para.part
    r_id = part.relate_to(
        url,
        'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',
        is_external=True
    )
    hl = OxmlElement('w:hyperlink')
    hl.set(qn('r:id'), r_id)
    r = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    color = OxmlElement('w:color')
    color.set(qn('w:val'), '0563C1')
    rPr.append(color)
    u = OxmlElement('w:u')
    u.set(qn('w:val'), 'single')
    rPr.append(u)
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), F)
    rFonts.set(qn('w:hAnsi'), F)
    rPr.append(rFonts)
    sz = OxmlElement('w:sz')
    sz.set(qn('w:val'), str(int(size * 2)))
    rPr.append(sz)
    r.append(rPr)
    t = OxmlElement('w:t')
    t.text = text
    r.append(t)
    hl.append(r)
    para._p.append(hl)


def bullet(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    if bold_prefix:
        run(p, bold_prefix, bold=True, size=10.5)
    run(p, text, size=10.5)
    return p


def bullet_with_link(doc, text_before, link_text, url, text_after='', bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    if bold_prefix:
        run(p, bold_prefix, bold=True, size=10.5)
    run(p, text_before, size=10.5)
    hyperlink(p, link_text, url, size=10.5)
    if text_after:
        run(p, text_after, size=10.5)
    return p


def section_header(doc, text, space_before=8):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(2)
    add_top_border(p)
    run(p, text, bold=True, size=11)


# NAME
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(2)
run(p, 'Keonhee Kim', bold=True, size=16)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(0)
run(p, 'Seoul, South Korea | (+82) 010-5704-4832 | keonhee3337@gmail.com | Availability: Mar \u2013 Sep 10', size=10)
add_bottom_border(p)

# EDUCATION
section_header(doc, 'EDUCATION', space_before=6)

p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(2)
p.paragraph_format.space_after = Pt(0)
run(p, 'Sungkyunkwan University (SKKU)', bold=True, size=11)
run(p, ' | Seoul, South Korea', size=11)

p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(0)
run(p, 'Bachelor of Business Administration | ', size=11)
run(p, 'Mar 2020 \u2013 Present (Expected Feb 2027)', italic=True, size=11)

bullet(doc, 'GPA: 3.7 / 4.5')
bullet(doc, 'Strategic Management, Corporate Finance, Data Analytics', bold_prefix='Relevant Coursework: ')
bullet(doc, 'Financial Modeling, K-GAAP, Cost Accounting (Jan 2024 \u2013 Jun 2025)', bold_prefix='Advanced Training: ')

# PROJECT & TECHNICAL EXPERIENCE
section_header(doc, 'PROJECT & TECHNICAL EXPERIENCE')

# SKKU-Deloitte
p = p_right_tab(doc, space_before=2)
run(p, 'SKKU\u2013Deloitte AI/IT Consulting Society | Founder & President', bold=True, size=11)
run(p, '\t')
run(p, 'Sep 2025 \u2013 Present', italic=True, size=10)

bullet(doc, 'Founded SKKU\u2019s first AI/IT consulting body; structured a formal MOU and internship pipeline with Deloitte Partners, bridging business management with applied IT practice.')
bullet(doc, 'Designed and deployed an AI-powered applicant screening pipeline: Gmail \u2192 PDF extraction \u2192 Claude API auto-grading (0\u2013100) \u2192 Google Sheets, eliminating manual review and enabling real-time scoring at scale.')
bullet(doc, 'Designed competency-based L&D curriculum (Strategy \u2192 Implementation), accelerating analyst readiness by 40% across the pilot cohort.')

# Enterprise RAG
p = p_right_tab(doc, space_before=3)
run(p, 'Enterprise RAG Demo', bold=True, size=11)
run(p, ' | Personal Project', italic=True, size=11)
run(p, '\t')
run(p, 'Mar 2025 \u2013 Present', italic=True, size=10)

bullet_with_link(
    doc,
    'Built a production-grade RAG system: FastAPI backend + Pinecone vector DB + Supabase (conversation history) + GPT-4o \u2014 deployed live at ',
    'web-production-e3a16.up.railway.app',
    'https://web-production-e3a16.up.railway.app',
    '.'
)
bullet(doc, 'Implemented end-to-end document ingestion: chunking, OpenAI embedding, upsert to Pinecone, and semantic retrieval \u2014 grounding all responses in source documents.')

# FinAgent
p = p_right_tab(doc, space_before=3)
run(p, 'FinAgent \u2014 Multi-Agent Financial Analysis System', bold=True, size=11)
run(p, ' | Personal Project', italic=True, size=11)
run(p, '\t')
run(p, 'Jan 2026 \u2013 Present', italic=True, size=10)

bullet_with_link(
    doc,
    'Architected a LangGraph StateGraph pipeline routing queries across three specialized agents: RAG, Text2SQL, and orchestration \u2014 deployed live at ',
    'keonhee-finagent.streamlit.app',
    'https://keonhee-finagent.streamlit.app',
    '.'
)
bullet(doc, 'Built a custom VectorDB from scratch using OpenAI text-embedding-3-small with cosine similarity; engineered the full retrieval layer independently after determining ChromaDB was incompatible with Python 3.14.')
bullet(doc, 'Implemented Text2SQL agent pairing GPT-4o with SQLite for natural-language querying of live financial data.')

# Samsung
p = p_right_tab(doc, space_before=3)
run(p, 'Samsung Electronics AI Strategy Engine', bold=True, size=11)
run(p, ' | Personal Project', italic=True, size=11)
run(p, '\t')
run(p, 'Jan 2026 \u2013 Feb 2026', italic=True, size=10)

bullet_with_link(
    doc,
    'Designed an end-to-end financial intelligence platform ingesting 7 years of audited statements via DART-FSS into SQLite; built a RAG + GPT-4o analysis engine \u2014 live at ',
    'keonhee-strategy.streamlit.app',
    'https://keonhee-strategy.streamlit.app',
    '.'
)
bullet(doc, 'Built a macroeconomic shock simulator modelling USD/KRW and SOX Index impacts on operating profit, visualized via Plotly waterfall charts comparable to sell-side sensitivity tables.')

# ADDITIONAL EXPERIENCE
section_header(doc, 'ADDITIONAL EXPERIENCE')

p = p_right_tab(doc, space_before=2)
run(p, 'LG Electronics HR', bold=True, size=11)
run(p, ', Lead Interviewer & Interpreter', italic=True, size=11)
run(p, '\t')
run(p, 'Nov 2025', italic=True, size=10)

bullet(doc, 'Led 45-minute real-time interpretation for LG Electronics HR leadership, facilitating manager-level diagnostics on organizational pain points and strategic outlook.')

p = p_right_tab(doc, space_before=3)
run(p, 'Ensight English Academy & Freelance', bold=True, size=11)
run(p, ', Academic Instructor & Speech Coach', italic=True, size=11)
run(p, '\t')
run(p, 'Sep 2023 \u2013 Mar 2024', italic=True, size=10)

bullet(doc, 'Coached students to the Grand Prize (Daesang) at the National English Speech Contest through a rigorous communication curriculum mirroring executive presentation standards.')

# SKILLS & ADDITIONAL INFORMATION
section_header(doc, 'SKILLS & ADDITIONAL INFORMATION')

bullet(doc, 'Python, SQL, OpenAI API, Claude API, LangGraph, RAG Pipeline, VectorDB (custom), Text2SQL, Prompt Engineering, FastAPI, Streamlit, Pinecone, MCP (Model Context Protocol).', bold_prefix='Technical & Data: ')
bullet(doc, 'English (Native \u2014 16 years overseas; OPIc: AL), Korean (Native); experienced in real-time professional interpretation for LG Electronics HR.', bold_prefix='Languages: ')
bullet(doc, 'Classical Music (Concertmaster for European orchestra), Sports (Varsity Basketball Captain).', bold_prefix='Interests: ')
bullet(doc, 'Republic of Korea Army (Sergeant); Completed Full Term of Service (2023).', bold_prefix='Military Service: ')

doc.save('cv-kearney-ra-v2.docx')
print('Saved.')
