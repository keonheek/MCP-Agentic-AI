"""Clients Page — CRUD + Interaction Log + AI Next-Action"""

import streamlit as st
from datetime import datetime
from db import (
    list_clients, get_client, create_client, update_client, delete_client,
    list_interactions, add_interaction, list_quotes, list_invoices,
    CLIENT_STATUSES, INTERACTION_TYPES, SOURCES, queue_message,
)
from ai_engine import get_next_action, generate_speed_to_lead_message

st.header("고객 관리")

# ─── Korean Label Maps ────────────────────────────────────

STATUS_LABELS = {
    "lead": "리드", "contacted": "연락완료", "quoted": "견적발송",
    "converted": "계약완료", "retainer": "리테이너", "churned": "이탈",
}
SOURCE_LABELS = {
    "soomgo": "숨고", "kmong": "크몽", "kakao": "카카오",
    "referral": "소개", "naver": "네이버", "other": "기타",
}
IX_LABELS = {
    "call": "전화", "kakao": "카카오", "email": "이메일",
    "meeting": "미팅", "note": "메모",
}
QUOTE_STATUS_KR = {
    "draft": "초안", "sent": "발송", "accepted": "수락",
    "rejected": "거절", "expired": "만료",
}
INV_STATUS_KR = {
    "unpaid": "미납", "paid": "완납", "overdue": "연체", "cancelled": "취소",
}

# ─── Filters ───────────────────────────────────────────────

col_search, col_filter = st.columns([2, 1])
with col_search:
    search = st.text_input("검색", placeholder="이름, 상호, 카카오 ID...")
with col_filter:
    status_options = {"전체": None, **{v: k for k, v in STATUS_LABELS.items()}}
    status_filter = st.selectbox("상태 필터", list(status_options.keys()))

status_val = status_options[status_filter]
clients = list_clients(status=status_val, search=search or None)

# ─── Add Client ────────────────────────────────────────────

with st.expander("새 고객 추가", icon=":material/person_add:"):
    with st.form("add_client"):
        ac1, ac2 = st.columns(2)
        with ac1:
            new_name = st.text_input("담당자 이름 *")
            new_biz = st.text_input("상호명 *")
            new_phone = st.text_input("전화번호")
            new_email = st.text_input("이메일")
        with ac2:
            new_kakao = st.text_input("카카오톡 ID")
            new_website = st.text_input("웹사이트 URL")
            source_display = st.selectbox("유입 경로", list(SOURCE_LABELS.values()))
            new_source = {v: k for k, v in SOURCE_LABELS.items()}[source_display]
            new_notes = st.text_area("메모", height=68)

        submitted = st.form_submit_button("고객 추가", type="primary")
        if submitted:
            if not new_name or not new_biz:
                st.error("담당자 이름과 상호명은 필수입니다.")
            else:
                cid = create_client(
                    name=new_name, business_name=new_biz, phone=new_phone,
                    email=new_email, kakao_id=new_kakao, website=new_website,
                    source=new_source, notes=new_notes,
                )
                # Speed-to-lead: auto-generate outreach if website provided
                if new_website:
                    msg = generate_speed_to_lead_message(
                        {"name": new_name, "business_name": new_biz, "website": new_website},
                    )
                    if msg and not msg.startswith("[AI 비활성]"):
                        queue_message(cid, "speed_to_lead", msg)
                st.success(f"고객 추가 완료: {new_biz}")
                st.rerun()

# ─── Client List ───────────────────────────────────────────

if not clients:
    st.info("등록된 고객이 없습니다.")
