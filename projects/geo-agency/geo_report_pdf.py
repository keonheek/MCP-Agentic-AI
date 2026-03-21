"""
GEO Audit PDF Report Generator — Navy + Teal consulting style

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


# --- Color palette (Navy + Teal consulting style) ---
NAVY = (27, 42, 74)
TEAL = (0, 199, 190)
GREEN = (34, 197, 94)
AMBER = (245, 158, 11)
RED = (239, 68, 68)
SLATE = (100, 116, 139)
LIGHT = (248, 250, 252)
WHITE = (255, 255, 255)
DARK = (15, 23, 42)
DIVIDER = (226, 232, 240)


def _score_color(score: int):
    if score >= 70:
        return GREEN
    elif score >= 40:
        return AMBER
    return RED


def _score_label(score: int) -> str:
    if score >= 70:
        return "High / 높음"
    elif score >= 40:
        return "Medium / 보통"
    return "Low / 낮음"


def _clean(text: str) -> str:
    """Strip markdown and citation markers before inserting into PDF."""
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*{1,2}([^*\n]+)\*{1,2}', r'\1', text)
    text = re.sub(r'(\[\d+\])+', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    return text.strip()


def _get_font_path() -> str | None:
    candidates = [
        r"C:\Windows\Fonts\malgun.ttf",
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

    def _sf(self, style: str = "", size: int = 10):
        """Shorthand for set_font."""
        self.set_font(self._base_font, style, size)

    def header(self):
        pass

    def footer(self):
        self.set_y(-12)
        self._sf("", 7)
        self.set_text_color(*SLATE)
        self.cell(0, 5, f"GEO Audit Report | {date.today().isoformat()} | Confidential / 기밀", align="C")


def _progress_bar(pdf: GeoPDF, score: int, max_score: int, x: float, y: float, w: float = 120):
    """Draw a rounded progress bar (gray track + colored fill)."""
    pct = score / max_score if max_score else 0
    color = _score_color(int(pct * 100))
    h = 8

    # Track
    pdf.set_fill_color(226, 232, 240)
    pdf.rect(x, y, w, h, "F")

    # Fill
    fill_w = max(2, pct * w)
    pdf.set_fill_color(*color)
    pdf.rect(x, y, fill_w, h, "F")

    # Score label right of bar
    pdf._sf("B", 8)
    pdf.set_text_color(*DARK)
    pdf.set_xy(x + w + 3, y)
    pdf.cell(20, h, f"{score}/{max_score}")


def generate_pdf(
    audit: dict,
    recommendations: list[str] | None = None,
    before_text: str = "",
    output_dir: str | None = None,
) -> str:
    """
    Generate a 2-page GEO audit PDF report (Navy + Teal consulting style).

    Returns path to the generated PDF file.
    """
    corp_name = audit.get("corp_name", "Company")
    geo_score = audit.get("geo_score", 0)
    breakdown = audit.get("geo_breakdown", {})
    website = audit.get("website_url") or "Not found"
    sov_competitors = audit.get("sov_competitors", [])
    sov_cited = audit.get("sov_cited", False)

    citability = breakdown.get("citability", 0)
    sov = breakdown.get("share_of_voice", 0)
    ai_bot = breakdown.get("ai_bot_access", breakdown.get("crawler_access", 0))
    ai_policy = breakdown.get("ai_policy_file", breakdown.get("llms_txt", 0))
    org_schema = breakdown.get("org_schema", 0)
    content_schema = breakdown.get("content_schema", 0)
    naver = breakdown.get("naver_presence", 0)
    kr_sync = breakdown.get("kr_platform_sync", 0)
    brand_mention = breakdown.get("brand_mention", 0)
    sentiment = breakdown.get("sentiment_quality", 0)

    content_pct = round((citability + content_schema + brand_mention) / 65 * 100)
    access_pct = round((ai_bot + ai_policy + org_schema) / 45 * 100)
    presence_pct = round((sov + naver + kr_sync + sentiment) / 40 * 100)

    if recommendations is None:
        recommendations = [
            "robots.txt에 GPTBot, ClaudeBot, PerplexityBot 허용 규칙 추가 (Allow AI Crawlers)",
            "홈페이지에 구조화된 FAQ 섹션 추가 — 질문-답변 형식 (Add Structured FAQ)",
            "회사 소개 페이지에 구체적인 수치 추가 (Strengthen About Page with Specifics)",
        ]

    pdf = GeoPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(18, 18, 18)
    pdf.add_page()

    # =====================================================================
    # PAGE 1
    # =====================================================================

    # Full-width Navy header bar
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, 210, 30, "F")
    pdf.set_xy(18, 8)
    pdf._sf("B", 12)
    pdf.set_text_color(*WHITE)
    pdf.cell(120, 7, "GEO Audit Report / AI 가시성 진단")
    pdf.set_xy(18, 16)
    pdf._sf("", 8)
    pdf.set_text_color(*TEAL)
    pdf.cell(174, 6, date.today().strftime("%Y-%m-%d"), align="R")

    # Company name + teal underline
    pdf.set_xy(18, 36)
    pdf._sf("B", 22)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 10, corp_name[:45])
    pdf.ln(11)
    # Teal underline bar
    pdf.set_fill_color(*TEAL)
    pdf.rect(18, pdf.get_y(), 60, 3, "F")
    pdf.ln(7)

    # Website caption
    pdf._sf("", 8)
    pdf.set_text_color(*SLATE)
    pdf.set_x(18)
    pdf.cell(0, 5, f"Website: {website}")
    pdf.ln(10)

    # Score hero block
    score_color = _score_color(geo_score)
    score_label = _score_label(geo_score)
    hero_y = pdf.get_y()

    # Score number
    pdf.set_xy(18, hero_y)
    pdf._sf("B", 52)
    pdf.set_text_color(*score_color)
    pdf.cell(38, 20, str(geo_score))

    # "/ 100" label
    pdf.set_xy(58, hero_y + 8)
    pdf._sf("", 14)
    pdf.set_text_color(*SLATE)
    pdf.cell(20, 10, "/ 100")

    # Colored label badge
    badge_x, badge_y = 85, hero_y + 6
    badge_w, badge_h = 55, 12
    pdf.set_fill_color(*score_color)
    pdf.rect(badge_x, badge_y, badge_w, badge_h, "F")
    pdf._sf("B", 9)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(badge_x, badge_y + 2)
    pdf.cell(badge_w, 8, score_label, align="C")

    # Teal horizontal line under score
    pdf.set_y(hero_y + 22)
    pdf.set_fill_color(*TEAL)
    pdf.rect(18, pdf.get_y(), 174, 2, "F")
    pdf.ln(6)

    # 3-column summary metrics
    summary_y = pdf.get_y()
    col_w = 58
    for i, (metric_en, metric_kr, pct) in enumerate([
        ("Content Quality", "콘텐츠 품질", content_pct),
        ("Technical Access", "기술 접근성", access_pct),
        ("Market Presence", "시장 존재감", presence_pct),
    ]):
        x = 18 + i * col_w
        pdf._sf("", 7)
        pdf.set_text_color(*SLATE)
        pdf.set_xy(x, summary_y)
        pdf.cell(col_w - 2, 5, metric_en)
        pdf.set_xy(x, summary_y + 5)
        pdf._sf("B", 16)
        pdf.set_text_color(*_score_color(pct))
        pdf.cell(col_w - 2, 9, f"{pct}%")
        pdf.set_xy(x, summary_y + 14)
        pdf._sf("", 7)
        pdf.set_text_color(*SLATE)
        pdf.cell(col_w - 2, 5, metric_kr)

    pdf.set_y(summary_y + 22)
    pdf.set_fill_color(*DIVIDER)
    pdf.rect(18, pdf.get_y(), 174, 1, "F")
    pdf.ln(5)

    # Section title: Score Breakdown
    # Teal left border + section label
    section_y = pdf.get_y()
    pdf.set_fill_color(*TEAL)
    pdf.rect(18, section_y, 4, 8, "F")
    pdf._sf("B", 10)
    pdf.set_text_color(*NAVY)
    pdf.set_xy(25, section_y)
    pdf.cell(0, 8, "Score Breakdown / 점수 세부 항목")
    pdf.ln(11)

    # Category cards
    categories = [
        ("Citability & Share of Voice", "AI 인용 가능성 & 점유율", [
            ("Citability", citability, 40),
            ("Share of Voice", sov, 10),
        ]),
        ("Crawler & AI Policy", "AI 크롤러 접근성 & 정책", [
            ("AI Bot Access", ai_bot, 20),
            ("AI Policy File", ai_policy, 10),
        ]),
        ("Schema & Structured Data", "스키마 & 구조화 데이터", [
            ("Org Schema", org_schema, 15),
            ("Content Schema", content_schema, 15),
        ]),
        ("Korean Platform Sync", "네이버 & KR 플랫폼", [
            ("Naver Presence", naver, 10),
            ("KR Platform Sync", kr_sync, 10),
        ]),
        ("Brand & Sentiment", "브랜드 & 감성 품질", [
            ("Brand Mention", brand_mention, 10),
            ("Sentiment Quality", sentiment, 10),
        ]),
    ]

    for cat_en, cat_kr, dims in categories:
        card_y = pdf.get_y()
        card_h = 8 + len(dims) * 13
        pdf.set_fill_color(*LIGHT)
        pdf.rect(18, card_y, 174, card_h, "F")

        # Category name
        pdf.set_xy(22, card_y + 2)
        pdf._sf("B", 9)
        pdf.set_text_color(*NAVY)
        pdf.cell(90, 5, cat_en)

        # Korean subtitle
        pdf.set_xy(22, card_y + 7)
        pdf._sf("", 7)
        pdf.set_text_color(*TEAL)
        pdf.cell(90, 4, cat_kr)

        # Progress bars for each dimension
        for j, (dim_name, dim_score, dim_max) in enumerate(dims):
            bar_y = card_y + 12 + j * 13
            pdf.set_xy(22, bar_y)
            pdf._sf("", 8)
            pdf.set_text_color(*SLATE)
            pdf.cell(45, 8, dim_name)
            _progress_bar(pdf, dim_score, dim_max, 68, bar_y + 1, w=105)

        pdf.set_y(card_y + card_h + 3)

    # Before text quote box
    if before_text:
        pdf.ln(2)
        quote_y = pdf.get_y()
        snippet = _clean(before_text)[:300] + ("..." if len(before_text) > 300 else "")

        # Section label
        section_y2 = pdf.get_y()
        pdf.set_fill_color(*TEAL)
        pdf.rect(18, section_y2, 4, 8, "F")
        pdf._sf("B", 9)
        pdf.set_text_color(*NAVY)
        pdf.set_xy(25, section_y2)
        pdf.cell(0, 8, "What AI says today / 현재 AI 응답")
        pdf.ln(11)

        # Gray quote box with teal left border
        box_y = pdf.get_y()
        pdf.set_fill_color(*LIGHT)
        pdf.rect(18, box_y, 174, 30, "F")
        pdf.set_fill_color(*TEAL)
        pdf.rect(18, box_y, 4, 30, "F")
        pdf.set_xy(25, box_y + 3)
        pdf._sf("I", 8)
        pdf.set_text_color(*DARK)
        pdf.multi_cell(164, 5, f'"{snippet}"', border=0)
        pdf.set_y(box_y + 32)

    # =====================================================================
    # PAGE 2
    # =====================================================================
    pdf.add_page()

    # Navy header bar
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, 210, 30, "F")
    pdf.set_xy(18, 8)
    pdf._sf("B", 11)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 7, f"{corp_name} — Implementation Roadmap / 구현 로드맵")
    pdf.set_xy(18, 16)
    pdf._sf("", 8)
    pdf.set_text_color(*TEAL)
    pdf.cell(174, 6, date.today().strftime("%Y-%m-%d"), align="R")

    pdf.set_y(36)

    # Section: Top 3 Actions
    section_y3 = pdf.get_y()
    pdf.set_fill_color(*TEAL)
    pdf.rect(18, section_y3, 4, 8, "F")
    pdf._sf("B", 11)
    pdf.set_text_color(*NAVY)
    pdf.set_xy(25, section_y3)
    pdf.cell(0, 8, "Top 3 Actions / 우선 실행 사항")
    pdf.ln(12)

    for i, rec in enumerate(recommendations[:3], 1):
        rec_clean = _clean(rec)
        card_y = pdf.get_y()

        # Teal left border on card
        pdf.set_fill_color(*LIGHT)
        pdf.rect(18, card_y, 174, 18, "F")
        pdf.set_fill_color(*TEAL)
        pdf.rect(18, card_y, 4, 18, "F")

        # Navy circle badge
        badge_cx = 30
        pdf.set_fill_color(*NAVY)
        pdf.ellipse(badge_cx - 5, card_y + 4, 10, 10, "F")
        pdf._sf("B", 9)
        pdf.set_text_color(*WHITE)
        pdf.set_xy(badge_cx - 5, card_y + 5)
        pdf.cell(10, 8, str(i), align="C")

        # Rec text
        pdf.set_xy(44, card_y + 3)
        pdf._sf("B", 9)
        pdf.set_text_color(*DARK)
        # Split on " (" to separate Korean from English translation if present
        if " (" in rec_clean and rec_clean.endswith(")"):
            parts = rec_clean.rsplit(" (", 1)
            pdf.cell(148, 6, parts[0][:70])
            pdf.set_xy(44, card_y + 9)
            pdf._sf("I", 8)
            pdf.set_text_color(*SLATE)
            pdf.cell(148, 5, f"({parts[1]}")
        else:
            pdf.multi_cell(148, 5, rec_clean[:120], border=0)

        pdf.set_y(card_y + 21)

    pdf.ln(4)

    # Competitive landscape
    if sov_competitors:
        section_y4 = pdf.get_y()
        pdf.set_fill_color(*TEAL)
        pdf.rect(18, section_y4, 4, 8, "F")
        pdf._sf("B", 10)
        pdf.set_text_color(*NAVY)
        pdf.set_xy(25, section_y4)
        pdf.cell(0, 8, "경쟁사 AI 인용 현황 / Competitive Landscape")
        pdf.ln(12)

        pdf._sf("", 9)
        pdf.set_text_color(*DARK)
        pdf.set_x(18)
        comp_str = ", ".join(sov_competitors[:5])
        pdf.multi_cell(174, 5, f"AI 추천 목록: {comp_str}", border=0)
        pdf.ln(3)

        # Cited badge
        cited_color = GREEN if sov_cited else RED
        cited_label = "귀사 포함됨: Yes" if sov_cited else "귀사 포함됨: No"
        badge_y = pdf.get_y()
        pdf.set_fill_color(*cited_color)
        pdf.rect(18, badge_y, 55, 9, "F")
        pdf._sf("B", 8)
        pdf.set_text_color(*WHITE)
        pdf.set_xy(18, badge_y + 1)
        pdf.cell(55, 7, cited_label, align="C")
        pdf.ln(14)

    # Before -> After score projection
    max_scores = {
        "citability": 40, "share_of_voice": 10,
        "ai_bot_access": 20, "ai_policy_file": 10,
        "org_schema": 15, "content_schema": 15,
        "naver_presence": 10, "kr_platform_sync": 10,
        "brand_mention": 10, "sentiment_quality": 10,
    }
    recoverable_raw = 0
    for dim, max_val in max_scores.items():
        current = breakdown.get(dim, 0)
        if current < max_val * 0.7:
            recoverable_raw += int((max_val - current) * 0.6)
    projected_improvement = round(recoverable_raw / 150 * 100)
    new_score = min(100, geo_score + projected_improvement)

    section_y5 = pdf.get_y()
    pdf.set_fill_color(*TEAL)
    pdf.rect(18, section_y5, 4, 8, "F")
    pdf._sf("B", 10)
    pdf.set_text_color(*NAVY)
    pdf.set_xy(25, section_y5)
    pdf.cell(0, 8, "Score Projection / 예상 점수 향상")
    pdf.ln(12)

    proj_y = pdf.get_y()
    # Before box
    pdf.set_fill_color(*_score_color(geo_score))
    pdf.rect(18, proj_y, 40, 16, "F")
    pdf._sf("B", 14)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(18, proj_y + 3)
    pdf.cell(40, 10, f"{geo_score}", align="C")

    # Arrow
    pdf._sf("B", 14)
    pdf.set_text_color(*SLATE)
    pdf.set_xy(61, proj_y + 4)
    pdf.cell(16, 8, "-->", align="C")

    # After box
    pdf.set_fill_color(*_score_color(new_score))
    pdf.rect(80, proj_y, 40, 16, "F")
    pdf._sf("B", 14)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(80, proj_y + 3)
    pdf.cell(40, 10, f"{new_score}", align="C")

    pdf._sf("", 8)
    pdf.set_text_color(*SLATE)
    pdf.set_xy(124, proj_y + 5)
    pdf.cell(0, 6, "(estimated after full implementation)")

    pdf.set_y(proj_y + 22)

    # Implementation Roadmap — 3 phases
    pdf.ln(2)
    section_y6 = pdf.get_y()
    pdf.set_fill_color(*TEAL)
    pdf.rect(18, section_y6, 4, 8, "F")
    pdf._sf("B", 10)
    pdf.set_text_color(*NAVY)
    pdf.set_xy(25, section_y6)
    pdf.cell(0, 8, "Implementation Roadmap / 구현 로드맵")
    pdf.ln(12)

    phases = [
        ("Phase 1 — Week 1", "robots.txt + llms.txt + Organization Schema"),
        ("Phase 2 — Weeks 2-3", "Content restructure + FAQ sections + About page"),
        ("Phase 3 — Ongoing", "Monthly SoV tracking + competitive monitoring"),
    ]
    for phase_label, phase_desc in phases:
        row_y = pdf.get_y()
        # Teal dot
        pdf.set_fill_color(*TEAL)
        pdf.ellipse(18, row_y + 1, 6, 6, "F")
        pdf._sf("B", 9)
        pdf.set_text_color(*NAVY)
        pdf.set_xy(28, row_y)
        pdf.cell(60, 7, phase_label)
        pdf._sf("", 8)
        pdf.set_text_color(*DARK)
        pdf.set_xy(90, row_y)
        pdf.cell(0, 7, phase_desc)
        pdf.ln(9)

    pdf.ln(2)

    # Files table
    pdf._sf("B", 9)
    pdf.set_text_color(*TEAL)
    pdf.set_x(18)
    pdf.cell(50, 6, "파일명 / File")
    pdf.cell(75, 6, "설명 / Description")
    pdf.cell(0, 6, "위치 / Location")
    pdf.ln(6)

    pdf.set_fill_color(*DIVIDER)
    pdf.rect(18, pdf.get_y(), 174, 1, "F")
    pdf.ln(2)

    deliverable_rows = [
        ("robots.txt", "AI crawler allow rules", "Website root"),
        ("llms.txt", "LLM permissions file", "Website root"),
        ("organization_schema.json", "Company JSON-LD schema", "<head> tag"),
        ("faqpage_schema.json", "FAQ JSON-LD template", "<head> tag"),
        ("implementation_checklist.md", "Prioritized action items (KR)", "Internal"),
        ("sov_tracking_queries.txt", "Monthly monitoring queries", "Monthly check"),
        ("implementation_guide.md", "Step-by-step client guide", "Share with dev"),
    ]
    pdf._sf("", 8)
    pdf.set_text_color(*DARK)
    for fname, desc, location in deliverable_rows:
        pdf.set_x(18)
        pdf.cell(50, 5, fname)
        pdf.cell(75, 5, desc)
        pdf.cell(0, 5, location)
        pdf.ln(5)

    pdf.ln(3)

    # Navy CTA box
    cta_y = pdf.get_y()
    pdf.set_fill_color(*NAVY)
    pdf.rect(18, cta_y, 174, 32, "F")
    pdf._sf("B", 11)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(18, cta_y + 4)
    pdf.cell(174, 7, "다음 단계 / Next Steps", align="C")
    pdf._sf("", 9)
    pdf.set_text_color(*TEAL)
    pdf.set_xy(22, cta_y + 12)
    pdf.multi_cell(
        166, 5,
        "1. 30분 전략 미팅으로 진단 결과 리뷰 (30-min strategy call to review findings)\n"
        "2. 전체 권장 사항 구현 (Implementation of all recommendations — Phase 1: 1 week)\n"
        "Contact: Keonhee Kim | SKKU Business Administration | GEO Consulting",
        border=0,
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
    sample_audit = {
        "corp_name": "현대모비스",
        "geo_score": 55,
        "geo_breakdown": {
            "citability": 22, "share_of_voice": 4,
            "ai_bot_access": 15, "ai_policy_file": 0,
            "org_schema": 5, "content_schema": 5,
            "naver_presence": 7, "kr_platform_sync": 3,
            "brand_mention": 6, "sentiment_quality": 4,
        },
        "website_url": "https://www.mobis.co.kr",
        "sov_competitors": ["현대차", "기아", "만도"],
        "sov_cited": False,
    }
    sample_recs = [
        "robots.txt에 GPTBot, ClaudeBot, PerplexityBot 허용 규칙 추가 (Allow AI Crawlers)",
        "홈페이지 제품 페이지에 구조화된 FAQ 섹션 추가 (Add Structured FAQ to Product Pages)",
        "회사 소개 페이지에 구체적인 수치와 사실 기반 문장 추가 (Strengthen About Page with Specifics)",
    ]
    path = generate_pdf(sample_audit, sample_recs, before_text="현대모비스에 대한 정보가 충분하지 않습니다.")
    print(f"Generated: {path}")
