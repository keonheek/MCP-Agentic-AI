"""
Quote + Invoice PDF Generator — Navy + Teal consulting style.
Reuses GeoPDF pattern from projects/geo-agency/geo_report_pdf.py.
"""

import io
import os
import sys
from datetime import date

try:
    from fpdf import FPDF
except ImportError:
    print("fpdf2 not installed. Run: pip install fpdf2")
    sys.exit(1)

# ─── Color Palette ─────────────────────────────────────────

NAVY = (27, 42, 74)
TEAL = (0, 199, 190)
SLATE = (100, 116, 139)
LIGHT = (248, 250, 252)
WHITE = (255, 255, 255)
DARK = (15, 23, 42)
DIVIDER = (226, 232, 240)


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


class ErpPDF(FPDF):
    def __init__(self):
        super().__init__()
        if _UNICODE_FONT:
            self.add_font(_FONT_NAME, "", _UNICODE_FONT, uni=True)
            self.add_font(_FONT_NAME, "B", _UNICODE_FONT, uni=True)
        self._base_font = _FONT_NAME if _UNICODE_FONT else "Helvetica"

    def _sf(self, style: str = "", size: int = 10):
        self.set_font(self._base_font, style, size)

    def header(self):
        pass

    def footer(self):
        self.set_y(-12)
        self._sf("", 7)
        self.set_text_color(*SLATE)
        self.cell(0, 5, f"GEO Agency | {date.today().isoformat()} | Confidential", align="C")


def _draw_header(pdf: ErpPDF, doc_type: str, doc_number: str):
    """Draw navy header bar with document type and number."""
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, 210, 35, "F")

    # Teal accent line
    pdf.set_fill_color(*TEAL)
    pdf.rect(0, 35, 210, 2, "F")

    pdf._sf("B", 20)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(15, 8)
    pdf.cell(0, 10, f"GEO Agency | {doc_type}")

    pdf._sf("", 11)
    pdf.set_xy(15, 20)
    pdf.cell(0, 8, doc_number)


def _draw_client_info(pdf: ErpPDF, data: dict, y_start: float):
    """Draw client info block."""
    pdf.set_xy(15, y_start)
    pdf._sf("B", 10)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 7, "고객 정보")

    pdf._sf("", 9)
    pdf.set_text_color(*SLATE)
    y = y_start + 8
    info_lines = [
        f"상호: {data.get('business_name', '-')}",
        f"담당자: {data.get('client_name', '-')}",
        f"연락처: {data.get('phone', '-')}",
        f"이메일: {data.get('email', '-')}",
        f"카카오톡: {data.get('kakao_id', '-')}",
    ]
    for line in info_lines:
        pdf.set_xy(15, y)
        pdf.cell(0, 5, line)
        y += 5.5

    return y + 3


def _draw_items_table(pdf: ErpPDF, items: list, y_start: float) -> float:
    """Draw line items table. Returns y position after table."""
    y = y_start

    # Table header
    pdf.set_fill_color(*NAVY)
    pdf._sf("B", 9)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(15, y)
    pdf.cell(95, 7, "  항목", fill=True)
    pdf.cell(20, 7, "수량", align="C", fill=True)
    pdf.cell(30, 7, "단가", align="R", fill=True)
    pdf.cell(30, 7, "금액  ", align="R", fill=True)
    y += 7

    # Table rows
    pdf._sf("", 9)
    pdf.set_text_color(*DARK)
    for i, item in enumerate(items):
        bg = LIGHT if i % 2 == 0 else WHITE
        pdf.set_fill_color(*bg)
        pdf.set_xy(15, y)
        pdf.cell(95, 7, f"  {item.get('description', '-')}", fill=True)
        pdf.cell(20, 7, str(item.get("quantity", 1)), align="C", fill=True)
        pdf.cell(30, 7, f"{item.get('unit_price', 0):,}", align="R", fill=True)
        subtotal = item.get("quantity", 1) * item.get("unit_price", 0)
        pdf.cell(30, 7, f"{subtotal:,}  ", align="R", fill=True)
        y += 7

    # Divider
    pdf.set_draw_color(*DIVIDER)
    pdf.line(15, y, 190, y)
    y += 2

    return y


