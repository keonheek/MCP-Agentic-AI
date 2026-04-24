"""Automations Page — Follow-Up Queue + Speed-to-Lead + Reactivation (Nate Herk)"""

import streamlit as st
from db import (
    list_messages, update_message_status, message_stats,
    list_clients, list_interactions, cold_leads, queue_message,
)
from ai_engine import generate_followup, generate_reactivation_message, _has_api
from datetime import datetime

st.header("AI 자동화")

with st.expander("이 기능은 무엇인가요?", icon=":material/info:"):
    st.markdown("""
**AI 자동화 3단계 (Nate Herk 프레임워크):**
1. **Speed-to-Lead** - 새 리드 등록 즉시 개인화 아웃리치 메시지 자동 생성 (응답 시간 47시간 -> 5분)
2. **Follow-Up Sequences** - 3일 무응답 고객에게 AI가 팔로업 초안 작성 (영업의 80%는 5회 이상 팔로업 필요)
3. **Database Reactivation** - 30일 이상 연락 없는 고객 재활성화 캠페인 (기존 고객 DB 활용)

모든 메시지는 AI가 생성하고, 사람이 검토 후 발송합니다.
    """)

# ─── Stats ─────────────────────────────────────────────────

stats = message_stats()
s1, s2, s3 = st.columns(3)
s1.metric("대기 중", stats.get("pending", 0))
s2.metric("발송 완료", stats.get("sent", 0))
s3.metric("건너뜀", stats.get("skipped", 0))

st.divider()

# ─── Follow-Up Generator ──────────────────────────────────

tab_followup, tab_stl, tab_reactivation, tab_stack = st.tabs([
    "팔로업 생성", "즉시 아웃리치 (Speed-to-Lead)", "재활성화", "Tech Stack"
])

with tab_followup:
    st.subheader("자동 팔로업 메시지 생성")
    st.markdown("3일 이상 응답 없는 고객에게 AI가 팔로업 메시지를 생성합니다.")

    if not _has_api():
        st.warning("ANTHROPIC_API_KEY가 설정되지 않았습니다. .env 파일에 키를 추가하면 AI 팔로업이 활성화됩니다.")

    if st.button("팔로업 생성 실행", type="primary", key="gen_followups"):
        if not _has_api():
            st.error("AI 팔로업을 생성하려면 ANTHROPIC_API_KEY가 필요합니다.")
        else:
            clients = list_clients()
            generated = 0
            with st.spinner("팔로업 메시지 생성 중..."):
                for c in clients:
                    if c["status"] in ("churned", "converted", "retainer"):
                        continue
                    interactions = list_interactions(c["id"])
                    if interactions:
                        last_dt = datetime.strptime(interactions[0]["created_at"][:19], "%Y-%m-%d %H:%M:%S")
                        days_since = (datetime.now() - last_dt).days
                    else:
                        days_since = (datetime.now() - datetime.strptime(c["created_at"][:19], "%Y-%m-%d %H:%M:%S")).days

                    if days_since >= 3:
                        msg = generate_followup(c, interactions)
                        if msg:
                            queue_message(c["id"], "followup", msg)
                            generated += 1

            if generated > 0:
                st.success(f"{generated}건의 팔로업 메시지가 생성되었습니다.")
                st.rerun()
            else:
                st.info("팔로업이 필요한 고객이 없습니다.")

with tab_stl:
    st.subheader("즉시 아웃리치 메시지")
    st.markdown("새 고객 등록 시 자동 생성된 아웃리치 메시지입니다. 카카오톡으로 복사해서 발송하세요.")

    stl_msgs = list_messages(type="speed_to_lead")
    if not stl_msgs:
        st.info("Speed-to-Lead 메시지가 없습니다. 고객 등록 시 웹사이트 URL을 입력하면 자동 생성됩니다.")
    else:
        for m in stl_msgs:
            status_icon = {"pending": "hourglass_empty", "sent": "check_circle", "skipped": "cancel"}.get(m["status"], "help")
            with st.expander(f":{status_icon}: **{m['business_name']}** | {m['created_at'][:16]}"):
                st.code(m["message"], language=None)
                if m["status"] == "pending":
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("발송 완료", key=f"stl_sent_{m['id']}", type="primary"):
                            update_message_status(m["id"], "sent")
                            st.rerun()
                    with c2:
                        if st.button("건너뛰기", key=f"stl_skip_{m['id']}"):
                            update_message_status(m["id"], "skipped")
                            st.rerun()

