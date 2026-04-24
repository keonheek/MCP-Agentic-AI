"""
SME AI Platform — Reflex app entry point.

Run with: reflex run
"""
import reflex as rx
from frontend.pages.home import home
from frontend.pages.geo_audit import geo_audit_page

app = rx.App(
    theme=rx.theme(
        appearance="light",
        accent_color="teal",
    )
)

app.add_page(home, route="/")
app.add_page(geo_audit_page, route="/audit")
