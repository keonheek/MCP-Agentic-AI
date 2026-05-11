"""
test_imweb_webhooks.py
Tests for Imweb client auth, orders, customers, and webhook operations.
All tests use mock transport -- no real API calls.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import hmac
import hashlib

from src.imweb.client import ImwebClient
from src.imweb.webhooks import (
    ImwebWebhookRouter,
    parse_imweb_payload,
    ORDER_PAY,
    MEMBER_CREATE,
)
from src.unified import Order, Customer


def make_mock(responses: dict):
    def transport(method, url, body):
        sorted_resp = sorted(responses.items(), key=lambda x: len(x[0][1]), reverse=True)
        for (m, url_key), resp in sorted_resp:
            if m == method and url_key in url:
                return resp
        raise ValueError(f"No mock for {method} {url}")
    return transport


MOCK_AUTH_RESP = {
    "code": 200,
    "data": {"access_token": "mock_imweb_token_abc"},
}

MOCK_ORDERS = {
    "code": 200,
    "data": {
        "list": [
            {
                "orderCode": "IW-2026-001",
                "memberCode": "MEM001",
                "memberInfo": {"name": "이수진", "email": "sujin@test.com"},
                "orderPhone": "010-9999-8888",
                "orderStatus": "pay_done",
                "payPrice": 38000,
                "prodList": [{"prodCode": "P001", "prodName": "토너 200ml"}],
                "addTime": "2026-01-15T09:30:00",
            }
        ]
    },
}

MOCK_SINGLE_ORDER = {
    "code": 200,
    "data": {
        "orderCode": "IW-2026-001",
        "memberCode": "MEM001",
        "memberInfo": {"name": "이수진", "email": "sujin@test.com"},
        "orderPhone": "010-9999-8888",
        "orderStatus": "pay_done",
        "payPrice": 38000,
        "prodList": [],
        "addTime": "2026-01-15T09:30:00",
    },
}

MOCK_CUSTOMERS = {
    "code": 200,
    "data": {
        "list": [
            {
                "memberCode": "MEM001",
                "name": "이수진",
                "email": "sujin@test.com",
                "phone": "010-9999-8888",
                "addTime": "2025-11-01T00:00:00",
                "orderCount": 5,
                "orderAmount": 190000,
            }
        ]
    },
}

MOCK_WEBHOOK_SUBSCRIBE = {"code": 200, "data": {"hookSeq": "H001"}}
MOCK_WEBHOOK_LIST = {
    "code": 200,
    "data": {"list": [{"hookSeq": "H001", "event": "order.pay", "hookUrl": "https://test.com/hook"}]},
}


def _make_client():
    mock = make_mock({
        ("POST", "auth/token"): MOCK_AUTH_RESP,
        ("GET", "shop/orders"): MOCK_ORDERS,
        ("GET", "shop/orders/IW-2026-001"): MOCK_SINGLE_ORDER,
        ("GET", "member/members"): MOCK_CUSTOMERS,
        ("POST", "api/hook"): MOCK_WEBHOOK_SUBSCRIBE,
        ("GET", "api/hook"): MOCK_WEBHOOK_LIST,
    })
    return ImwebClient(
        api_key="test_key",
        api_secret="test_secret",
        access_token="pre_set_token",
        _mock_transport=mock,
    )


# ------------------------------------------------------------------ #
# Tests
# ------------------------------------------------------------------ #

def test_authenticate_returns_true():
    client = _make_client()
    client.access_token = ""  # force re-auth
    result = client.authenticate()
    assert result is True
    assert client.access_token == "mock_imweb_token_abc"


def test_list_orders_normalized():
    client = _make_client()
    orders = client.list_orders()
    assert len(orders) == 1
    o = orders[0]
    assert isinstance(o, Order)
    assert o.order_id == "IW-2026-001"
    assert o.platform == "imweb"
    assert o.customer_name == "이수진"
    assert o.total_price == 38000
    assert o.status == "pay_done"


def test_get_order_normalized():
    client = _make_client()
    o = client.get_order("IW-2026-001")
    assert isinstance(o, Order)
    assert o.customer_email == "sujin@test.com"


def test_list_customers_normalized():
    client = _make_client()
    customers = client.list_customers()
    assert len(customers) == 1
    c = customers[0]
    assert isinstance(c, Customer)
    assert c.customer_id == "MEM001"
    assert c.total_orders == 5
    assert c.total_spent == 190000


def test_subscribe_webhook():
    client = _make_client()
    result = client.subscribe_webhook("order.pay", "https://test.com/hook")
    assert result.get("code") == 200


def test_list_webhook_subscriptions():
    client = _make_client()
    subs = client.list_webhook_subscriptions()
    assert len(subs) == 1
    assert subs[0]["event"] == "order.pay"


def test_verify_webhook_signature_valid():
    secret = "test_secret"
    payload = b'{"event":"order.pay"}'
    sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    client = ImwebClient(api_key="k", api_secret=secret, access_token="t")
    assert client.verify_webhook_signature(payload, sig) is True


def test_verify_webhook_signature_invalid():
    client = ImwebClient(api_key="k", api_secret="test_secret", access_token="t")
    assert client.verify_webhook_signature(b"body", "wrong") is False


def test_parse_webhook_event():
    client = _make_client()
    raw = {
        "event": "order.pay",
        "hookSeq": "H001",
        "siteCode": "SITE001",
        "data": {"orderCode": "IW-2026-001"},
    }
    event = client.parse_webhook_event(raw)
    assert event.platform == "imweb"
    assert event.event_type == "order.pay"
    assert event.event_id == "H001"


def test_webhook_router_dispatches():
    router = ImwebWebhookRouter()
    received = []
    router.on(ORDER_PAY, lambda p: received.append(p.event))
    router.dispatch({"event": "order.pay", "hookSeq": "1", "siteCode": "S", "data": {}})
    assert received == ["order.pay"]


def test_webhook_router_ignores_unregistered():
    router = ImwebWebhookRouter()
    received = []
    router.on(MEMBER_CREATE, lambda p: received.append(p))
    router.dispatch({"event": "order.pay", "hookSeq": "1", "siteCode": "S", "data": {}})
    assert received == []


if __name__ == "__main__":
    tests = [
        test_authenticate_returns_true,
        test_list_orders_normalized,
        test_get_order_normalized,
        test_list_customers_normalized,
        test_subscribe_webhook,
        test_list_webhook_subscriptions,
        test_verify_webhook_signature_valid,
        test_verify_webhook_signature_invalid,
        test_parse_webhook_event,
        test_webhook_router_dispatches,
        test_webhook_router_ignores_unregistered,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed}/{passed+failed} passed")
