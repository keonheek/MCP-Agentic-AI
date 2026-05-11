"""
Hagwon tuition auto-billing engine.
Wraps Toss Payments billing key API.
"""
import os
import requests
from datetime import datetime

TOSS_SECRET_KEY = os.environ.get("TOSS_SECRET_KEY", "")
TOSS_BILLING_BASE = "https://api.tosspayments.com/v1/billing"

import base64

def _auth_header() -> dict:
    encoded = base64.b64encode(f"{TOSS_SECRET_KEY}:".encode()).decode()
    return {"Authorization": f"Basic {encoded}", "Content-Type": "application/json"}


def charge_billing_key(billing_key: str, amount: int, order_id: str, customer_name: str) -> dict:
    """
    Charge a saved billing key (recurring payment).
    Returns Toss API response dict.
    """
    if not TOSS_SECRET_KEY:
        # Dry-run mode for demo
        return {
            "status": "dry_run",
            "orderId": order_id,
            "amount": amount,
            "customerName": customer_name,
        }

    resp = requests.post(
        f"{TOSS_BILLING_BASE}/{billing_key}",
        json={
            "customerKey": order_id,
            "amount": amount,
            "orderId": order_id,
            "orderName": f"{customer_name} 수강료",
        },
        headers=_auth_header(),
        timeout=15,
    )
    return resp.json()


def cancel_payment(payment_key: str, reason: str = "이중 결제") -> dict:
    """Cancel a payment (for double-charge recovery)."""
    if not TOSS_SECRET_KEY:
        return {"status": "dry_run_cancel"}

    resp = requests.post(
        f"https://api.tosspayments.com/v1/payments/{payment_key}/cancel",
        json={"cancelReason": reason},
        headers=_auth_header(),
        timeout=15,
    )
    return resp.json()
