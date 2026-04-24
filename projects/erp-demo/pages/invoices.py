"""Invoices Page — From-Quote + Payment Tracking + PDF"""

import streamlit as st
from db import (
    list_invoices, get_invoice, update_invoice_status, list_clients,
    create_invoice_manual, INVOICE_STATUSES,
)
from pdf_gen import generate_invoice_pdf

st.header("청구서")

# ─── Manual Invoice ────────────────────────────────────────

with st.expander("수동 청구서 생성", icon=":material/add_circle:"):
    clients = list_clients()
    if not clients:
        st.warning("먼저 고객을 등록해주세요.")
    else:
        client_options = {f"{c['business_name']} ({c['name']})": c for c in clients}
        sel = st.selectbox("고객 선택", list(client_options.keys()), key="inv_client")
        sel_client = client_options[sel]

        amount = st.number_input("청구 금액 (원)", min_value=0, step=10000, value=500000)
        due = st.date_input("납부 기한")

        if st.button("청구서 생성", type="primary"):
            if amount <= 0:
                st.error("금액을 입력해주세요.")
            else:
                create_invoice_manual(sel_client["id"], amount, due.strftime("%Y-%m-%d"))
                st.success("청구서 생성 완료")
                st.rerun()

st.divider()

# ─── Invoice List ──────────────────────────────────────────

st.subheader("청구서 목록")

if1, if2 = st.columns([1, 3])
with if1:
    inv_filter_options = {"전체": None, "미납": "unpaid", "완납": "paid", "연체": "overdue", "취소": "cancelled"}
    inv_filter = st.selectbox("상태", list(inv_filter_options.keys()), key="inv_filter")

inv_status = inv_filter_options[inv_filter]
invoices = list_invoices(status=inv_status)

STATUS_COLORS = {
    "unpaid": "orange", "paid": "green", "overdue": "red", "cancelled": "gray",
}
STATUS_LABELS = {
    "unpaid": "미납", "paid": "완납", "overdue": "연체", "cancelled": "취소",
}

# ─── Summary ───────────────────────────────────────────────

all_invoices = list_invoices()
total_invoiced = sum(i["total_amount"] for i in all_invoices)
total_paid = sum(i["total_amount"] for i in all_invoices if i["status"] == "paid")
outstanding = total_invoiced - total_paid

sc1, sc2, sc3 = st.columns(3)
sc1.metric("총 청구액", f"{total_invoiced:,}원")
sc2.metric("수금 완료", f"{total_paid:,}원")
sc3.metric("미수금", f"{outstanding:,}원")

st.divider()

if not invoices:
    st.info("청구서가 없습니다.")
else:
    for inv in invoices:
        color = STATUS_COLORS.get(inv["status"], "gray")
        label = STATUS_LABELS.get(inv["status"], inv["status"])

        with st.expander(
            f"**{inv['invoice_number']}** | {inv['business_name']} | "
            f":{color}-badge[{label}] | {inv['total_amount']:,}원 | 기한: {inv.get('due_date', '-')}"
        ):
            st.markdown(f"**발행일:** {inv['issued_at'][:10]}")
            st.markdown(f"**납부 기한:** {inv.get('due_date', '-')}")
            if inv.get("quote_number"):
                st.markdown(f"**연결 견적서:** {inv['quote_number']}")
            if inv.get("paid_at"):
                st.markdown(f"**수금일:** {inv['paid_at'][:10]}")

            # Actions
            ac1, ac2, ac3 = st.columns(3)
            with ac1:
                if inv["status"] == "unpaid":
                    if st.button("수금 완료", key=f"pay_{inv['id']}", type="primary"):
                        update_invoice_status(inv["id"], "paid")
                        st.rerun()
            with ac2:
                if inv["status"] == "unpaid":
                    if st.button("연체 처리", key=f"od_{inv['id']}"):
                        update_invoice_status(inv["id"], "overdue")
                        st.rerun()
            with ac3:
                if inv["status"] in ("unpaid", "overdue"):
                    if st.button("취소", key=f"can_{inv['id']}"):
                        update_invoice_status(inv["id"], "cancelled")
                        st.rerun()

            # PDF
            detail = get_invoice(inv["id"])
            if detail:
                pdf_bytes = generate_invoice_pdf(detail)
                if pdf_bytes:
                    st.download_button(
                        "PDF 다운로드",
                        data=pdf_bytes,
                        file_name=f"{detail['invoice_number']}.pdf",
                        mime="application/pdf",
                        key=f"ipdf_{inv['id']}",
                    )
