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
import html as _html

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
    # Strip horizontal rule markdown artifacts (---, ***, ___)
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Collapse multiple blank lines left behind
    text = re.sub(r'\n{3,}', '\n\n', text)
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
        self.set_y(-18)
        self._sf("", 6)
        self.set_text_color(*TEAL)
        self.cell(0, 4, "AI 검색 점수 개선이 필요하신가요? 무료 상담: geo.keonhee@gmail.com | SME 종합 진단: keonhee-sme-diagnostic.streamlit.app", align="C")
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


def _extract_real_competitors(sov_competitors: list, before_text: str, corp_name: str) -> list:
    """
    If sov_competitors looks like tokenized garbage, extract real names from before_text.
    """
    if sov_competitors:
        avg_len = sum(len(s) for s in sov_competitors) / len(sov_competitors)
        is_garbage = avg_len < 5 or any(t in sov_competitors for t in ["경쟁사", "한국"])
        if not is_garbage:
            return sov_competitors[:5]

    if not before_text:
        return sov_competitors[:5]

    # Extract bold-marked firm names from Perplexity text (**name**)
    import re as _re
    bold_firms = _re.findall(r'\*\*([^*\n]{3,30})\*\*', before_text)
    seen, result = set(), []
    for f in bold_firms:
        f = f.strip()
        if f and f not in seen and corp_name not in f:
            seen.add(f)
            result.append(f)
        if len(result) >= 5:
            break

    return result if result else sov_competitors[:5]


def _is_positive_citation(corp_name: str, before_text: str) -> bool:
    """
    Returns True only if corp appears in a clearly positive citation context.
    Returns False if corp appears only in negative context.
    """
    if not before_text or corp_name not in before_text:
        return False
    negative_markers = ["확인되지 않", "포함되지 않", "미포함", "TOP20~100", "상대적으로 작거나", "데이터 미공개", "주요 언급에서"]
    import re as _re
    sentences = _re.split(r'[.。\n]', before_text)
    positive, negative = 0, 0
    for sent in sentences:
        if corp_name in sent or corp_name.replace("세무법인 ", "") in sent:
            if any(m in sent for m in negative_markers):
                negative += 1
            else:
                positive += 1
    return positive > 0 and negative == 0


