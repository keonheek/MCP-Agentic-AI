"""Dashboard — KPIs + Pipeline Funnel + Activity Feed + Alerts"""

import streamlit as st
import plotly.graph_objects as go
from db import (
    pipeline_counts, total_clients, conversion_rate, open_quotes_value,
    monthly_revenue, recent_activity, expiring_quotes, overdue_invoices, cold_leads,
)
from ai_engine import generate_weekly_report

st.header("대시보드")

# ─── KPI Cards ─────────────────────────────────────────────

tc = total_clients()
cr = conversion_rate()
oq = open_quotes_value()
mr = monthly_revenue()

c1, c2, c3, c4 = st.columns(4)
c1.metric("총 고객", f"{tc}명")
c2.metric("전환율", f"{cr}%")
c3.metric("미결 견적", f"{oq:,}원")
c4.metric("이번 달 매출", f"{mr:,}원")

st.divider()

# ─── Pipeline Funnel ───────────────────────────────────────

col_funnel, col_alerts = st.columns([3, 2])

with col_funnel:
    st.subheader("파이프라인")
    counts = pipeline_counts()
    stages = ["lead", "contacted", "quoted", "converted", "retainer"]
    labels = ["리드", "연락 완료", "견적 발송", "계약 완료", "리테이너"]
    values = [counts.get(s, 0) for s in stages]

    if any(v > 0 for v in values):
        fig = go.Figure(go.Funnel(
            y=labels,
            x=values,
            textinfo="value+percent initial",
            marker=dict(color=["#1B2A4A", "#0F4C75", "#1B7A8C", "#00A896", "#00C7BE"]),
        ))
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=10),
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F8FAFC"),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("고객 데이터가 없습니다. 고객 관리 페이지에서 고객을 추가하세요.")

# ─── Alerts ────────────────────────────────────────────────

with col_alerts:
    st.subheader("알림")

    exp_q = expiring_quotes()
    if exp_q:
        for q in exp_q:
            st.warning(f"견적 만료 임박: **{q['business_name']}** — {q['quote_number']} ({q['valid_until']}까지, {q['total']:,}원)")

    od_inv = overdue_invoices()
    if od_inv:
        for inv in od_inv:
            st.error(f"미수금: **{inv['business_name']}** — {inv['invoice_number']} ({inv['total_amount']:,}원, 기한: {inv['due_date']})")

    cl = cold_leads()
    if cl:
        for c in cl[:3]:
            st.warning(f"이탈 위험: **{c['business_name']}** — 마지막 업데이트 {c['updated_at'][:10]}")

    if not exp_q and not od_inv and not cl:
        st.success("특별한 알림이 없습니다.")

st.divider()

# ─── Recent Activity ───────────────────────────────────────

col_act, col_report = st.columns([3, 2])

with col_act:
    st.subheader("최근 활동")
    TYPE_LABELS = {"call": "전화", "kakao": "카카오", "email": "이메일", "meeting": "미팅", "note": "메모"}
    TYPE_ICONS = {"call": ":telephone_receiver:", "kakao": ":speech_balloon:", "email": ":email:", "meeting": ":busts_in_silhouette:", "note": ":memo:"}

    activity = recent_activity(10)
    if activity:
        for a in activity:
            icon = TYPE_ICONS.get(a["type"], ":memo:")
            label = TYPE_LABELS.get(a["type"], a["type"])
            content = a.get("content") or ""
            st.markdown(
                f"{icon} **{a['business_name']}** - {label} | {content[:60]}{'...' if len(content) > 60 else ''} "
                f"<span style='color:#64748B;font-size:0.8rem;'>{a['created_at'][:16]}</span>",
                unsafe_allow_html=True,
            )
    else:
        st.info("아직 활동 기록이 없습니다.")

# ─── Weekly Report ─────────────────────────────────────────

with col_report:
    st.subheader("주간 리포트")
    if st.button("AI 주간 리포트 생성", type="primary"):
        with st.spinner("리포트 생성 중..."):
            stats = {
                "total_clients": tc,
                "conversion_rate": cr,
                "monthly_revenue": mr,
                "open_quotes": oq,
                "expiring_quotes": len(exp_q),
                "overdue_invoices": len(od_inv),
                "cold_leads": len(cl),
            }
            report = generate_weekly_report(stats)
            st.session_state["weekly_report"] = report

    if "weekly_report" in st.session_state:
        report = st.session_state["weekly_report"]
        st.markdown(
            f'<div style="background:#0F4C4C;border-left:4px solid #00C7BE;padding:0.8rem 1rem;border-radius:4px;">'
            f'<span style="color:#00C7BE;font-weight:bold;">AI 주간 리포트</span><br/>'
            f'<span style="color:#F8FAFC;">{report}</span></div>',
            unsafe_allow_html=True,
        )

