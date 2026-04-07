"""
app_optimized.py — THIS IS THE FILE THE AGENT EDITS.

Baseline: same imports as app.py, restructured for importability (no st.set_page_config at module level).
The agent's goal: reduce import time measured by benchmark.py.

Techniques to try:
- Lazy imports (import inside functions)
- Removing unused imports
- __all__ to limit what gets imported
- Restructuring so heavy imports are deferred
"""

# ── Lazy imports — streamlit deferred until functions are called ──

def setup_page():
    import streamlit as st
    st.set_page_config(
        page_title="GEO Agency ERP",
        page_icon=":material/dashboard:",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def _init_once():
    import streamlit as st
    from db import init_db, total_clients

    @st.cache_resource
    def _inner():
        init_db()
        if total_clients() == 0:
            from seed import seed_all
            seed_all()
        return True
    return _inner()


def build_sidebar():
    import streamlit as st
    from db import total_clients, open_quotes_value, monthly_revenue, conversion_rate
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 1rem 0;">
            <h2 style="margin:0; color:#00C7BE;">GEO Agency</h2>
            <p style="margin:0; color:#94A3B8; font-size:0.85rem;">ERP Demo | Quote Tracker + Client Log</p>
        </div>
        """, unsafe_allow_html=True)
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.metric("고객", total_clients())
            st.metric("전환율", f"{conversion_rate()}%")
        with c2:
            st.metric("미결 견적", f"{open_quotes_value():,}원")
            st.metric("월 매출", f"{monthly_revenue():,}원")


def build_nav():
    import streamlit as st
    dashboard = st.Page("pages/dashboard.py", title="대시보드", icon=":material/dashboard:", default=True)
    clients = st.Page("pages/clients.py", title="고객 관리", icon=":material/people:")
    quotes = st.Page("pages/quotes.py", title="견적서", icon=":material/request_quote:")
    invoices = st.Page("pages/invoices.py", title="청구서", icon=":material/receipt_long:")
    automations = st.Page("pages/automations.py", title="AI 자동화", icon=":material/smart_toy:")
    return st.navigation([dashboard, clients, quotes, invoices, automations])


def main():
    setup_page()
    _init_once()
    build_sidebar()
    nav = build_nav()
    nav.run()


if __name__ == "__main__":
    main()
