"""
GEO Agency - Streamlit App

Single-company GEO audit tool for client demos and service delivery.
Input: company name -> GEO audit -> before/after proof -> PDF download
"""

import os
import sys
import time
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
        help="DART 상장 여부 무관 — 어떤 회사든 가능합니다"
    )
    product_category = st.text_input(
        "주요 제품/서비스 카테고리 (선택)",
        placeholder="예: 반도체 소재, IT 컨설팅, 온라인 쇼핑몰",
        help="AI 추천 쿼리를 더 정확하게 만들기 위해 사용됩니다"
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

    # Score display
    st.markdown(f"## {company_name} GEO Score")
    color = "green" if geo_score >= 70 else ("orange" if geo_score >= 40 else "red")
    label = "High" if geo_score >= 70 else ("Medium" if geo_score >= 40 else "Low")
    st.markdown(f"<h1 style='color:{color}'>{geo_score}/100 — {label}</h1>", unsafe_allow_html=True)
    st.caption(f"웹사이트: {website}")

    # 5-category GEO breakdown
    st.markdown("#### 5-Category GEO Breakdown")

    # Category 1: AI Citability & Share of Voice (max 50)
    citability = breakdown.get("citability", 0)
    sov = breakdown.get("share_of_voice", 0)
    cat1 = citability + sov
    col_c1, col_c2, col_cat1 = st.columns([2, 2, 1])
    with col_c1:
        st.metric("AI Citability", f"{citability}/40")
    with col_c2:
        st.metric("Share of Voice", f"{sov}/10")
    with col_cat1:
        st.metric("Cat 1 Total", f"{cat1}/50")

    # Category 2: Crawler & Agent Accessibility (max 30)
    ai_bot = breakdown.get("ai_bot_access", breakdown.get("crawler_access", 0))
    ai_policy = breakdown.get("ai_policy_file", breakdown.get("llms_txt", 0))
    cat2 = ai_bot + ai_policy
    col_c3, col_c4, col_cat2 = st.columns([2, 2, 1])
    with col_c3:
        st.metric("AI Bot Access", f"{ai_bot}/20")
    with col_c4:
        st.metric("AI Policy File (llms.txt)", f"{ai_policy}/10")
    with col_cat2:
        st.metric("Cat 2 Total", f"{cat2}/30")

    # Category 3: Schema & Structured Data (max 30)
    org_schema = breakdown.get("org_schema", 0)
    content_schema = breakdown.get("content_schema", 0)
    cat3 = org_schema + content_schema
    col_c5, col_c6, col_cat3 = st.columns([2, 2, 1])
    with col_c5:
        st.metric("Org Schema", f"{org_schema}/15")
    with col_c6:
        st.metric("Content Schema", f"{content_schema}/15")
    with col_cat3:
        st.metric("Cat 3 Total", f"{cat3}/30")

    # Category 4: Local Sync — KR Platforms (max 20)
    naver = breakdown.get("naver_presence", 0)
    kr_sync = breakdown.get("kr_platform_sync", breakdown.get("korean_presence", 0) - breakdown.get("naver_presence", 0))
    cat4 = naver + kr_sync
    col_c7, col_c8, col_cat4 = st.columns([2, 2, 1])
    with col_c7:
        st.metric("Naver Presence", f"{naver}/10")
    with col_c8:
        st.metric("KR Platform Sync", f"{kr_sync}/10")
    with col_cat4:
        st.metric("Cat 4 Total", f"{cat4}/20")

    # Category 5: Brand Sentiment & Mention Quality (max 20)
    brand_mention = breakdown.get("brand_mention", 0)
    sentiment_quality = breakdown.get("sentiment_quality", 0)
    cat5 = brand_mention + sentiment_quality
    col_c9, col_c10, col_cat5 = st.columns([2, 2, 1])
    with col_c9:
        st.metric("Brand Mention", f"{brand_mention}/10")
    with col_c10:
        st.metric("Sentiment Quality", f"{sentiment_quality}/10")
    with col_cat5:
        st.metric("Cat 5 Total", f"{cat5}/20")

    # Competitors from SoV
    sov_competitors = audit.get("sov_competitors", [])
    sov_cited = audit.get("sov_cited", False)
    if sov_competitors:
        cited_label = "포함됨" if sov_cited else "미포함"
        st.markdown(
            f"**경쟁사 AI 인용 현황:** {', '.join(sov_competitors[:5])} "
            f"| 귀사 인용 여부: **{cited_label}**"
        )

    st.session_state["audit"] = audit

    # Before/after
    st.divider()
    st.markdown("### AI 가시성 현황 (Before)")
    with st.spinner("AI가 현재 이 회사에 대해 뭐라고 하는지 확인 중..."):
        try:
            from before_after import get_before, get_after
            before = get_before(company_name, product_category)
        except Exception as e:
            before = f"오류: {e}"

    st.info(before[:800] + ("..." if len(before) > 800 else ""))
    st.session_state["before"] = before

    # Dynamic recommendations based on actual scores
    from geo_audit import generate_dynamic_recommendations
    recs = generate_dynamic_recommendations(breakdown, company_name)
    st.session_state["recs"] = recs

    st.markdown("### GEO 최적화 후 예상 AI 응답 (After)")
    with st.spinner("최적화 후 AI 응답 시뮬레이션 중..."):
        try:
            after = get_after(before, audit, recs, company_name, product_category)
        except Exception as e:
            after = f"오류: {e}"

    st.success(after)
    st.session_state["after"] = after

    # PDF generation
    st.divider()
    st.markdown("### PDF 리포트 생성")
    if st.button("PDF 리포트 다운로드", type="secondary"):
        with st.spinner("PDF 생성 중..."):
            try:
                from geo_report_pdf import generate_pdf
                pdf_path = generate_pdf(audit, recs, before_text=before)
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                import re
                safe_name = re.sub(r"[^\w\-]", "_", company_name)
                st.download_button(
                    label="PDF 다운로드",
                    data=pdf_bytes,
                    file_name=f"GEO_Audit_{safe_name}.pdf",
                    mime="application/pdf",
                )
                st.success(f"PDF 생성 완료: {Path(pdf_path).name}")
            except Exception as e:
                st.error(f"PDF 생성 오류: {e}")

# PDF download if already generated (persists in session)
elif "audit" in st.session_state:
    st.info("이전 진단 결과가 있습니다. 새 회사를 입력하거나 PDF를 다운로드하세요.")
    audit = st.session_state["audit"]
    recs = st.session_state.get("recs", [])
    before = st.session_state.get("before", "")
    if st.button("PDF 리포트 다운로드 (이전 결과)", type="secondary"):
        with st.spinner("PDF 생성 중..."):
            try:
                from geo_report_pdf import generate_pdf
                pdf_path = generate_pdf(audit, recs, before_text=before)
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                import re
                safe_name = re.sub(r"[^\w\-]", "_", audit.get("corp_name", "company"))
                st.download_button(
                    label="PDF 다운로드",
                    data=pdf_bytes,
                    file_name=f"GEO_Audit_{safe_name}.pdf",
                    mime="application/pdf",
                )
            except Exception as e:
                st.error(f"PDF 생성 오류: {e}")

st.divider()
st.caption("Built by Keonhee Kim | SKKU Business Administration | GEO Consulting")
