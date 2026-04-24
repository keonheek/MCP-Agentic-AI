"""Quotes Page — Builder + Line Items + AI Suggest + Status Flow + PDF"""

import streamlit as st
from datetime import datetime, timedelta
from db import (
    list_clients, list_quotes, get_quote, create_quote,
    update_quote_status, create_invoice_from_quote, update_client, QUOTE_STATUSES,
)
from ai_engine import suggest_quote_items
from pdf_gen import generate_quote_pdf

st.header("견적서")

# ─── New Quote ─────────────────────────────────────────────

with st.expander("새 견적서 작성", icon=":material/add_circle:"):
    clients = list_clients()
    if not clients:
        st.warning("먼저 고객을 등록해주세요.")
    else:
        client_options = {f"{c['business_name']} ({c['name']})": c for c in clients}
        selected_client_label = st.selectbox("고객 선택", list(client_options.keys()))
        selected_client = client_options[selected_client_label]

        title = st.text_input("견적서 제목", value="GEO 최적화 패키지")
        valid_days = st.number_input("유효기간 (일)", value=30, min_value=7, max_value=90)
        valid_until = (datetime.now() + timedelta(days=valid_days)).strftime("%Y-%m-%d")
        notes = st.text_area("비고", height=68)

        # ─── AI Suggest ────────────────────────────
        if st.button("AI 추천 견적 항목", type="secondary"):
            with st.spinner("AI가 견적 항목을 추천합니다..."):
                suggested = suggest_quote_items(selected_client)
                st.session_state["suggested_items"] = suggested

        # ─── Line Items ───────────────────────────
        st.markdown("##### 견적 항목")

        if "quote_items" not in st.session_state:
            st.session_state["quote_items"] = []

        # Load AI suggestions if available
        if "suggested_items" in st.session_state and st.session_state["suggested_items"]:
            st.session_state["quote_items"] = st.session_state.pop("suggested_items")

        # Display current items
        items_to_keep = []
        for i, item in enumerate(st.session_state["quote_items"]):
            ic1, ic2, ic3, ic4 = st.columns([4, 1, 2, 1])
            with ic1:
                desc = st.text_input("항목", value=item["description"], key=f"qi_d_{i}")
            with ic2:
                qty = st.number_input("수량", value=item.get("quantity", 1), min_value=1, key=f"qi_q_{i}")
            with ic3:
                price = st.number_input("단가 (원)", value=item["unit_price"], min_value=0, step=10000, key=f"qi_p_{i}")
            with ic4:
                remove = st.button("삭제", key=f"qi_r_{i}")

            if not remove:
                items_to_keep.append({"description": desc, "quantity": qty, "unit_price": price})

        st.session_state["quote_items"] = items_to_keep

        # Add new item
        if st.button("항목 추가"):
            st.session_state["quote_items"].append(
                {"description": "", "quantity": 1, "unit_price": 0}
            )
            st.rerun()

        # Totals
        subtotal = sum(i["quantity"] * i["unit_price"] for i in st.session_state["quote_items"])
        vat_on = st.checkbox("부가세 (10%) 포함", value=True)
        vat = int(subtotal * 0.1) if vat_on else 0
        total = subtotal + vat

        tc1, tc2, tc3 = st.columns(3)
        tc1.metric("소계", f"{subtotal:,}원")
        tc2.metric("부가세", f"{vat:,}원")
        tc3.metric("합계", f"{total:,}원")

        # Save
        if st.button("견적서 저장", type="primary"):
            valid_items = [i for i in st.session_state["quote_items"] if i["description"] and i["unit_price"] > 0]
            if not valid_items:
                st.error("견적 항목을 1개 이상 추가해주세요.")
            else:
                qid = create_quote(
                    client_id=selected_client["id"],
                    title=title,
                    items=valid_items,
                    valid_until=valid_until,
                    notes=notes,
                )
                st.session_state["quote_items"] = []
                st.success(f"견적서 저장 완료 (ID: {qid})")
                st.rerun()

st.divider()

# ─── Quote List ────────────────────────────────────────────

st.subheader("견적서 목록")

qf1, qf2 = st.columns([1, 3])
with qf1:
    q_filter_options = {"전체": None, "초안": "draft", "발송": "sent", "수락": "accepted", "거절": "rejected", "만료": "expired"}
    q_status_filter = st.selectbox("상태", list(q_filter_options.keys()), key="q_filter")

q_status = q_filter_options[q_status_filter]
quotes = list_quotes(status=q_status)

STATUS_COLORS = {
    "draft": "blue", "sent": "orange", "accepted": "green",
    "rejected": "red", "expired": "gray",
}
STATUS_LABELS = {
    "draft": "초안", "sent": "발송", "accepted": "수락",
    "rejected": "거절", "expired": "만료",
}

if not quotes:
    st.info("견적서가 없습니다.")
else:
    for q in quotes:
        color = STATUS_COLORS.get(q["status"], "gray")
        label = STATUS_LABELS.get(q["status"], q["status"])

        with st.expander(
            f"**{q['quote_number']}** | {q['business_name']} | {q['title']} | "
            f":{color}-badge[{label}] | {q['total']:,}원"
        ):
            detail = get_quote(q["id"])
            if detail:
                st.markdown(f"**유효기간:** {detail.get('valid_until', '-')}")
                if detail.get("notes"):
                    st.markdown(f"**비고:** {detail['notes']}")

                # Items table
                st.markdown("##### 항목")
                for item in detail["items"]:
                    st.markdown(
                        f"- {item['description']} | {item['quantity']}개 | "
                        f"{item['unit_price']:,}원 | 소계 {item['quantity'] * item['unit_price']:,}원"
                    )
                st.markdown(f"**합계: {detail['total']:,}원**")

                # Actions
                ac1, ac2, ac3, ac4 = st.columns(4)
                with ac1:
                    if detail["status"] == "draft" and st.button("발송", key=f"send_{q['id']}"):
                        update_quote_status(q["id"], "sent")
                        st.rerun()
                with ac2:
                    if detail["status"] in ("draft", "sent") and st.button("수락", key=f"acc_{q['id']}"):
                        update_quote_status(q["id"], "accepted")
                        update_client(detail["client_id"], status="converted")
                        st.rerun()
                with ac3:
                    if detail["status"] in ("draft", "sent") and st.button("거절", key=f"rej_{q['id']}"):
                        update_quote_status(q["id"], "rejected")
                        st.rerun()
                with ac4:
                    if detail["status"] == "accepted":
                        from db import list_invoices as _li
                        existing_inv = [i for i in _li(client_id=detail["client_id"]) if i.get("quote_id") == q["id"]]
                        if existing_inv:
                            st.caption("청구서 생성 완료")
                        elif st.button("청구서 생성", key=f"inv_{q['id']}", type="primary"):
                            create_invoice_from_quote(q["id"])
                            st.success("청구서 생성 완료")
                            st.rerun()

                # PDF Download
                pdf_bytes = generate_quote_pdf(detail)
                if pdf_bytes:
                    st.download_button(
                        "PDF 다운로드",
                        data=pdf_bytes,
                        file_name=f"{detail['quote_number']}.pdf",
                        mime="application/pdf",
                        key=f"pdf_{q['id']}",
                    )
