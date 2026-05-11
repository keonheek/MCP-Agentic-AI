"""
imweb/webhooks.py
Webhook event type constants and payload parsers for Imweb.

Imweb webhook events (as of 2026):
    order.create   - New order placed
    order.pay      - Payment confirmed
    order.cancel   - Order cancelled
    order.refund   - Refund completed
    member.create  - New member joined
    member.delete  - Member withdrawn
    prod.soldout   - Product sold out

Imweb sends POST to your hookUrl with JSON body.
Signature header: X-IMWEB-SIGNATURE
"""

from dataclasses import dataclass
from typing import Callable


# Event type constants
ORDER_CREATE = "order.create"
ORDER_PAY = "order.pay"
ORDER_CANCEL = "order.cancel"
ORDER_REFUND = "order.refund"
MEMBER_CREATE = "member.create"
MEMBER_DELETE = "member.delete"
PROD_SOLDOUT = "prod.soldout"

ALL_EVENTS = [
    ORDER_CREATE,
    ORDER_PAY,
    ORDER_CANCEL,
    ORDER_REFUND,
    MEMBER_CREATE,
    MEMBER_DELETE,
    PROD_SOLDOUT,
]

# Automation flow triggers
AUTOMATION_EVENTS = [ORDER_PAY, MEMBER_CREATE, PROD_SOLDOUT]


@dataclass
class ImwebWebhookPayload:
    event: str
    hook_seq: str
    site_code: str
    data: dict


def parse_imweb_payload(raw: dict) -> ImwebWebhookPayload:
    return ImwebWebhookPayload(
        event=raw.get("event", ""),
        hook_seq=str(raw.get("hookSeq", "")),
        site_code=raw.get("siteCode", ""),
        data=raw.get("data", {}),
    )


class ImwebWebhookRouter:
    """Simple event router for Imweb webhooks."""

    def __init__(self):
        self._handlers: dict[str, list[Callable]] = {}

    def on(self, event_type: str, handler: Callable[[ImwebWebhookPayload], None]):
        self._handlers.setdefault(event_type, []).append(handler)

    def dispatch(self, raw: dict):
        payload = parse_imweb_payload(raw)
        for handler in self._handlers.get(payload.event, []):
            handler(payload)
