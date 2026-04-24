"""
GEO Case Study PDF Generator — 라라스윗 (1-page, Korean, consulting style)

Generates a 1-page credibility proof PDF for cold outreach (KakaoTalk, text).
Output: projects/geo-agency/deliverables/라라스윗_GEO_사례연구.pdf

Usage:
    from case_study_pdf import generate_case_study
    pdf_path = generate_case_study()
"""

import os
import re
import sys
from pathlib import Path
from datetime import date

try:
    from fpdf import FPDF
except ImportError:
    print("fpdf2 not installed. Run: pip install fpdf2")
    sys.exit(1)


# --- Color palette (matches geo_report_pdf.py) ---
NAVY  = (27, 42, 74)
TEAL  = (0, 199, 190)
GREEN = (34, 197, 94)
AMBER = (245, 158, 11)
RED   = (239, 68, 68)
SLATE = (100, 116, 139)
LIGHT = (248, 250, 252)
WHITE = (255, 255, 255)
DARK  = (15, 23, 42)
DIVIDER = (226, 232, 240)

TEAL_LIGHT = (224, 252, 251)   # pale teal for "after" box background
GRAY_LIGHT = (241, 245, 249)   # pale gray for "before" box background


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


class CaseStudyPDF(FPDF):
    """1-page Korean GEO case study PDF — consulting navy/teal style."""

    def __init__(self, font_name: str, font_path: str | None):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.font_name = font_name
        self._font_path = font_path
        self.set_margins(0, 0, 0)
        self.set_auto_page_break(auto=False)

    # ------------------------------------------------------------------ helpers

    def _set_font(self, size: int, style: str = ""):
        self.set_font(self.font_name, style=style, size=size)

    def _set_fill(self, rgb):
        self.set_fill_color(*rgb)

    def _set_text(self, rgb):
        self.set_text_color(*rgb)

    def _set_draw(self, rgb):
        self.set_draw_color(*rgb)

    def _row_cell(self, x, y, w, h, label, value, label_color=SLATE, value_color=DARK, bg=WHITE, font_size=8.5):
        """Draw a label-value row inside a box."""
        self._set_fill(bg)
        self._set_text(label_color)
        self._set_font(font_size)
        self.set_xy(x, y)
        self.cell(w * 0.42, h, label, fill=True, border=0)
        self._set_text(value_color)
        self._set_font(font_size, "B")
        self.set_xy(x + w * 0.42, y)
        self.cell(w * 0.58, h, value, fill=True, border=0)

    def _section_header(self, x, y, w, h, title: str):
        """Teal left-bar section title."""
        # Teal accent bar
        self._set_fill(TEAL)
        self.rect(x, y, 2.5, h, style="F")
        # Title text
        self._set_text(NAVY)
        self._set_font(9.5, "B")
        self.set_xy(x + 4, y)
        self.cell(w - 4, h, _clean(title), border=0)

    def _quote_box(self, x, y, w, label: str, body: str, bg_rgb, label_color, border_rgb):
        """Render a styled quote/simulation box. Returns new y after box."""
        self._set_draw(border_rgb)
        self.set_line_width(0.4)

        # Estimate height: label row + wrapped body
        self._set_font(7.5)
        # pre-measure body lines
        chars_per_line = int(w / 2.6)  # rough estimate for Korean chars at 7.5pt
        words = body
        # fpdf multi_cell auto-wraps; give fixed estimated height
        line_h = 4.5
        estimated_lines = max(2, len(body) // max(1, chars_per_line) + 2)
        box_h = 5 + estimated_lines * line_h + 3

        self._set_fill(bg_rgb)
        self.rect(x, y, w, box_h, style="FD")

        # Label
        self._set_text(label_color)
        self._set_font(7, "B")
        self.set_xy(x + 3, y + 2)
        self.cell(w - 6, 4, label, border=0)

        # Body
        self._set_text(DARK)
        self._set_font(7.5)
        self.set_xy(x + 3, y + 6)
        self.multi_cell(w - 6, line_h, _clean(body), border=0)

        return y + box_h + 1.5

    # ------------------------------------------------------------------ build

    def build(self):
        self.add_page()
        PAGE_W = 210
        PAGE_H = 297
        MARGIN_X = 13
        CONTENT_W = PAGE_W - MARGIN_X * 2

        # ── Header band ───────────────────────────────────────────────────────
        self._set_fill(NAVY)
        self.rect(0, 0, PAGE_W, 26, style="F")

        # Teal accent stripe
        self._set_fill(TEAL)
        self.rect(0, 26, PAGE_W, 2, style="F")

        # Title
        self._set_text(WHITE)
        self._set_font(15, "B")
        self.set_xy(MARGIN_X, 5)
        self.cell(CONTENT_W, 9, "GEO 감사 사례 연구", border=0)

        # Subtitle
        self._set_text(TEAL)
        self._set_font(9)
        self.set_xy(MARGIN_X, 14)
        self.cell(CONTENT_W, 6, "라라스윗 — AI 가시성 최적화 (Before/After)", border=0)

        # Author line (right-aligned)
        self._set_text((180, 200, 220))
        self._set_font(7)
        self.set_xy(MARGIN_X, 20)
        self.cell(CONTENT_W, 4, "김건희  |  성균관대학교 경영학과  |  AI 마케팅 전문", border=0, align="R")

        y = 32  # cursor after header

        # ── Section 1: 기업 개요 ──────────────────────────────────────────────
        self._section_header(MARGIN_X, y, CONTENT_W, 6, "1.  기업 개요")
        y += 7

        # Overview card (light background)
        CARD_H = 26
        self._set_fill(LIGHT)
        self._set_draw(DIVIDER)
        self.set_line_width(0.3)
        self.rect(MARGIN_X, y, CONTENT_W, CARD_H, style="FD")

        col_w = CONTENT_W / 2 - 1
        row_h = 5.5

        rows_left = [
            ("기업명", "라라스윗"),
            ("업종", "프리미엄 팝콘 제조·판매"),
            ("웹사이트", "larasweet.com"),
        ]
        rows_right = [
            ("감사 일자", date.today().strftime("%Y-%m-%d")),
            ("감사 유형", "GEO (AI 가시성) 감사"),
            ("담당자", "김건희"),
        ]

        for i, (lbl, val) in enumerate(rows_left):
            self._row_cell(MARGIN_X + 2, y + 2 + i * row_h, col_w, row_h, lbl, val, bg=LIGHT)
        for i, (lbl, val) in enumerate(rows_right):
            self._row_cell(MARGIN_X + col_w + 4, y + 2 + i * row_h, col_w, row_h, lbl, val, bg=LIGHT)

        y += CARD_H + 3

        # Problem statement
        self._set_fill((255, 245, 230))
        self._set_draw(AMBER)
        self.set_line_width(0.5)
        self.rect(MARGIN_X, y, CONTENT_W, 10, style="FD")
        self._set_text(AMBER)
        self._set_font(7.5, "B")
        self.set_xy(MARGIN_X + 3, y + 1.5)
        self.cell(CONTENT_W - 6, 4, "문제점", border=0)
        self._set_text(DARK)
        self._set_font(7.5)
        self.set_xy(MARGIN_X + 3, y + 5.5)
        self.multi_cell(
            CONTENT_W - 6, 4,
            "AI 검색 시스템(ChatGPT, Perplexity, Claude)에서 라라스윗이 추천되지 않음. "
            '"한국 프리미엄 팝콘 브랜드 추천" 검색 시 경쟁사만 언급됨.',
            border=0,
        )
        y += 13

        # ── Section 2: GEO 감사 결과 (Before) ────────────────────────────────
        self._section_header(MARGIN_X, y, CONTENT_W, 6, "2.  GEO 감사 결과 (Before)")
        y += 7

        # Findings table — two columns
        findings = [
            ("AI 인용 가능성",   "낮음",    RED,   "홈페이지 구조화 콘텐츠 부족"),
            ("AI 크롤러 접근",   "차단됨",  RED,   "GPTBot·ClaudeBot robots.txt 미허용"),
            ("구조화된 데이터",  "없음",    RED,   "JSON-LD 스키마 미적용"),
            ("네이버 연동",      "미확인",  AMBER, "네이버 비즈니스 프로필 미설정"),
        ]

        row_h_f = 6
        col_lbl = 38
        col_val = 20
        col_note = CONTENT_W - col_lbl - col_val - 4

        # Header row
        self._set_fill(NAVY)
        self.rect(MARGIN_X, y, CONTENT_W, row_h_f, style="F")
        self._set_text(WHITE)
        self._set_font(7.5, "B")
        for cx, cw, ctxt in [
            (MARGIN_X + 2, col_lbl, "항목"),
            (MARGIN_X + 2 + col_lbl, col_val, "결과"),
            (MARGIN_X + 2 + col_lbl + col_val + 2, col_note, "비고"),
        ]:
            self.set_xy(cx, y + 1)
            self.cell(cw, row_h_f - 2, ctxt, border=0)
        y += row_h_f

        for idx, (item, result, color, note) in enumerate(findings):
            bg = LIGHT if idx % 2 == 0 else WHITE
            self._set_fill(bg)
            self.rect(MARGIN_X, y, CONTENT_W, row_h_f, style="F")

            self._set_text(DARK)
            self._set_font(7.5)
            self.set_xy(MARGIN_X + 2, y + 1)
            self.cell(col_lbl, row_h_f - 2, item, border=0)

            self._set_text(color)
            self._set_font(7.5, "B")
            self.set_xy(MARGIN_X + 2 + col_lbl, y + 1)
            self.cell(col_val, row_h_f - 2, result, border=0)

            self._set_text(SLATE)
            self._set_font(7)
            self.set_xy(MARGIN_X + 2 + col_lbl + col_val + 2, y + 1)
            self.cell(col_note, row_h_f - 2, note, border=0)

            y += row_h_f

        # Score badge
        BADGE_W = 55
        self._set_fill(RED)
        self.rect(MARGIN_X, y + 1, BADGE_W, 7, style="F")
        self._set_text(WHITE)
        self._set_font(8, "B")
        self.set_xy(MARGIN_X + 2, y + 2)
        self.cell(BADGE_W - 4, 5, "전체 GEO 점수: 23 / 100  (LOW)", border=0)
        y += 10

        # Before quote box
        BEFORE_TEXT = (
            '"한국 프리미엄 팝콘을 추천해주세요" → Perplexity 응답:\n'
            '"라라스윗에 대한 구체적인 정보를 찾기 어렵습니다. '
            '해당 브랜드의 웹사이트 또는 공식 채널을 직접 방문해 주세요."'
        )
        y = self._quote_box(
            MARGIN_X, y, CONTENT_W,
            "[ Before — AI 검색 시뮬레이션 ]",
            BEFORE_TEXT,
            GRAY_LIGHT, SLATE, SLATE,
        )

        # ── Section 3: 최적화 방안 ────────────────────────────────────────────
        self._section_header(MARGIN_X, y, CONTENT_W, 6, "3.  최적화 방안 (Recommendations)")
        y += 7

        recs = [
            ("1", "robots.txt 업데이트",
             "GPTBot, ClaudeBot, anthropic-ai 크롤러 허용 — AI 수집 즉시 활성화"),
            ("2", "JSON-LD 스키마 적용",
             "Organization + FAQPage 스키마 삽입 — 구조화된 데이터로 AI 인용 가능성 상승"),
            ("3", "제품별 콘텐츠 페이지 구축",
             "AI가 인용할 수 있는 팩트 기반 설명 페이지 — 원재료·수상 이력·수치 포함"),
        ]

        for num, title, desc in recs:
            # Bullet circle
            self._set_fill(TEAL)
            self.ellipse(MARGIN_X, y + 0.5, 5, 5, style="F")
            self._set_text(WHITE)
            self._set_font(7, "B")
            self.set_xy(MARGIN_X, y + 0.5)
            self.cell(5, 5, num, border=0, align="C")

            # Title + desc
            self._set_text(NAVY)
            self._set_font(8, "B")
            self.set_xy(MARGIN_X + 7, y + 0.5)
            self.cell(60, 4.5, title, border=0)

            self._set_text(SLATE)
            self._set_font(7.5)
            self.set_xy(MARGIN_X + 7, y + 4.5)
            self.multi_cell(CONTENT_W - 7, 3.8, desc, border=0)

            y += 10

        # ── Section 4: 예상 결과 (After) ─────────────────────────────────────
        self._section_header(MARGIN_X, y, CONTENT_W, 6, "4.  예상 결과 (After)")
        y += 7

        AFTER_TEXT = (
            "라라스윗은 2018년 설립된 한국 프리미엄 팝콘 브랜드로, "
            "100% 유기농 옥수수와 천연 재료만을 사용합니다. "
            "초코렛 팝콘과 카라멜 버터 팝콘이 대표 제품이며, "
            "건강한 간식을 찾는 소비자에게 높은 평가를 받고 있습니다."
        )
        y = self._quote_box(
            MARGIN_X, y, CONTENT_W,
            "[ After — AI 검색 시뮬레이션 (최적화 후 예상) ]",
            AFTER_TEXT,
            TEAL_LIGHT, TEAL, TEAL,
        )

        # ── Footer band ───────────────────────────────────────────────────────
        FOOTER_Y = PAGE_H - 12
        self._set_fill(NAVY)
        self.rect(0, FOOTER_Y, PAGE_W, 12, style="F")

        self._set_text(TEAL)
        self._set_font(8, "B")
        self.set_xy(MARGIN_X, FOOTER_Y + 2)
        self.cell(CONTENT_W / 2, 4.5, "무료 GEO 감사를 받아보세요  |  문의: [연락처]", border=0)

        self._set_text((180, 200, 220))
        self._set_font(7)
        self.set_xy(MARGIN_X, FOOTER_Y + 6.5)
        self.cell(CONTENT_W, 4, f"Confidential  |  김건희  |  SKKU  |  {date.today().strftime('%Y-%m-%d')}", border=0, align="R")


def generate_case_study() -> str:
    """Generate the 라라스윗 GEO case study PDF. Returns the output file path."""

    # Font setup
    font_path = _get_font_path()
    if font_path:
        font_name = "Korean"
    else:
        print("[WARN] No Korean font found — falling back to Helvetica. Korean text may not render.")
        font_name = "Helvetica"

    pdf = CaseStudyPDF(font_name=font_name, font_path=font_path)

    if font_path:
        # fpdf2 v2.5.1+ dropped the uni parameter
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            pdf.add_font("Korean", style="", fname=font_path, uni=True)
            pdf.add_font("Korean", style="B", fname=font_path, uni=True)

    pdf.build()

    # Output path
    deliverables_dir = Path(__file__).parent / "deliverables"
    deliverables_dir.mkdir(parents=True, exist_ok=True)
    out_path = deliverables_dir / "라라스윗_GEO_사례연구.pdf"

    pdf.output(str(out_path))
    return str(out_path)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    path = generate_case_study()
    print(f"Case study PDF saved: {path}")