def _generate_pdf_fpdf2(
    audit: dict,
    recommendations: list[str] | None = None,
    before_text: str = "",
    after_text: str = "",
    output_dir: str | None = None,
) -> str:
    """
    Generate a 2-3 page GEO audit PDF report (Navy + Teal consulting style).

    Returns path to the generated PDF file.
    """
    corp_name = audit.get("corp_name", "Company")
    geo_score = audit.get("geo_score", 0)
    breakdown = audit.get("geo_breakdown", {})
    website = audit.get("website_url") or "Not found"
    sov_competitors_raw = audit.get("sov_competitors", [])
    sov_cited_raw = audit.get("sov_cited", False)

    # Fix tokenized competitor list and false-positive citation
    sov_competitors = _extract_real_competitors(sov_competitors_raw, before_text, corp_name)
    sov_cited = _is_positive_citation(corp_name, before_text) if sov_cited_raw else False

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
    pdf.set_auto_page_break(auto=False)  # Manual page management — prevents cards splitting across pages
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

    # 2-column category card layout — all 5 categories fit on page 1
    # Col 1 (left, x=18, w=84): categories 0,1,2
    # Col 2 (right, x=108, w=84): categories 3,4
    # Each compact card: 9px title + N*10px per dim + 2px gap
    COL1_X = 18
    COL2_X = 108
    COL_W = 84
    BAR_W = 42
    start_y = pdf.get_y()

    def _draw_card(cx, cy, cat_en, cat_kr, dims, col_w, bar_offset=46, bar_w=32):
        card_h = 10 + len(dims) * 10
        pdf.set_fill_color(*LIGHT)
        pdf.rect(cx, cy, col_w, card_h, "F")
        pdf.set_fill_color(*TEAL)
        pdf.rect(cx, cy, 3, card_h, "F")
        # Category name bilingual
        pdf.set_xy(cx + 4, cy + 2)
        pdf._sf("B", 7)
        pdf.set_text_color(*NAVY)
        pdf.cell(col_w - 5, 4, f"{cat_en}")
        pdf.set_xy(cx + 4, cy + 6)
        pdf._sf("", 6)
        pdf.set_text_color(*TEAL)
        pdf.cell(col_w - 5, 3, cat_kr)
        # Dim bars
        for j, (dim_name, dim_score, dim_max) in enumerate(dims):
            bar_y = cy + 10 + j * 10
            pdf.set_xy(cx + 4, bar_y)
            pdf._sf("", 6)
            pdf.set_text_color(*SLATE)
            pdf.cell(bar_offset - 4, 7, dim_name)
            _progress_bar(pdf, dim_score, dim_max, cx + bar_offset, bar_y + 1, w=bar_w)
        return card_h

    col1_y = start_y
    col2_y = start_y
    for idx, (cat_en, cat_kr, dims) in enumerate(categories):
        if idx < 3:  # Left column: cats 0, 1, 2
            h = _draw_card(COL1_X, col1_y, cat_en, cat_kr, dims, COL_W, bar_offset=38, bar_w=38)
            col1_y += h + 2
        else:  # Right column: cats 3, 4
            h = _draw_card(COL2_X, col2_y, cat_en, cat_kr, dims, COL_W, bar_offset=38, bar_w=38)
            col2_y += h + 2

    # Advance cursor past both columns
    pdf.set_y(max(col1_y, col2_y))

    # =====================================================================
    # PAGE 2
    # =====================================================================
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)  # Keep off for page 2 — we control all Y positions manually

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

    # Before text quote box — "What AI says today" on page 2 (compact 25mm fixed box)
    if before_text:
        snippet = _clean(before_text)[:220] + ("..." if len(before_text) > 220 else "")
        section_y2 = pdf.get_y()
        pdf.set_fill_color(*TEAL)
        pdf.rect(18, section_y2, 4, 7, "F")
        pdf._sf("B", 8)
        pdf.set_text_color(*NAVY)
        pdf.set_xy(25, section_y2)
        pdf.cell(0, 7, "What AI says today / 현재 AI 응답")
        pdf.ln(8)

        box_y = pdf.get_y()
        pdf.set_fill_color(*LIGHT)
        pdf.rect(18, box_y, 174, 25, "F")
        pdf.set_fill_color(*TEAL)
        pdf.rect(18, box_y, 4, 25, "F")
        pdf.set_xy(25, box_y + 2)
        pdf._sf("I", 7)
        pdf.set_text_color(*DARK)
        pdf.multi_cell(164, 4, f'"{snippet}"', border=0)
        pdf.set_y(box_y + 27)
        pdf.ln(2)

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

        pdf.set_y(card_y + 18)

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
        pdf.ln(9)

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
        ("Phase 1 — Week 1 / 1주차", "robots.txt + llms.txt + Organization Schema"),
        ("Phase 2 — Weeks 2-3 / 2-3주차", "Content + FAQ sections + About page"),
        ("Phase 3 — Ongoing / 지속", "Monthly SoV tracking + monitoring"),
    ]
    for phase_label, phase_desc in phases:
        # Use set_x + cells in sequence (no set_xy with same row_y to avoid page-break issues)
        pdf.set_x(18)
        pdf._sf("B", 8)
        pdf.set_text_color(*TEAL)
        pdf.cell(6, 6, ">")
        pdf._sf("B", 8)
        pdf.set_text_color(*NAVY)
        pdf.cell(72, 6, phase_label)
        pdf._sf("", 8)
        pdf.set_text_color(*DARK)
        pdf.cell(0, 6, phase_desc)
        pdf.ln(7)

    pdf.ln(2)

    pdf.ln(2)

    # Files reference — compact note instead of full table (saves ~30mm on page 2)
    impl_section_y = pdf.get_y()
    pdf.set_fill_color(*TEAL)
    pdf.rect(18, impl_section_y, 4, 7, "F")
    pdf._sf("B", 8)
    pdf.set_text_color(*NAVY)
    pdf.set_xy(25, impl_section_y)
    pdf.cell(0, 7, "Implementation Kit 포함 파일 / Included Files")
    pdf.ln(9)
    pdf._sf("", 7)
    pdf.set_text_color(*SLATE)
    pdf.set_x(18)
    pdf.multi_cell(
        174, 4,
        "robots.txt  |  llms.txt  |  organization_schema.json  |  faqpage_schema.json\n"
        "implementation_checklist.md  |  sov_tracking_queries.txt  |  implementation_guide.md",
        border=0,
    )

    # After text + CTA — pinned to bottom of page 2 with fixed Y coordinates
    # Page height = 297mm, bottom margin = 10mm → usable bottom = 287mm
    # CTA: 28mm tall, sits at y=259. After box: 32mm, sits at y=218. Header: 8mm at y=208.
    PAGE_H = 287  # usable bottom (297 - 10mm margin)
    CTA_H = 28
    AFTER_BOX_H = 32
    AFTER_HEADER_H = 10

    cta_y = PAGE_H - CTA_H                          # 259
    after_box_y = cta_y - AFTER_BOX_H - 4           # 223
    after_header_y = after_box_y - AFTER_HEADER_H   # 213

    if after_text:
        after_clean = _clean(after_text)
        # Calculate max chars that fit in box: width=162mm, font=8, line_h=4.5 → ~18 chars/line
        # box_h=32mm / 4.5 = ~7 lines → ~126 chars max
        max_chars = 120
        after_display = after_clean[:max_chars] + ("..." if len(after_clean) > max_chars else "")

        pdf.set_fill_color(*TEAL)
        pdf.rect(18, after_header_y, 4, 8, "F")
        pdf._sf("B", 9)
        pdf.set_text_color(*NAVY)
        pdf.set_xy(25, after_header_y)
        pdf.cell(0, 8, "AI 응답 시뮬레이션 (GEO 개선 후) / After GEO Optimization")

        pdf.set_fill_color(230, 255, 240)
        pdf.rect(18, after_box_y, 174, AFTER_BOX_H, "F")
        pdf.set_fill_color(*GREEN)
        pdf.rect(18, after_box_y, 4, AFTER_BOX_H, "F")
        pdf.set_xy(25, after_box_y + 3)
        pdf._sf("I", 8)
        pdf.set_text_color(*DARK)
        # Use cell loop instead of multi_cell to avoid triggering auto page break
        lines = pdf.multi_cell(162, 4.5, chr(34) + after_display + chr(34), border=0, split_only=True)
        y_cur = after_box_y + 3
        for line in lines:
            if y_cur + 4.5 > after_box_y + AFTER_BOX_H:
                break
            pdf.set_xy(25, y_cur)
            pdf.cell(162, 4.5, line)
            y_cur += 4.5

    # CTA box — pinned to fixed Y near page bottom
    pdf.set_fill_color(*NAVY)
    pdf.rect(18, cta_y, 174, CTA_H, "F")
    pdf._sf("B", 10)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(18, cta_y + 3)
    pdf.cell(174, 6, "다음 단계 / Next Steps", align="C")
    pdf._sf("", 8)
    pdf.set_text_color(*TEAL)
    pdf.set_xy(22, cta_y + 10)
    # Use cell loop for CTA body too — no multi_cell that could overflow
    cta_lines = [
        "1. 30분 전략 미팅으로 진단 결과 리뷰 (30-min strategy call to review findings)",
        "2. 전체 권장 사항 구현 (Full implementation - Phase 1: 1 week)",
        "Contact: Keonhee Kim | SKKU Business Administration | GEO Consulting",
    ]
    for li, line in enumerate(cta_lines):
        pdf.set_xy(22, cta_y + 10 + li * 5)
        pdf.cell(166, 4.5, line)
    # --- Save ---
    if output_dir is None:
        output_dir = Path(__file__).parent / "reports"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r'[^\w\-]', '_', corp_name)
    output_path = Path(output_dir) / f"geo_audit_{safe_name}_{date.today().isoformat()}.pdf"
    pdf.output(str(output_path))
    print(f"PDF saved: {output_path}")
    return str(output_path)



