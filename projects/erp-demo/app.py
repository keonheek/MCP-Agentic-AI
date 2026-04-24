"""
GEO Agency ERP Demo — Quote Tracker + Client Log + AI Automations
Streamlit multi-page app with SQLite backend.
"""

import streamlit as st

st.set_page_config(
    page_title="GEO Agency ERP",
    page_icon=":material/dashboard:",
    layout="wide",
    initial_sidebar_state="expanded",
)

from db import init_db, DB_PATH


@st.cache_resource
def _init_once():
    """Initialize DB + seed exactly once across all Streamlit reruns."""
    init_db()
    from db import total_clients
    if total_clients() == 0:
        from seed import seed_all
        seed_all()
    return True


_init_once()

# ─── Navigation ────────────────────────────────────────────

dashboard = st.Page("pages/dashboard.py", title="대시보드", icon=":material/dashboard:", default=True)
clients = st.Page("pages/clients.py", title="고객 관리", icon=":material/people:")
quotes = st.Page("pages/quotes.py", title="견적서", icon=":material/request_quote:")
invoices = st.Page("pages/invoices.py", title="청구서", icon=":material/receipt_long:")
automations = st.Page("pages/automations.py", title="AI 자동화", icon=":material/smart_toy:")

nav = st.navigation([dashboard, clients, quotes, invoices, automations])

# ─── Sidebar Branding ──────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0;">
        <h2 style="margin:0; color:#00C7BE;">GEO Agency</h2>
        <p style="margin:0; color:#94A3B8; font-size:0.85rem;">ERP Demo | Quote Tracker + Client Log</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # Quick stats in sidebar
    from db import total_clients, open_quotes_value, monthly_revenue, conversion_rate as _cr
    c1, c2 = st.columns(2)
    with c1:
        st.metric("고객", total_clients())
        st.metric("전환율", f"{_cr()}%")
    with c2:
        oq = open_quotes_value()
        mr = monthly_revenue()
        st.metric("미결 견적", f"{oq:,}원")
        st.metric("월 매출", f"{mr:,}원")

nav.run()
