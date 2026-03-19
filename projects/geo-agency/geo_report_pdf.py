"""
GEO Audit PDF Report Generator

Takes a GEO audit dict (from audit_single_company or audit_company_geo)
and produces a professional 2-page PDF report for client delivery.

Usage:
    from geo_report_pdf import generate_pdf
    pdf_path = generate_pdf(audit_result, recommendations)
"""

import os
import re
import sys
import json
from pathlib import Path
from datetime import date

# --- env loading ---
for _p in [
    Path(__file__).parent / ".env",
    Path(__file__).parent.parent / ".env",
    Path(__file__).parent.parent.parent / ".env",
]:
    if _p.exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=_p)
        break

try:
    from fpdf import FPDF
except ImportError:
    print("fpdf2 not installed. Run: pip install fpdf2")
    sys.exit(1)


# --- Colors (RGB) ---
DARK = (30, 30, 30)
ACCENT = (37, 99, 235)       # blue
LIGHT_GRAY = (245, 245, 245)
MID_GRAY = (156, 163, 175)
WHITE = (255, 255, 255)
GREEN = (34, 197, 94)
YELLOW = (234, 179, 8)
RED = (239, 68, 68)


def _score_color(score: int):
    if score >= 70:
        return GREEN
    elif score >= 40:
        return YELLOW
    return RED