def _draw_totals(pdf: ErpPDF, total: int, y_start: float, include_vat: bool = True) -> float:
    """Draw subtotal / VAT / total block."""
    y = y_start
    vat = int(total * 0.1) if include_vat else 0
    grand = total + vat

    pdf._sf("", 9)
    pdf.set_text_color(*SLATE)

    # Subtotal
    pdf.set_xy(120, y)
    pdf.cell(40, 6, "소계", align="R")
    pdf.cell(30, 6, f"{total:,}원", align="R")
    y += 6

    if include_vat:
        pdf.set_xy(120, y)
        pdf.cell(40, 6, "부가세 (10%)", align="R")
        pdf.cell(30, 6, f"{vat:,}원", align="R")
        y += 6

    # Grand total
    pdf._sf("B", 11)
    pdf.set_text_color(*DARK)
    pdf.set_xy(120, y)
    pdf.cell(40, 8, "합계", align="R")
    pdf.cell(30, 8, f"{grand:,}원", align="R")
    y += 10

    return y


def _draw_footer_info(pdf: ErpPDF, y_start: float):
    """Draw bank info and signature area."""
    y = y_start
    pdf.set_draw_color(*TEAL)
    pdf.line(15, y, 190, y)
    y += 5

    pdf._sf("", 8)
    pdf.set_text_color(*SLATE)
    lines = [
        "입금 계좌: [은행명] [계좌번호] (예금주: 김건희)",
        "GEO Agency | Keonhee Kim | SKKU Business Administration",
        "문의: keonhee@skku.edu | KakaoTalk: keonhee_geo",
    ]
    for line in lines:
        pdf.set_xy(15, y)
        pdf.cell(0, 5, line)
        y += 5


def generate_quote_pdf(quote: dict) -> bytes | None:
    """Generate quote PDF from quote dict (with items, client info)."""
    try:
        pdf = ErpPDF()
        pdf.add_page()

        _draw_header(pdf, "견적서", quote.get("quote_number", "-"))

        # Meta info (right side of header area)
        pdf._sf("", 9)
        pdf.set_text_color(*DARK)
        pdf.set_xy(15, 42)
        pdf.cell(90, 5, f"발행일: {date.today().isoformat()}")
        pdf.cell(0, 5, f"유효기간: {quote.get('valid_until', '-')}", align="R")
        pdf.set_xy(15, 48)
        pdf.cell(0, 5, f"견적 제목: {quote.get('title', '-')}")

        y = _draw_client_info(pdf, quote, 57)
        y = _draw_items_table(pdf, quote.get("items", []), y)
        y = _draw_totals(pdf, quote.get("total", 0), y)

        if quote.get("notes"):
            pdf._sf("", 8)
            pdf.set_text_color(*SLATE)
            pdf.set_xy(15, y)
            pdf.cell(0, 5, f"비고: {quote['notes']}")
            y += 8

        _draw_footer_info(pdf, y)

        buf = io.BytesIO()
        pdf.output(buf)
        return buf.getvalue()
    except Exception:
        return None


def generate_invoice_pdf(invoice: dict) -> bytes | None:
    """Generate invoice PDF from invoice dict."""
    try:
        pdf = ErpPDF()
        pdf.add_page()

        _draw_header(pdf, "청구서", invoice.get("invoice_number", "-"))

        pdf._sf("", 9)
        pdf.set_text_color(*DARK)
        pdf.set_xy(15, 42)
        pdf.cell(90, 5, f"발행일: {invoice.get('issued_at', date.today().isoformat())[:10]}")
        pdf.cell(0, 5, f"납부 기한: {invoice.get('due_date', '-')}", align="R")

        STATUS_KR = {"unpaid": "미납", "paid": "완납", "overdue": "연체", "cancelled": "취소"}
        status_label = STATUS_KR.get(invoice.get("status", ""), invoice.get("status", ""))
        pdf.set_xy(15, 48)
        pdf.cell(0, 5, f"상태: {status_label}")
        if invoice.get("paid_at"):
            pdf.set_xy(15, 54)
            pdf.cell(0, 5, f"수금일: {invoice['paid_at'][:10]}")

        y = _draw_client_info(pdf, invoice, 60)

        items = invoice.get("items", [])
        if items:
            y = _draw_items_table(pdf, items, y)
            y = _draw_totals(pdf, invoice.get("total_amount", 0), y)
        else:
            # Simple total display if no line items
            pdf._sf("B", 14)
            pdf.set_text_color(*DARK)
            pdf.set_xy(15, y)
            pdf.cell(0, 10, f"청구 금액: {invoice.get('total_amount', 0):,}원")
            y += 15

        _draw_footer_info(pdf, y)

        buf = io.BytesIO()
        pdf.output(buf)
        return buf.getvalue()
    except Exception:
        return None