# ─── Revenue Trend + Tech Stack Panel ─────────────────────

col_rev, col_stack = st.columns([3, 2])

with col_rev:
    st.subheader("매출 추이")
    from datetime import datetime as _dt
    _now = _dt.now()
    _months = []
    _revenues = []
    for i in range(5, -1, -1):
        m = _now.month - i
        y = _now.year
        if m <= 0:
            m += 12
            y -= 1
        _months.append(f"{y}-{m:02d}")
        _revenues.append(monthly_revenue(y, m))

    if any(r > 0 for r in _revenues):
        rev_fig = go.Figure(go.Bar(
            x=_months, y=_revenues,
            marker=dict(color="#00C7BE", line=dict(color="#1B2A4A", width=1)),
            text=[f"{r:,}" if r > 0 else "" for r in _revenues],
            textposition="outside",
        ))
        rev_fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=30),
            height=250,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F8FAFC"),
            yaxis=dict(gridcolor="rgba(100,116,139,0.2)", title="원"),
            xaxis=dict(title=""),
        )
        st.plotly_chart(rev_fig, use_container_width=True)
    else:
        st.info("아직 수금 내역이 없습니다.")

with col_stack:
    st.subheader("Tech Stack")
    st.markdown("""
    <style>
    .stack-card {
        background: #0F1E38;
        border: 1px solid #1E3A5F;
        border-radius: 8px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.5rem;
    }
    .stack-layer {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        margin-bottom: 0.65rem;
    }
    .stack-badge {
        background: #1B2A4A;
        color: #00C7BE;
        font-size: 0.7rem;
        font-weight: bold;
        padding: 2px 7px;
        border-radius: 4px;
        white-space: nowrap;
        min-width: 48px;
        text-align: center;
        margin-top: 2px;
    }
    .stack-detail { color: #CBD5E1; font-size: 0.8rem; line-height: 1.4; }
    .stack-detail b { color: #F1F5F9; }
    .stack-divider { border: none; border-top: 1px solid #1E3A5F; margin: 0.5rem 0; }
    .upgrade-box {
        background: #0A2E2E;
        border-left: 3px solid #00C7BE;
        border-radius: 4px;
        padding: 0.6rem 0.8rem;
        margin-top: 0.75rem;
        font-size: 0.75rem;
        color: #94A3B8;
    }
    .upgrade-box b { color: #00C7BE; }
    </style>

    <div class="stack-card">
      <div class="stack-layer">
        <span class="stack-badge">UI</span>
        <div class="stack-detail">
          <b>Streamlit</b><br/>
          Pages, sidebar KPIs, charts — all rendered here
        </div>
      </div>
      <hr class="stack-divider"/>
      <div class="stack-layer">
        <span class="stack-badge">AI</span>
        <div class="stack-detail">
          <b>Claude API (Haiku)</b><br/>
          Follow-up drafts, quote suggestions, weekly summaries
        </div>
      </div>
      <hr class="stack-divider"/>
      <div class="stack-layer">
        <span class="stack-badge">Logic</span>
        <div class="stack-detail">
          <b>Python</b><br/>
          KPI aggregation, pipeline counts, conversion rate
        </div>
      </div>
      <hr class="stack-divider"/>
      <div class="stack-layer">
        <span class="stack-badge">Data</span>
        <div class="stack-detail">
          <b>SQLite</b><br/>
          clients, quotes, invoices, message_queue tables
        </div>
      </div>
      <hr class="stack-divider"/>
      <div class="stack-layer">
        <span class="stack-badge">Docs</span>
        <div class="stack-detail">
          <b>fpdf2</b><br/>
          Quote + invoice PDFs with Navy/Teal branding
        </div>
      </div>

      <div class="upgrade-box">
        <b>Production upgrade path:</b><br/>
        SQLite → PostgreSQL &nbsp;|&nbsp; Streamlit → Next.js + FastAPI<br/>
        Claude Haiku → Claude Sonnet (complex workflows)<br/>
        Add: Vercel deploy, webhook triggers, n8n automations
      </div>
    </div>
    """, unsafe_allow_html=True)
