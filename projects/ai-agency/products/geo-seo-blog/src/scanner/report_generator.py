"""
report_generator.py
Generates a Korean PDF audit report for the GEO Scanner free lead magnet.
Wraps geo_report_pdf.py from projects/geo-agency/ -- adapts its output
format for skincare D2C clients.

Usage:
    from src.scanner.report_generator import generate_scanner_report
    pdf_path = generate_scanner_report(geo_score_dict, out_dir=Path("demo/"))
"""

import sys
import json
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# Attempt to reuse geo-agency PDF generator
_GEO_AGENCY_ROOT = Path(__file__).resolve().parents[5] / "projects" / "geo-agency"
sys.path.insert(0, str(_GEO_AGENCY_ROOT))


def _build_audit_dict_for_pdf(geo_score_dict: dict) -> dict:
    """
    Converts geo-seo-blog score dict into the format expected by
    geo_report_pdf.generate_pdf() from geo-agency.
    """
    brand = geo_score_dict.get("brand", "브랜드")
    score = geo_score_dict.get("geo_score", 0)
    ai_score = geo_score_dict.get("ai_score", 0)
    naver_score = geo_score_dict.get("naver_score", 0)
    band = geo_score_dict.get("band", "미흡")
    rec = geo_score_dict.get("recommendation", "")

    return {
        "company": brand,
        "website": geo_score_dict.get("website_url", ""),
        "overall_score": score,
        "geo_score": score,
        "band": band,
        "geo_breakdown": {
            "AI 가시성 (ChatGPT/Claude)": ai_score,
            "네이버 검색 노출": naver_score,
        },
        "dimensions": {
            "AI 가시성 (ChatGPT/Claude)": ai_score,
            "네이버 검색 노출": naver_score,
        },
        "recommendations": [rec] if rec else [],
        "generated_date": str(date.today()),
    }


def generate_scanner_report(geo_score_dict: dict, out_dir: Path = None) -> Path:
    """
    Generates a PDF audit report.

    Falls back to a plain Markdown report if fpdf2 or geo_report_pdf
    is not available (keeps the scanner usable without full stack installed).

    Args:
        geo_score_dict: Output from score_calculator.score_from_audit_results()
        out_dir: Directory for the output file. Defaults to demo/ folder.

    Returns:
        Path to the generated file (.pdf or .md fallback).
    """
    if out_dir is None:
        out_dir = Path(__file__).resolve().parents[2] / "demo"
    out_dir.mkdir(parents=True, exist_ok=True)

    brand = geo_score_dict.get("brand", "brand").replace(" ", "_")
    today = date.today().isoformat()

    # Try PDF first via geo-agency generator
    try:
        from geo_report_pdf import generate_pdf

        audit_dict = _build_audit_dict_for_pdf(geo_score_dict)
        recommendations = geo_score_dict.get("recommendation", "")
        pdf_path = out_dir / f"{today}-{brand}-geo-audit.pdf"
        generated = generate_pdf(audit_dict, [recommendations], output_path=str(pdf_path))
        return Path(generated)

    except Exception as e:
        # Fallback: Markdown report (always works)
        return _generate_markdown_report(geo_score_dict, out_dir, brand, today, fallback_reason=str(e))


def _generate_markdown_report(
    geo_score_dict: dict,
    out_dir: Path,
    brand: str,
    today: str,
    fallback_reason: str = "",
) -> Path:
    """Generates a structured Korean Markdown report as PDF fallback."""
    score = geo_score_dict.get("geo_score", 0)
    band = geo_score_dict.get("band", "")
    ai_score = geo_score_dict.get("ai_score", 0)
    naver_score = geo_score_dict.get("naver_score", 0)
    rec = geo_score_dict.get("recommendation", "")
    ai_details = geo_score_dict.get("ai_details", {})
    naver_details = geo_score_dict.get("naver_details", {})

    lines = [
        f"# {geo_score_dict.get('brand', brand)} GEO 진단 리포트",
        f"진단일: {today}",
        "",
        "---",
        "",
        "## 종합 GEO 점수",
        "",
        f"**{score}/100** ({band})",
        "",
        "| 항목 | 점수 |",
        "|---|---|",
        f"| AI 가시성 (ChatGPT/Claude 기준) | {ai_score}/100 |",
        f"| 네이버 검색 노출 | {naver_score}/100 |",
        "",
        "---",
        "",
        "## AI 가시성 상세",
        "",
        f"- AI 응답 중 브랜드 언급: {ai_details.get('mentions', 0)}/{ai_details.get('total_responses', 0)}회",
        f"- 언급 비율: {int(ai_details.get('mention_rate', 0) * 100)}%",
        "",
        "## 네이버 검색 상세",
        "",
        f"- 검색 결과 내 브랜드 언급: {naver_details.get('brand_mentions', 0)}회",
        f"- 블로그/후기 신호: {naver_details.get('blog_signals', 0)}개",
        f"- 공식 네이버 블로그: {'있음' if naver_details.get('has_official_blog') else '미확인'}",
        f"- 진단 메모: {naver_details.get('notes', '')}",
        "",
        "---",
        "",
        "## 개선 권장사항",
        "",
        rec,
        "",
        "---",
        "",
        "## 다음 단계",
        "",
        "**GEO/SEO 블로그 자동화 서비스** (월 4편, ₩300,000/월)",
        "",
        "- 매주 금요일 블로그 포스트 납품",
        "- ChatGPT/Perplexity/Claude 인용 최적화 구조 적용",
        "- 네이버 블로그 바로 붙여넣기 가능한 형식으로 전달",
        "- 첫 달 무료 체험 가능 (선착순)",
        "",
        "문의: 카카오톡 채널 [브랜드명]",
    ]

    md_path = out_dir / f"{today}-{brand}-geo-audit.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


if __name__ == "__main__":
    # Smoke test
    from src.scanner.score_calculator import calculate_geo_score

    dummy_score = calculate_geo_score(ai_score=25, naver_score=15)
    dummy_score["brand"] = "테스트브랜드"
    dummy_score["ai_details"] = {"mentions": 1, "total_responses": 10, "mention_rate": 0.1}
    dummy_score["naver_details"] = {
        "brand_mentions": 2,
        "blog_signals": 1,
        "has_official_blog": False,
        "notes": "후기 콘텐츠 부족",
    }

    out = generate_scanner_report(dummy_score)
    print(f"Report generated: {out}")