with tab_reactivation:
    st.subheader("이탈 고객 재활성화")
    st.markdown("30일 이상 연락 없는 고객에게 경쟁 데이터 기반 재활성화 메시지를 생성합니다.")

    if not _has_api():
        st.warning("ANTHROPIC_API_KEY가 설정되지 않았습니다. .env 파일에 키를 추가하면 재활성화가 활성화됩니다.")

    if st.button("재활성화 실행", type="primary", key="gen_reactivation"):
        if not _has_api():
            st.error("재활성화 메시지를 생성하려면 ANTHROPIC_API_KEY가 필요합니다.")
        else:
            cold = cold_leads(days=30)
            generated = 0
            with st.spinner("재활성화 메시지 생성 중..."):
                for c in cold:
                    msg = generate_reactivation_message(c)
                    if msg:
                        queue_message(c["id"], "reactivation", msg)
                        generated += 1

            if generated > 0:
                st.success(f"{generated}건의 재활성화 메시지가 생성되었습니다.")
                st.rerun()
            else:
                st.info("재활성화 대상 고객이 없습니다.")

with tab_stack:
    st.subheader("Product Architecture")
    st.caption("각 레이어가 어떤 비즈니스 기능을 담당하는지 보여줍니다.")

    st.markdown("""
    <style>
    .arch-row {
        display: grid;
        grid-template-columns: 90px 1fr 1fr;
        gap: 0.6rem;
        align-items: start;
        margin-bottom: 0.75rem;
    }
    .arch-badge {
        background: #1B2A4A;
        color: #00C7BE;
        font-weight: bold;
        font-size: 0.72rem;
        padding: 6px 8px;
        border-radius: 6px;
        text-align: center;
    }
    .arch-component {
        background: #0F1E38;
        border: 1px solid #1E3A5F;
        border-radius: 6px;
        padding: 0.6rem 0.8rem;
        font-size: 0.8rem;
        color: #F1F5F9;
    }
    .arch-component b { color: #00C7BE; }
    .arch-component small { color: #64748B; display: block; margin-top: 2px; }
    .arch-feature {
        background: #0A1A30;
        border: 1px solid #1E3A5F;
        border-radius: 6px;
        padding: 0.6rem 0.8rem;
        font-size: 0.78rem;
        color: #CBD5E1;
    }
    .arch-feature b { color: #F1F5F9; }
    </style>

    <div class="arch-row">
      <div class="arch-badge">UI Layer</div>
      <div class="arch-component">
        <b>Streamlit</b>
        <small>pages/, sidebar, st.navigation</small>
      </div>
      <div class="arch-feature">
        <b>담당 기능:</b> 5-page multi-app, KPI cards, Plotly charts, sidebar branding, filters
      </div>
    </div>

    <div class="arch-row">
      <div class="arch-badge">AI Layer</div>
      <div class="arch-component">
        <b>Claude API (Haiku)</b>
        <small>ai_engine.py — claude-haiku-4-5</small>
      </div>
      <div class="arch-feature">
        <b>담당 기능:</b> follow-up message drafts, speed-to-lead outreach, quote item suggestions, weekly report generation, reactivation messages
      </div>
    </div>

    <div class="arch-row">
      <div class="arch-badge">Logic Layer</div>
      <div class="arch-component">
        <b>Python</b>
        <small>db.py — query functions</small>
      </div>
      <div class="arch-feature">
        <b>담당 기능:</b> KPI aggregation (monthly_revenue, conversion_rate, open_quotes_value), pipeline_counts, expiring quote alerts, cold lead detection
      </div>
    </div>

    <div class="arch-row">
      <div class="arch-badge">Data Layer</div>
      <div class="arch-component">
        <b>SQLite</b>
        <small>erp_demo.db — schema.sql</small>
      </div>
      <div class="arch-feature">
        <b>담당 기능:</b> clients, quotes, quote_items, invoices, interactions, message_queue — 6 normalized tables with FK constraints
      </div>
    </div>

    <div class="arch-row">
      <div class="arch-badge">Doc Layer</div>
      <div class="arch-component">
        <b>fpdf2</b>
        <small>pdf_gen.py — Navy/Teal style</small>
      </div>
      <div class="arch-feature">
        <b>담당 기능:</b> quote PDFs (견적서), invoice PDFs (청구서) — Korean font, VAT table, GEO Agency branding
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.subheader("Production Upgrade Path")
    col_now, col_prod = st.columns(2)
    with col_now:
        st.markdown("**현재 (Demo)**")
        st.markdown("""
- UI: Streamlit (rapid prototyping)
- AI: Claude Haiku (cost-effective)
- DB: SQLite (zero-config, local)
- Deploy: `streamlit run app.py`
- PDF: fpdf2 (lightweight)
        """)
    with col_prod:
        st.markdown("**Production 업그레이드**")
        st.markdown("""
- UI: Next.js + FastAPI (scale + auth)
- AI: Claude Sonnet (complex workflows)
- DB: PostgreSQL + Redis cache
- Deploy: Vercel (FE) + AWS Lambda (BE)
- PDF: WeasyPrint or external PDF API
- Add: n8n automation triggers, webhook 알림
        """)

    st.info("현재 데모는 Streamlit + SQLite로 동작합니다. 실제 고객사 배포 시 위 업그레이드 경로를 따릅니다.")

st.divider()

# ─── Message Queue ─────────────────────────────────────────

st.subheader("메시지 대기열")

mf1, mf2 = st.columns([1, 3])
with mf1:
    msg_filter_options = {"전체": None, "대기 중": "pending", "발송 완료": "sent", "건너뜀": "skipped"}
    msg_filter = st.selectbox("상태", list(msg_filter_options.keys()), key="msg_filter")

msg_status = msg_filter_options[msg_filter]
messages = list_messages(status=msg_status)

TYPE_LABELS = {
    "followup": "팔로업",
    "speed_to_lead": "즉시 아웃리치",
    "reactivation": "재활성화",
}
TYPE_COLORS = {
    "followup": "blue",
    "speed_to_lead": "green",
    "reactivation": "violet",
}

if not messages:
    st.info("대기 중인 메시지가 없습니다.")
else:
    for m in messages:
        t_label = TYPE_LABELS.get(m["type"], m["type"])
        t_color = TYPE_COLORS.get(m["type"], "gray")
        status_icon = {"pending": "hourglass_empty", "sent": "check_circle", "skipped": "cancel"}.get(m["status"], "help")

        with st.expander(
            f":{status_icon}: **{m['business_name']}** | :{t_color}-badge[{t_label}] | {m['channel']} | {m['created_at'][:16]}"
        ):
            st.markdown(f"**받는 사람:** {m['client_name']} ({m['business_name']})")
            st.markdown(f"**채널:** {m['channel']}")
            st.code(m["message"], language=None)

            if m["status"] == "pending":
                bc1, bc2 = st.columns(2)
                with bc1:
                    if st.button("발송 완료 표시", key=f"msent_{m['id']}", type="primary"):
                        update_message_status(m["id"], "sent")
                        st.rerun()
                with bc2:
                    if st.button("건너뛰기", key=f"mskip_{m['id']}"):
                        update_message_status(m["id"], "skipped")
                        st.rerun()
