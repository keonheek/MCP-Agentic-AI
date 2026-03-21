"""
GEO Agency - Streamlit App

Single-company GEO audit tool for client demos and service delivery.
Input: company name -> GEO audit -> before/after proof -> PDF download
"""

import os
import re
import sys
from pathlib import Path

import streamlit as st

for _p in [Path(__file__).parent / ".env", Path(__file__).parent.parent / ".env", Path(__file__).parent.parent.parent / ".env"]:
    if _p.exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=_p)
        break

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "lead-intelligence"))

st.set_page_config(page_title="GEO Audit", page_icon="🔍", layout="wide")

# --- Sidebar: access code ---
with st.sidebar:
    st.markdown("### Access Code / 액세스 코드")
    st.text_input(
        "코드를 입력하면 전체 리포트를 볼 수 있습니다",
        type="password",
        key="access_code",
        placeholder="액세스 코드 입력...",
    )
    st.caption("코드가 없으신가요? Keonhee Kim에게 문의하세요.")

_VALID_CODES = {"GEO2026", "DEMO", "FREE"}
_env_code = os.environ.get("GEO_ACCESS_CODE", "")
if _env_code:
    _VALID_CODES.add(_env_code)


def _has_access() -> bool:
    return st.session_state.get("access_code", "") in _VALID_CODES


def _strip_citations(text: str) -> str:
    """Remove [1], [2], etc. citation markers from display text."""
    return re.sub(r"(\[\d+\])+", "", text).strip()


_KIT_ICONS = {
    "robots.txt": "🔐",
    "llms.txt": "🤖",
    "organization_schema.json": "🏢",
    "faqpage_schema.json": "❓",
    "implementation_checklist.md": "✅",
    "sov_tracking_queries.txt": "📊",
    "implementation_guide.md": "📖",
}

# --- Main UI ---
st.title("GEO Audit Tool")
st.caption("AI 가시성 진단 — Generative Engine Optimization")

st.markdown("""
**GEO(Generative Engine Optimization)**는 ChatGPT, Perplexity, Claude 같은 AI 시스템이
당신의 비즈니스를 추천하도록 최적화하는 것입니다.
""")

st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    company_name = st.text_input(
        "회사명 (한국어 또는 영어)",
        placeholder="예: 솔브레인, 현대모비스, 스타트업 이름",
        help="DART 상장 여부 무관 — 어떤 회사든 가능합니다",
    )
    product_category = st.text_input(
        "주요 제품/서비스 카테고리 (선택)",
        placeholder="예: 반도체 소재, IT 컨설팅, 온라인 쇼핑몰",
        help="AI 추천 쿼리를 더 정확하게 만들기 위해 사용됩니다",
    )

with col2:
    st.markdown("#### 점수 기준")
    st.markdown("""
    | 범위 | 등급 |
    |------|------|
    | 70-100 | 🟢 High |
    | 40-69  | 🟡 Medium |
    | 0-39   | 🔴 Low |
    """)

run = st.button("GEO 진단 시작", type="primary", disabled=not company_name)