else:
    STATUS_COLORS = {
        "lead": "blue", "contacted": "orange", "quoted": "violet",
        "converted": "green", "retainer": "rainbow", "churned": "red",
    }

    for c in clients:
        color = STATUS_COLORS.get(c["status"], "gray")
        label = STATUS_LABELS.get(c["status"], c["status"])

        with st.expander(f"**{c['business_name']}** | {c['name']} | :{color}-badge[{label}]"):
            # ─── Client Detail ─────────────────────────
            det1, det2, det3 = st.columns(3)
            with det1:
                st.markdown(f"**전화:** {c.get('phone') or '-'}")
                st.markdown(f"**이메일:** {c.get('email') or '-'}")
                st.markdown(f"**카카오:** {c.get('kakao_id') or '-'}")
            with det2:
                st.markdown(f"**웹사이트:** {c.get('website') or '-'}")
                st.markdown(f"**유입:** {SOURCE_LABELS.get(c.get('source', ''), c.get('source') or '-')}")
                geo = c.get('geo_score')
                st.markdown(f"**GEO 점수:** {geo}/100" if geo is not None else "**GEO 점수:** -")
            with det3:
                st.markdown(f"**등록일:** {c['created_at'][:10]}")
                st.markdown(f"**최종 업데이트:** {c['updated_at'][:10]}")
                if c.get("notes"):
                    st.markdown(f"**메모:** {c['notes']}")

            # ─── AI Next Action ────────────────────────
            interactions = list_interactions(c["id"])
            if interactions:
                last_dt = datetime.strptime(interactions[0]["created_at"][:19], "%Y-%m-%d %H:%M:%S")
                days_since = (datetime.now() - last_dt).days
            else:
                created_dt = datetime.strptime(c["created_at"][:19], "%Y-%m-%d %H:%M:%S")
                days_since = (datetime.now() - created_dt).days

            action = get_next_action(c, days_since)
            st.markdown(
                f'<div style="background:#0F4C4C;border-left:4px solid #00C7BE;padding:0.7rem 1rem;border-radius:4px;margin:0.5rem 0;">'
                f'<span style="color:#00C7BE;font-weight:bold;">AI 추천</span> '
                f'<span style="color:#F8FAFC;">{action}</span></div>',
                unsafe_allow_html=True,
            )

            # ─── Interaction Timeline ──────────────────
            st.markdown("##### 상호작용 이력")
            if interactions:
                for ix in interactions[:10]:
                    ix_label = IX_LABELS.get(ix['type'], ix['type'])
                    st.markdown(f"- **[{ix_label}]** {ix['created_at'][:16]} - {ix['content']}")
            else:
                st.caption("아직 상호작용이 없습니다.")

            # ─── Add Interaction ───────────────────────
            with st.form(f"add_ix_{c['id']}"):
                ix1, ix2 = st.columns([1, 3])
                with ix1:
                    ix_type_display = st.selectbox("유형", list(IX_LABELS.values()), key=f"ixt_{c['id']}")
                    ix_type = {v: k for k, v in IX_LABELS.items()}[ix_type_display]
                with ix2:
                    ix_content = st.text_input("내용", key=f"ixc_{c['id']}")
                if st.form_submit_button("상호작용 추가"):
                    if ix_content:
                        add_interaction(c["id"], ix_type, ix_content)
                        st.success("추가 완료")
                        st.rerun()

            # ─── Linked Quotes / Invoices ──────────────
            q_list = list_quotes(client_id=c["id"])
            i_list = list_invoices(client_id=c["id"])
            lk1, lk2 = st.columns(2)
            with lk1:
                if q_list:
                    st.markdown("##### 연결된 견적서")
                    for q in q_list:
                        qs_kr = QUOTE_STATUS_KR.get(q['status'], q['status'])
                        st.markdown(f"- {q['quote_number']} | {qs_kr} | {q['total']:,}원")
            with lk2:
                if i_list:
                    st.markdown("##### 연결된 청구서")
                    for inv in i_list:
                        is_kr = INV_STATUS_KR.get(inv['status'], inv['status'])
                        st.markdown(f"- {inv['invoice_number']} | {is_kr} | {inv['total_amount']:,}원")

            # ─── Edit / Delete ─────────────────────────
            ed1, ed2, ed3 = st.columns([2, 1, 1])
            with ed1:
                status_kr_list = list(STATUS_LABELS.values())
                status_en_list = list(STATUS_LABELS.keys())
                current_idx = status_en_list.index(c["status"]) if c["status"] in status_en_list else 0
                new_status_kr = st.selectbox(
                    "상태 변경", status_kr_list,
                    index=current_idx,
                    key=f"st_{c['id']}",
                )
                new_status = {v: k for k, v in STATUS_LABELS.items()}[new_status_kr]
                if new_status != c["status"]:
                    if st.button("상태 업데이트", key=f"upd_{c['id']}"):
                        update_client(c["id"], status=new_status)
                        st.rerun()
            with ed3:
                if st.button("고객 삭제", key=f"del_{c['id']}", type="secondary"):
                    delete_client(c["id"])
                    st.rerun()