# ---------------------------------------------------------------------------
# WeasyPrint HTML/CSS renderer (preferred — higher visual quality)
# Falls back to fpdf2 above if weasyprint not installed
# ---------------------------------------------------------------------------

_HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&family=Inter:wght@400;600;700&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Noto Sans KR','Inter',sans-serif;font-size:10pt;color:#0F172A;background:white;}}
.page{{width:210mm;min-height:270mm;padding:0;page-break-after:always;position:relative;}}
.header{{background:#1B2A4A;color:white;padding:14px 24px;display:flex;justify-content:space-between;align-items:center;}}
.header-title{{font-size:13pt;font-weight:700;}}
.header-sub{{font-size:8pt;opacity:0.8;margin-top:2px;}}
.header-date{{font-size:8pt;opacity:0.7;}}
.body{{padding:16px 24px 40px 24px;}}
.company-name{{font-size:20pt;font-weight:700;color:#0F172A;margin-bottom:4px;margin-top:10px;}}
.teal-bar{{width:56px;height:3px;background:#00C7BE;margin-bottom:10px;border-radius:2px;}}
.website{{font-size:8pt;color:#64748B;margin-bottom:12px;}}
.score-hero{{display:flex;align-items:center;gap:14px;margin-bottom:6px;}}
.score-num{{font-size:48pt;font-weight:700;line-height:1;}}
.score-num.high{{color:#22C55E;}}.score-num.medium{{color:#F59E0B;}}.score-num.low{{color:#EF4444;}}
.score-denom{{font-size:13pt;color:#64748B;}}
.score-badge{{display:inline-block;padding:3px 10px;border-radius:12px;font-size:8.5pt;font-weight:700;color:white;margin-top:4px;}}
.score-badge.high{{background:#22C55E;}}.score-badge.medium{{background:#F59E0B;}}.score-badge.low{{background:#EF4444;}}
.teal-line{{height:2px;background:#00C7BE;margin-bottom:12px;border-radius:1px;}}
.summary{{display:flex;margin-bottom:12px;border:1px solid #E2E8F0;border-radius:6px;overflow:hidden;}}
.summary-col{{flex:1;padding:8px 12px;border-right:1px solid #E2E8F0;}}
.summary-col:last-child{{border-right:none;}}
.summary-label{{font-size:7pt;color:#64748B;text-transform:uppercase;letter-spacing:0.4px;}}
.summary-val{{font-size:15pt;font-weight:700;margin:2px 0;}}
.summary-val.high{{color:#22C55E;}}.summary-val.medium{{color:#F59E0B;}}.summary-val.low{{color:#EF4444;}}
.summary-sub{{font-size:6.5pt;color:#94A3B8;}}
.section-hdr{{display:flex;align-items:center;gap:7px;margin:10px 0 6px 0;padding-bottom:3px;border-bottom:1px solid #E2E8F0;}}
.hdr-bar{{width:4px;height:14px;background:#00C7BE;border-radius:2px;flex-shrink:0;}}
.hdr-title{{font-size:9.5pt;font-weight:700;color:#1B2A4A;}}
.hdr-sub{{font-size:7pt;color:#64748B;margin-left:2px;}}
.cat-card{{background:#F8FAFC;border-radius:5px;padding:7px 11px;margin-bottom:5px;border-left:3px solid #00C7BE;}}
.cat-title{{font-size:8pt;font-weight:700;color:#1B2A4A;}}
.cat-sub{{font-size:6.5pt;color:#64748B;margin-bottom:5px;}}
.prog-row{{display:flex;align-items:center;gap:6px;margin-bottom:3px;}}
.prog-label{{font-size:7pt;color:#0F172A;width:110px;flex-shrink:0;}}
.prog-track{{flex:1;height:6px;background:#E2E8F0;border-radius:3px;overflow:hidden;}}
.prog-fill{{height:100%;border-radius:3px;}}
.prog-fill.high{{background:#22C55E;}}.prog-fill.medium{{background:#F59E0B;}}.prog-fill.low{{background:#EF4444;}}
.prog-score{{font-size:7pt;font-weight:700;width:32px;text-align:right;flex-shrink:0;}}
.before-box{{background:#F8FAFC;border-left:4px solid #00C7BE;padding:8px 12px;margin:8px 0;border-radius:0 5px 5px 0;}}
.before-lbl{{font-size:7pt;color:#64748B;font-weight:700;margin-bottom:3px;}}
.before-txt{{font-size:8pt;color:#334155;font-style:italic;line-height:1.4;}}
.after-box{{background:#F0FDF4;border-left:4px solid #22C55E;padding:8px 12px;margin:8px 0;border-radius:0 5px 5px 0;}}
.after-lbl{{font-size:7pt;color:#16A34A;font-weight:700;margin-bottom:3px;}}
.after-txt{{font-size:8pt;color:#334155;font-style:italic;line-height:1.4;}}
.footer{{text-align:center;font-size:7pt;color:#94A3B8;padding:6px 24px;border-top:1px solid #E2E8F0;margin-top:8px;}}
.rec-card{{display:flex;gap:10px;background:#F8FAFC;border-left:3px solid #00C7BE;border-radius:0 5px 5px 0;padding:9px 12px;margin-bottom:7px;}}
.rec-num{{width:22px;height:22px;background:#1B2A4A;color:white;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:8.5pt;font-weight:700;flex-shrink:0;line-height:22px;text-align:center;}}
.rec-body{{flex:1;}}
.rec-title{{font-size:8.5pt;font-weight:700;color:#0F172A;margin-bottom:2px;}}
.rec-en{{font-size:7.5pt;color:#64748B;font-style:italic;}}
.proj-row{{display:flex;align-items:center;gap:12px;padding:8px 0;}}
.proj-box{{text-align:center;padding:7px 14px;border-radius:7px;background:#F8FAFC;border:1px solid #E2E8F0;}}
.proj-lbl{{font-size:7pt;color:#64748B;}}
.proj-score{{font-size:18pt;font-weight:700;}}
.proj-arrow{{font-size:16pt;color:#00C7BE;}}
.timeline-item{{display:flex;gap:9px;margin-bottom:7px;}}
.tl-dot{{width:9px;height:9px;background:#00C7BE;border-radius:50%;margin-top:3px;flex-shrink:0;}}
.tl-phase{{font-size:8pt;font-weight:700;color:#1B2A4A;}}
.tl-desc{{font-size:7.5pt;color:#64748B;}}
.files-tbl{{width:100%;border-collapse:collapse;margin:6px 0;font-size:7.5pt;}}
.files-tbl th{{background:#1B2A4A;color:white;padding:4px 7px;text-align:left;font-weight:600;}}
.files-tbl td{{padding:4px 7px;border-bottom:1px solid #E2E8F0;}}
.files-tbl tr:nth-child(even) td{{background:#F8FAFC;}}
.cta{{background:#1B2A4A;color:white;border-radius:7px;padding:12px 18px;margin-top:10px;}}
.cta-title{{font-size:11pt;font-weight:700;margin-bottom:5px;}}
.cta-body{{font-size:8pt;line-height:1.6;opacity:0.9;}}
.cta-contact{{font-size:7.5pt;opacity:0.65;margin-top:5px;}}
.comp-section{{margin:6px 0;}}
.badge{{display:inline-block;padding:2px 7px;border-radius:9px;font-size:7pt;font-weight:700;}}
.badge-yes{{background:#DCFCE7;color:#166534;}}.badge-no{{background:#FEE2E2;color:#991B1B;}}
</style>
</head>
<body>
<!-- PAGE 1 -->
<div class="page">
<div class="header">
  <div><div class="header-title">GEO Audit Report</div><div class="header-sub">Generative Engine Optimization / AI 가시성 진단</div></div>
  <div class="header-date">{DATE}</div>
</div>
<div class="body">
  <div class="company-name">{COMPANY}</div>
  <div class="teal-bar"></div>
  <div class="website">Website: {WEBSITE}</div>
  <div class="score-hero">
    <div class="score-num {SC}">{SCORE}</div>
    <div><div class="score-denom">/ 100</div><div class="score-badge {SC}">{SLABEL}</div></div>
  </div>
  <div class="teal-line"></div>
  <div class="summary">
    <div class="summary-col"><div class="summary-label">Content Quality / 콘텐츠 품질</div><div class="summary-val {CC}">{CPCT}%</div><div class="summary-sub">Citability · Schema · Brand</div></div>
    <div class="summary-col"><div class="summary-label">Technical Access / 기술 접근성</div><div class="summary-val {AC}">{APCT}%</div><div class="summary-sub">Crawler · Policy · Schema</div></div>
    <div class="summary-col"><div class="summary-label">Market Presence / 시장 존재감</div><div class="summary-val {PC}">{PPCT}%</div><div class="summary-sub">SoV · Naver · Sentiment</div></div>
  </div>
  <div class="section-hdr"><div class="hdr-bar"></div><div class="hdr-title">Score Breakdown</div><div class="hdr-sub">/ 점수 세부 항목</div></div>
  {CAT_CARDS}
  {BEFORE_BOX}
</div>
<div class="footer" style="font-size:6pt;color:#0EC7BE;margin-bottom:2px;">AI 검색 점수 개선이 필요하신가요? 무료 상담: geo.keonhee@gmail.com | SME 종합 진단: keonhee-sme-diagnostic.streamlit.app</div>
<div class="footer">GEO Audit Report &nbsp;|&nbsp; {DATE} &nbsp;|&nbsp; Confidential / 기밀</div>
</div>
<!-- PAGE 2 -->
<div class="page">
<div class="header">
  <div><div class="header-title">{COMPANY} — Implementation Roadmap</div><div class="header-sub">구현 로드맵 / Action Plan</div></div>
  <div class="header-date">{DATE}</div>
</div>
<div class="body">
  <div class="section-hdr"><div class="hdr-bar"></div><div class="hdr-title">Top 3 Actions</div><div class="hdr-sub">/ 우선 실행 사항</div></div>
  {REC_CARDS}
  {COMP_SECTION}
  <div class="section-hdr"><div class="hdr-bar"></div><div class="hdr-title">Expected Impact</div><div class="hdr-sub">/ 최적화 후 예상 점수</div></div>
  <div class="proj-row">
    <div class="proj-box"><div class="proj-lbl">현재 / Current</div><div class="proj-score {SC}">{SCORE}</div></div>
    <div class="proj-arrow">&#8594;</div>
    <div class="proj-box"><div class="proj-lbl">예상 / Projected</div><div class="proj-score {PRJC}">{PRJS}</div></div>
  </div>
  <div class="section-hdr"><div class="hdr-bar"></div><div class="hdr-title">Implementation Roadmap</div><div class="hdr-sub">/ 단계별 구현</div></div>
  <div class="timeline-item"><div class="tl-dot"></div><div><div class="tl-phase">Phase 1 — Week 1 / 1주차</div><div class="tl-desc">robots.txt + llms.txt + Organization Schema — AI 크롤러 허용 및 구조화 데이터</div></div></div>
  <div class="timeline-item"><div class="tl-dot"></div><div><div class="tl-phase">Phase 2 — Weeks 2–3 / 2-3주차</div><div class="tl-desc">Content restructure + FAQ sections + About page — AI 인용 가능 콘텐츠 전환</div></div></div>
  <div class="timeline-item"><div class="tl-dot"></div><div><div class="tl-phase">Phase 3 — Ongoing / 지속</div><div class="tl-desc">Monthly SoV tracking + competitive monitoring — 월간 모니터링</div></div></div>
  <div class="section-hdr"><div class="hdr-bar"></div><div class="hdr-title">Implementation Kit Files</div><div class="hdr-sub">/ 구현 파일 목록</div></div>
  <table class="files-tbl">
    <tr><th>파일명</th><th>설명 / Description</th><th>위치 / Location</th></tr>
    <tr><td>robots.txt</td><td>AI crawler allow rules</td><td>Website root</td></tr>
    <tr><td>llms.txt</td><td>LLM content permissions</td><td>Website root</td></tr>
    <tr><td>organization_schema.json</td><td>Company JSON-LD schema</td><td>&lt;head&gt; tag</td></tr>
    <tr><td>faqpage_schema.json</td><td>FAQ JSON-LD template</td><td>&lt;head&gt; tag</td></tr>
    <tr><td>implementation_checklist.md</td><td>Priority checklist (KR+EN)</td><td>Internal ref</td></tr>
    <tr><td>sov_tracking_queries.txt</td><td>Monthly monitoring queries</td><td>Monthly check</td></tr>
    <tr><td>implementation_guide.md</td><td>Step-by-step client guide</td><td>Share with dev</td></tr>
  </table>
  {AFTER_BOX}
  <div class="cta">
    <div class="cta-title">다음 단계 / Next Steps</div>
    <div class="cta-body">1. 30분 전략 미팅으로 이 결과를 검토합니다 / 30-min strategy call to review findings<br>2. Phase 1 구현 (1주 소요) / Phase 1 implementation — 1 week<br>3. 30일 후 재진단으로 개선도 측정 / Re-audit in 30 days to measure improvement</div>
    <div class="cta-contact">Keonhee Kim &nbsp;|&nbsp; SKKU Business Administration &nbsp;|&nbsp; GEO Consulting</div>
  </div>
</div>
<div class="footer" style="font-size:6pt;color:#0EC7BE;margin-bottom:2px;">AI 검색 점수 개선이 필요하신가요? 무료 상담: geo.keonhee@gmail.com | SME 종합 진단: keonhee-sme-diagnostic.streamlit.app</div>
<div class="footer">GEO Audit Report &nbsp;|&nbsp; {DATE} &nbsp;|&nbsp; Confidential / 기밀 &nbsp;|&nbsp; Page 2</div>
</div>
</body>
</html>"""


def _sc(score: int) -> str:
    return "high" if score >= 70 else "medium" if score >= 40 else "low"


def _slabel(score: int) -> str:
    if score >= 70: return "High / 높음"
    if score >= 40: return "Medium / 보통"
    return "Low / 낮음"


def _cat_cards_html(breakdown: dict) -> str:
    categories = [
        ("AI Citability & Share of Voice", "AI 인용성 및 공유 점수", [
            ("AI Citability", "citability", 40),
            ("Share of Voice", "share_of_voice", 10),
        ]),
        ("Crawler & Agent Accessibility", "크롤러 및 에이전트 접근성", [
            ("AI Bot Access", "ai_bot_access", 20),
            ("AI Policy File (llms.txt)", "ai_policy_file", 10),
        ]),
        ("Schema & Structured Data", "스키마 및 구조화 데이터", [
            ("Org Schema", "org_schema", 15),
            ("Content Schema", "content_schema", 15),
        ]),
        ("Local Sync: KR Platforms", "한국 플랫폼 연동", [
            ("Naver Presence", "naver_presence", 10),
            ("KR Platform Sync", "kr_platform_sync", 10),
        ]),
        ("Brand Sentiment & Mention", "브랜드 언급 및 감성", [
            ("Brand Mention", "brand_mention", 10),
            ("Sentiment Quality", "sentiment_quality", 10),
        ]),
    ]
    fallback = {"ai_bot_access": "crawler_access", "ai_policy_file": "llms_txt"}
    html = ""
    for title_en, title_kr, metrics in categories:
        bars = ""
        for label, key, max_val in metrics:
            val = breakdown.get(key, breakdown.get(fallback.get(key, key), 0))
            pct = int(val / max_val * 100) if max_val else 0
            cls = _sc(pct)
            bars += (
                f'<div class="prog-row">'
                f'<div class="prog-label">{label}</div>'
                f'<div class="prog-track"><div class="prog-fill {cls}" style="width:{pct}%"></div></div>'
                f'<div class="prog-score">{val}/{max_val}</div>'
                f'</div>'
            )
        html += (
            f'<div class="cat-card">'
            f'<div class="cat-title">{title_en}</div>'
            f'<div class="cat-sub">{title_kr}</div>'
            f'{bars}</div>'
        )
    return html


def _rec_cards_html(recommendations: list) -> str:
    out = ""
    for i, rec in enumerate(recommendations[:3], 1):
        clean = _html.escape(re.sub(r'\[.*?\]|\*{1,2}|#{1,6}\s*', '', rec).strip())
        out += (
            f'<div class="rec-card">'
            f'<div class="rec-num">{i}</div>'
            f'<div class="rec-body"><div class="rec-title">{clean}</div></div>'
            f'</div>'
        )
    return out


def _comp_section_html(audit: dict) -> str:
    comps = audit.get("sov_competitors", [])
    if not comps:
        return ""
    cited = audit.get("sov_cited", False)
    corp = audit.get("corp_name", "귀사")
    badge = '<span class="badge badge-yes">포함됨 / Yes</span>' if cited else '<span class="badge badge-no">미포함 / No</span>'
    comp_str = _html.escape(", ".join(comps[:5]))
    corp_esc = _html.escape(corp)
    return (
        '<div class="section-hdr"><div class="hdr-bar"></div>'
        '<div class="hdr-title">Competitive Landscape</div>'
        '<div class="hdr-sub">/ 경쟁사 AI 인용 현황</div></div>'
        f'<div class="comp-section" style="font-size:8pt;color:#334155;line-height:1.6;">'
        f'AI 추천 시 언급되는 경쟁사: <strong>{comp_str}</strong><br>'
        f'{corp_esc} 포함 여부: {badge}</div>'
    )


def _generate_pdf_weasyprint(audit: dict, recommendations: list | None = None, before_text: str = "", after_text: str = "", output_dir=None) -> str:
    from weasyprint import HTML as _WP

    corp = audit.get("corp_name", "Company")
    score = audit.get("geo_score", 0)
    bd = audit.get("geo_breakdown", {})
    website = audit.get("website_url") or "Not found"

    if recommendations is None:
        recommendations = [
            "robots.txt에 GPTBot, ClaudeBot, PerplexityBot 허용 규칙 추가 / Allow AI crawlers in robots.txt",
            "홈페이지에 구조화된 FAQ 섹션 추가 / Add structured FAQ section to website",
            "회사 소개 페이지에 구체적인 수치 추가 / Strengthen About page with specific facts and numbers",
        ]

    citability = bd.get("citability", 0)
    sov = bd.get("share_of_voice", 0)
    ai_bot = bd.get("ai_bot_access", bd.get("crawler_access", 0))
    ai_policy = bd.get("ai_policy_file", bd.get("llms_txt", 0))
    org_schema = bd.get("org_schema", 0)
    content_schema = bd.get("content_schema", 0)
    naver = bd.get("naver_presence", 0)
    kr_sync = bd.get("kr_platform_sync", 0)
    brand = bd.get("brand_mention", 0)
    sentiment = bd.get("sentiment_quality", 0)

    cpct = round((citability + content_schema + brand) / 65 * 100)
    apct = round((ai_bot + ai_policy + org_schema) / 45 * 100)
    ppct = round((sov + naver + kr_sync + sentiment) / 40 * 100)

    max_scores = {"citability":40,"share_of_voice":10,"ai_bot_access":20,"ai_policy_file":10,"org_schema":15,"content_schema":15,"naver_presence":10,"kr_platform_sync":10,"brand_mention":10,"sentiment_quality":10}
    recoverable = sum(int((mv - bd.get(k, 0)) * 0.6) for k, mv in max_scores.items() if bd.get(k, 0) < mv * 0.7)
    proj = min(100, score + round(recoverable / 150 * 100))

    before_box = ""
    if before_text:
        snippet = re.sub(r'(\[\d+\])+', '', before_text).strip()[:380]
        if len(before_text) > 380:
            snippet += "..."
        before_box = (
            '<div class="before-box">'
            '<div class="before-lbl">현재 AI 응답 / What AI says about you today</div>'
            f'<div class="before-txt">"{_html.escape(snippet)}"</div>'
            '</div>'
        )

    after_box = ""
    if after_text:
        after_snippet = re.sub(r'(\[\d+\])+', '', after_text).strip()[:380]
        if len(after_text) > 380:
            after_snippet += "..."
        after_box = (
            '<div class="after-box">'
            '<div class="after-lbl">AI 응답 시뮬레이션 (GEO 개선 후) / After GEO Optimization</div>'
            f'<div class="after-txt">"{_html.escape(after_snippet)}"</div>'
            '</div>'
        )

    sanitized_audit = dict(audit)
    sanitized_audit["sov_competitors"] = _extract_real_competitors(
        audit.get("sov_competitors", []), before_text, corp
    )
    sanitized_audit["sov_cited"] = (
        _is_positive_citation(corp, before_text) if audit.get("sov_cited", False) else False
    )

    html_doc = _HTML_TEMPLATE.format(
        DATE=date.today().isoformat(),
        COMPANY=_html.escape(corp[:50]),
        WEBSITE=_html.escape(website[:80]),
        SCORE=score,
        SC=_sc(score),
        SLABEL=_slabel(score),
        CC=_sc(cpct), CPCT=cpct,
        AC=_sc(apct), APCT=apct,
        PC=_sc(ppct), PPCT=ppct,
        CAT_CARDS=_cat_cards_html(bd),
        BEFORE_BOX=before_box,
        AFTER_BOX=after_box,
        REC_CARDS=_rec_cards_html(recommendations),
        COMP_SECTION=_comp_section_html(sanitized_audit),
        PRJC=_sc(proj), PRJS=proj,
    )

    if output_dir is None:
        output_dir = Path(__file__).parent / "reports"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    safe = re.sub(r'[^\w\-]', '_', corp)
    out = Path(output_dir) / f"geo_audit_{safe}_{date.today().isoformat()}.pdf"
    _WP(string=html_doc).write_pdf(str(out))
    print(f"PDF saved (WeasyPrint): {out}")
    return str(out)


def generate_pdf(audit: dict, recommendations: list | None = None, before_text: str = "", after_text: str = "", output_dir=None) -> str:
    """
    Generate GEO audit PDF. Uses WeasyPrint (HTML/CSS) if available,
    falls back to fpdf2 renderer for compatibility.
    """
    try:
        import weasyprint  # noqa: F401
    except ImportError:
        return _generate_pdf_fpdf2(audit, recommendations, before_text, after_text, output_dir)
    try:
        return _generate_pdf_weasyprint(audit, recommendations, before_text, after_text, output_dir)
    except Exception as e:
        import logging
        logging.exception("WeasyPrint rendering failed; falling back to fpdf2: %s", e)
        return _generate_pdf_fpdf2(audit, recommendations, before_text, after_text, output_dir)


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