if run and company_name:
    st.divider()

    with st.spinner(f"'{company_name}' 분석 중... (약 30-60초)"):
        try:
            from geo_audit import audit_single_company
            audit = audit_single_company(company_name)
        except Exception as e:
            st.error(f"GEO 진단 오류: {e}")
            st.stop()

    geo_score = audit.get("geo_score", 0)
    breakdown = audit.get("geo_breakdown", {})
    website = audit.get("website_url") or "찾을 수 없음"

    citability = breakdown.get("citability", 0)
    sov = breakdown.get("share_of_voice", 0)
    ai_bot = breakdown.get("ai_bot_access", breakdown.get("crawler_access", 0))
    ai_policy = breakdown.get("ai_policy_file", breakdown.get("llms_txt", 0))
    org_schema = breakdown.get("org_schema", 0)
    content_schema = breakdown.get("content_schema", 0)
    naver = breakdown.get("naver_presence", 0)
    kr_sync = breakdown.get("kr_platform_sync", 0)
    brand_mention = breakdown.get("brand_mention", 0)
    sentiment_quality = breakdown.get("sentiment_quality", 0)

    content_pct = round((citability + content_schema + brand_mention) / 65 * 100)
    access_pct = round((ai_bot + ai_policy + org_schema) / 45 * 100)
    presence_pct = round((sov + naver + kr_sync + sentiment_quality) / 40 * 100)

    st.markdown(f"## {company_name} GEO Score")
    color = "green" if geo_score >= 70 else ("orange" if geo_score >= 40 else "red")
    label = "High" if geo_score >= 70 else ("Medium" if geo_score >= 40 else "Low")
    st.markdown(f"<h1 style='color:{color}'>{geo_score}/100 — {label}</h1>", unsafe_allow_html=True)
    st.caption(f"웹사이트: {website}")

    col_content, col_access, col_presence = st.columns(3)
    with col_content:
        st.metric("Content Quality", f"{content_pct}%",
                  help="AI가 귀사 콘텐츠를 읽고 이해할 수 있는지")
    with col_access:
        st.metric("Technical Access", f"{access_pct}%",
                  help="AI 크롤러가 귀사 사이트에 접근 가능한지")
    with col_presence:
        st.metric("Market Presence", f"{presence_pct}%",
                  help="AI가 귀사를 시장에서 인식하고 추천하는지")

    with st.expander("기술 세부 점수 (10개 지표)", expanded=False):
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("AI Citability", f"{citability}/40")
            st.metric("Share of Voice", f"{sov}/10")
            st.metric("AI Bot Access", f"{ai_bot}/20")
            st.metric("AI Policy File (llms.txt)", f"{ai_policy}/10")
            st.metric("Org Schema", f"{org_schema}/15")
        with col_b:
            st.metric("Content Schema", f"{content_schema}/15")
            st.metric("Naver Presence", f"{naver}/10")
            st.metric("KR Platform Sync", f"{kr_sync}/10")
            st.metric("Brand Mention", f"{brand_mention}/10")
            st.metric("Sentiment Quality", f"{sentiment_quality}/10")

    sov_competitors = audit.get("sov_competitors", [])
    sov_cited = audit.get("sov_cited", False)
    if sov_competitors:
        cited_label = "포함됨" if sov_cited else "미포함"
        st.markdown(
            f"**경쟁사 AI 인용 현황:** {', '.join(sov_competitors[:5])} "
            f"| 귀사 인용 여부: **{cited_label}**"
        )

    st.session_state["audit"] = audit

    # Before text -- always free, strip citation numbers before display
    st.divider()
    st.markdown("### AI 가시성 현황 (Before)")
    with st.spinner("AI가 현재 이 회사에 대해 뭐라고 하는지 확인 중..."):
        try:
            from before_after import get_before, get_after
            before = get_before(company_name, product_category)
        except Exception as e:
            before = f"오류: {e}"

    before_display = _strip_citations(before)
    st.info(before_display[:800] + ("..." if len(before_display) > 800 else ""))
    st.session_state["before"] = before

    from geo_audit import generate_dynamic_recommendations
    recs = generate_dynamic_recommendations(breakdown, company_name)
    st.session_state["recs"] = recs

    # Recommendation 1 is always free; 2 and 3 are gated
    st.divider()
    st.markdown("### GEO 최적화 권장 사항")
    if recs:
        st.markdown(f"**1. {recs[0]}**")

    if not _has_access():
        st.warning(
            "나머지 권장 사항과 구현 파일은 액세스 코드가 필요합니다. "
            "왼쪽 사이드바에 코드를 입력하세요."
        )
        st.markdown(
            "<div style='filter:blur(4px);user-select:none;pointer-events:none;'>"
            "<p><b>2. [권장 사항 2 잠김]</b> 액세스 코드 입력 후 공개됩니다.</p>"
            "<p><b>3. [권장 사항 3 잠김]</b> 액세스 코드 입력 후 공개됩니다.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        for i, rec in enumerate(recs[1:3], 2):
            st.markdown(f"**{i}. {rec}**")

    # After text
    st.divider()
    st.markdown("### GEO 최적화 후 예상 AI 응답 (After)")
    with st.spinner("최적화 후 AI 응답 시뮬레이션 중..."):
        try:
            after = get_after(before, audit, recs, company_name, product_category)
        except Exception as e:
            after = f"오류: {e}"
    st.success(after)
    st.session_state["after"] = after

    # Generate PDF eagerly (no re-run on download click)
    pdf_bytes = None
    _pdf_error = ""
    try:
        from geo_report_pdf import generate_pdf
        pdf_path = generate_pdf(audit, recs, before_text=before)
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
    except Exception as e:
        _pdf_error = str(e)

    # Generate kit eagerly
    kit_files = None
    kit_zip_bytes = None
    _kit_error = ""
    try:
        from geo_deliverables import generate_deliverables, zip_deliverables
        kit_files = generate_deliverables(
            audit,
            company_name=company_name,
            product_category=product_category,
        )
        zip_path = zip_deliverables(kit_files)
        with open(zip_path, "rb") as f:
            kit_zip_bytes = f.read()
    except Exception as e:
        _kit_error = str(e)

    st.session_state["pdf_bytes"] = pdf_bytes
    st.session_state["kit_files"] = kit_files
    st.session_state["kit_zip_bytes"] = kit_zip_bytes
    st.session_state["company_name"] = company_name

    st.divider()
    st.markdown("### 리포트 및 구현 파일")
    safe_name = re.sub(r"[^\w\-]", "_", company_name)
    col_pdf, col_kit = st.columns(2)

    with col_pdf:
        if not _has_access():
            st.info("PDF 리포트는 액세스 코드가 필요합니다.")
        elif pdf_bytes:
            st.download_button(
                label="PDF 리포트 다운로드",
                data=pdf_bytes,
                file_name=f"GEO_Audit_{safe_name}.pdf",
                mime="application/pdf",
                type="secondary",
            )
        else:
            st.error(f"PDF 생성 오류: {_pdf_error}")

    with col_kit:
        if not _has_access():
            st.info("구현 파일은 액세스 코드가 필요합니다.")
        elif kit_zip_bytes:
            st.download_button(
                label="구현 파일 다운로드 (ZIP)",
                data=kit_zip_bytes,
                file_name=f"GEO_Implementation_{safe_name}.zip",
                mime="application/zip",
                type="secondary",
            )
        else:
            st.error(f"구현 파일 생성 오류: {_kit_error}")

    if kit_files and _has_access():
        st.markdown("#### 구현 파일 미리보기")
        for fname, fpath in kit_files.items():
            icon = _KIT_ICONS.get(fname, "📄")
            try:
                content = Path(fpath).read_text(encoding="utf-8")
            except Exception:
                content = "(파일을 읽을 수 없습니다)"
            lang = "json" if fname.endswith(".json") else "text"
            with st.expander(f"{icon} {fname}"):
                st.code(content, language=lang)

elif "audit" in st.session_state and not run:
    audit = st.session_state["audit"]
    recs = st.session_state.get("recs", [])
    before = st.session_state.get("before", "")
    pdf_bytes = st.session_state.get("pdf_bytes")
    kit_files = st.session_state.get("kit_files")
    kit_zip_bytes = st.session_state.get("kit_zip_bytes")
    saved_company = st.session_state.get("company_name", audit.get("corp_name", "company"))

    st.info(f"이전 진단 결과 ({saved_company})가 있습니다. 새 회사를 입력하거나 파일을 다운로드하세요.")
    safe_name = re.sub(r"[^\w\-]", "_", saved_company)
    col_pdf, col_kit = st.columns(2)

    with col_pdf:
        if not _has_access():
            st.info("PDF 리포트는 액세스 코드가 필요합니다.")
        elif pdf_bytes:
            st.download_button(
                label="PDF 리포트 다운로드 (이전 결과)",
                data=pdf_bytes,
                file_name=f"GEO_Audit_{safe_name}.pdf",
                mime="application/pdf",
                type="secondary",
            )
        else:
            st.warning("PDF를 다시 생성하려면 진단을 다시 실행하세요.")

    with col_kit:
        if not _has_access():
            st.info("구현 파일은 액세스 코드가 필요합니다.")
        elif kit_zip_bytes:
            st.download_button(
                label="구현 파일 다운로드 (이전 결과)",
                data=kit_zip_bytes,
                file_name=f"GEO_Implementation_{safe_name}.zip",
                mime="application/zip",
                type="secondary",
            )
        else:
            st.warning("구현 파일을 다시 생성하려면 진단을 다시 실행하세요.")

    if kit_files and _has_access():
        st.markdown("#### 구현 파일 미리보기")
        for fname, fpath in kit_files.items():
            icon = _KIT_ICONS.get(fname, "📄")
            try:
                content = Path(fpath).read_text(encoding="utf-8")
            except Exception:
                content = "(파일을 읽을 수 없습니다)"
            lang = "json" if fname.endswith(".json") else "text"
            with st.expander(f"{icon} {fname}"):
                st.code(content, language=lang)

st.divider()
st.caption("Built by Keonhee Kim | SKKU Business Administration | GEO Consulting")