def _clean(text: str) -> str:
    """Strip markdown before inserting into PDF."""
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*{1,2}([^*\n]+)\*{1,2}', r'\1', text)
    text = re.sub(r'(\[\d+\])+', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    return text.strip()


def _get_font_path() -> str | None:
    """Find a Unicode font that supports Korean on Windows."""
    candidates = [
        r"C:\Windows\Fonts\malgun.ttf",       # 맑은 고딕
        r"C:\Windows\Fonts\NanumGothic.ttf",
        r"C:\Windows\Fonts\gulim.ttc",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


_UNICODE_FONT = _get_font_path()
_FONT_NAME = "KorFont"


class GeoPDF(FPDF):
    def __init__(self):
        super().__init__()
        if _UNICODE_FONT:
            self.add_font(_FONT_NAME, "", _UNICODE_FONT, uni=True)
            self.add_font(_FONT_NAME, "B", _UNICODE_FONT, uni=True)
            self.add_font(_FONT_NAME, "I", _UNICODE_FONT, uni=True)
        self._base_font = _FONT_NAME if _UNICODE_FONT else "Helvetica"

    def _set_font(self, style: str = "", size: int = 10):
        self.set_font(self._base_font, style, size)

    def header(self):
        pass

    def footer(self):
        self.set_y(-12)
        self._set_font("", 8)
        self.set_text_color(*MID_GRAY)
        self.cell(0, 5, f"GEO Audit Report — Generated {date.today().isoformat()} | Confidential", align="C")


def _bar(pdf: GeoPDF, label: str, score: int, max_score: int, x: float, y: float, w: float = 110):
    """Draw a labeled progress bar."""
    pct = score / max_score if max_score else 0
    bar_h = 6
    color = _score_color(int(score / max_score * 100)) if max_score else MID_GRAY

    pdf.set_xy(x, y)
    pdf._set_font("", 9)
    pdf.set_text_color(*DARK)
    pdf.cell(50, bar_h, label)

    # Background track
    pdf.set_fill_color(*LIGHT_GRAY)
    pdf.rect(x + 52, y + 1, w, bar_h - 2, "F")

    # Fill
    pdf.set_fill_color(*color)
    fill_w = max(1, pct * w)
    pdf.rect(x + 52, y + 1, fill_w, bar_h - 2, "F")

    # Score label
    pdf.set_xy(x + 52 + w + 3, y)
    pdf._set_font("B", 9)
    pdf.cell(20, bar_h, f"{score}/{max_score}")


def generate_pdf(audit: dict, recommendations: list[str] | None = None, before_text: str = "", output_dir: str | None = None) -> str:
    """
    Generate a 2-page GEO audit PDF report.

    Args:
        audit: dict from audit_single_company() or audit_company_geo()
        recommendations: list of 3 recommendation strings (plain text)
        before_text: what AI currently says about the company (Perplexity response)
        output_dir: where to save the PDF (defaults to projects/geo-agency/reports/)

    Returns:
        Path to the generated PDF file
    """
    corp_name = audit.get("corp_name", "Company")
    geo_score = audit.get("geo_score", 0)
    breakdown = audit.get("geo_breakdown", {})
    citability = breakdown.get("citability", 0)
    crawler = breakdown.get("crawler_access", 0)
    brand = breakdown.get("brand_mention", 0)
    website = audit.get("website_url") or "Not found"

    if recommendations is None:
        recommendations = [
            "Add structured FAQ section to website with clear product/service descriptions",
            "Update robots.txt to allow GPTBot, ClaudeBot, and PerplexityBot",
            "Create a dedicated 'About' page with specific, factual claims about your business",
        ]

    # --- Setup ---
    pdf = GeoPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_margins(18, 18, 18)

    # =====================
    # PAGE 1
    # =====================

    # Header bar
    pdf.set_fill_color(*ACCENT)
    pdf.rect(0, 0, 210, 22, "F")
    pdf.set_xy(18, 6)
    pdf._set_font("B", 13)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 10, "GEO Audit Report")
    pdf.set_xy(130, 6)
    pdf._set_font("", 9)
    pdf.cell(0, 10, "Generative Engine Optimization", align="R")

    # Company name
    pdf.set_xy(18, 28)
    pdf._set_font("B", 20)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 10, corp_name[:40])
    pdf.ln(10)

    # Website
    pdf.set_x(18)
    pdf._set_font("", 9)
    pdf.set_text_color(*MID_GRAY)
    pdf.cell(0, 6, f"Website: {website}")
    pdf.ln(6)
    pdf.ln(3)

    # Score
    score_color = _score_color(geo_score)
    label_text = "Low" if geo_score < 40 else ("Medium" if geo_score < 70 else "High")

    pdf.set_xy(18, pdf.get_y())
    pdf._set_font("B", 36)
    pdf.set_text_color(*score_color)
    pdf.cell(30, 18, f"{geo_score}")
    pdf._set_font("", 11)
    pdf.set_text_color(*DARK)
    pdf.set_xy(50, pdf.get_y() + 2)
    pdf.cell(0, 6, f"/ 100  -  AI Visibility: {label_text}")
    pdf.ln(8)
    pdf.ln(2)

    # Divider
    pdf.set_draw_color(*MID_GRAY)
    pdf.line(18, pdf.get_y(), 192, pdf.get_y())
    pdf.ln(5)

    # Score breakdown bars
    pdf._set_font("B", 10)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 6, "Score Breakdown")
    pdf.ln(6)
    pdf.ln(2)

    schema = breakdown.get("schema_org", 0)
    llms = breakdown.get("llms_txt", 0)
    korean = breakdown.get("korean_presence", 0)
    sov = breakdown.get("share_of_voice", 0)

    _bar(pdf, "AI Citability", citability, 40, 18, pdf.get_y())
    pdf.ln(9)
    _bar(pdf, "Crawler Access", crawler, 30, 18, pdf.get_y())
    pdf.ln(9)
    _bar(pdf, "Brand Mention", brand, 30, 18, pdf.get_y())
    pdf.ln(9)
    _bar(pdf, "Schema.org", schema, 20, 18, pdf.get_y())
    pdf.ln(9)
    _bar(pdf, "llms.txt", llms, 10, 18, pdf.get_y())
    pdf.ln(9)
    _bar(pdf, "Korean Presence", korean, 20, 18, pdf.get_y())
    pdf.ln(9)
    _bar(pdf, "Share of Voice", sov, 10, 18, pdf.get_y())
    pdf.ln(12)

    # Divider
    pdf.line(18, pdf.get_y(), 192, pdf.get_y())
    pdf.ln(5)

    # What is GEO box
    pdf.set_fill_color(*LIGHT_GRAY)
    pdf.set_xy(18, pdf.get_y())
    box_y = pdf.get_y()
    pdf._set_font("B", 10)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 7, "  What is GEO?")
    pdf.ln(7)
    pdf._set_font("", 9)
    pdf.set_x(18)
    pdf.multi_cell(
        174, 5,
        "Generative Engine Optimization (GEO) makes your business visible to AI systems like ChatGPT, "
        "Perplexity, and Claude. When customers ask AI for recommendations, GEO-optimized businesses "
        "get cited. This is the next generation of digital marketing.",
        border=0
    )
    pdf.rect(18, box_y, 174, pdf.get_y() - box_y, "DF")
    pdf.ln(5)

    # Current AI visibility
    if before_text:
        pdf._set_font("B", 10)
        pdf.set_text_color(*DARK)
        pdf.cell(0, 6, "Current AI Visibility (what AI says about you today)")
        pdf.ln(6)
        pdf._set_font("", 9)
        pdf.set_text_color(*MID_GRAY)
        snippet = _clean(before_text)[:350] + ("..." if len(before_text) > 350 else "")
        pdf.multi_cell(174, 5, f'"{snippet}"')
        pdf.ln(3)

    # =====================
    # PAGE 2
    # =====================
    pdf.add_page()

    # Header bar
    pdf.set_fill_color(*ACCENT)
    pdf.rect(0, 0, 210, 22, "F")
    pdf.set_xy(18, 6)
    pdf._set_font("B", 13)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 10, f"{corp_name} - Recommendations & Next Steps")

    pdf.set_xy(18, 28)

    # Recommendations
    pdf._set_font("B", 12)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 8, "3 Actions to Improve Your AI Visibility")
    pdf.ln(8)
    pdf.ln(2)

    for i, rec in enumerate(recommendations[:3], 1):
        rec_clean = _clean(rec)
        pdf.set_fill_color(*ACCENT)
        pdf.set_xy(18, pdf.get_y())
        y_rec = pdf.get_y()
        pdf._set_font("B", 10)
        pdf.set_text_color(*WHITE)
        pdf.cell(8, 8, str(i), align="C", fill=True)
        pdf.set_xy(30, y_rec)
        pdf._set_font("", 10)
        pdf.set_text_color(*DARK)
        pdf.multi_cell(162, 6, rec_clean)
        pdf.ln(3)

    pdf.ln(4)
    pdf.line(18, pdf.get_y(), 192, pdf.get_y())
    pdf.ln(6)

    # Expected improvement
    new_score = min(100, geo_score + 30)
    pdf._set_font("B", 10)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 6, "Expected Impact After Optimization")
    pdf.ln(6)
    pdf.ln(2)

    pdf._set_font("", 9)
    pdf.set_text_color(*MID_GRAY)
    pdf.cell(50, 6, "Current GEO Score:")
    pdf._set_font("B", 9)
    pdf.set_text_color(*_score_color(geo_score))
    pdf.cell(0, 6, f"{geo_score}/100")
    pdf.ln(6)

    pdf._set_font("", 9)
    pdf.set_text_color(*MID_GRAY)
    pdf.cell(50, 6, "Projected Score:")
    pdf._set_font("B", 9)
    pdf.set_text_color(*_score_color(new_score))
    pdf.cell(0, 6, f"{new_score}/100 (estimated)")
    pdf.ln(6)

    pdf.ln(6)
    pdf.line(18, pdf.get_y(), 192, pdf.get_y())
    pdf.ln(6)

    # Next steps CTA
    pdf.set_fill_color(*ACCENT)
    pdf.set_text_color(*WHITE)
    pdf._set_font("B", 11)
    cta_y = pdf.get_y()
    pdf.set_xy(18, cta_y)
    pdf.cell(174, 10, "Next Steps", align="C", fill=True)
    pdf.ln(10)

    pdf.set_fill_color(*LIGHT_GRAY)
    pdf.set_text_color(*DARK)
    pdf._set_font("", 10)
    pdf.set_x(18)
    pdf.multi_cell(
        174, 6,
        "1. Schedule a 30-minute strategy call to review these findings\n"
        "2. We implement all 3 recommendations (estimated 1 week)\n"
        "3. Re-audit in 30 days to measure improvement\n\n"
        "Contact: Keonhee Kim  |  SKKU Business Administration  |  AI Consulting Specialist",
        border=0,
        fill=True
    )

    # --- Save ---
    if output_dir is None:
        output_dir = Path(__file__).parent / "reports"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r'[^\w\-]', '_', corp_name)
    output_path = Path(output_dir) / f"geo_audit_{safe_name}_{date.today().isoformat()}.pdf"
    pdf.output(str(output_path))
    print(f"PDF saved: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    # Quick test
    sample_audit = {
        "corp_name": "현대모비스",
        "geo_score": 55,
        "geo_breakdown": {"citability": 30, "crawler_access": 15, "brand_mention": 10},
        "website_url": "https://www.mobis.co.kr",
    }
    sample_recs = [
        "robots.txt에 GPTBot, ClaudeBot, PerplexityBot 허용 규칙 추가",
        "홈페이지 제품 페이지에 구조화된 FAQ 섹션 추가 (질문-답변 형식)",
        "회사 소개 페이지에 구체적인 수치와 사실 기반 문장 추가 (예: '연간 XX만 대 부품 공급')",
    ]
    path = generate_pdf(sample_audit, sample_recs, before_text="현대모비스에 대한 정보가 충분하지 않습니다.")
    print(f"Generated: {path}")
