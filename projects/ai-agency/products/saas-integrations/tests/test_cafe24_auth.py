"""
test_cafe24_auth.py
Tests for Cafe24 client auth and order/customer normalization.
All tests use mock transport -- no real API calls.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.cafe24.client import Cafe24Client
from src.unified import Order, Customer


# ------------------------------------------------------------------ #
# Mock transport
# ------------------------------------------------------------------ #

def make_mock(responses: dict):
    """
    responses: dict mapping (method, url_substring) -> response dict
    Longer URL keys take priority over shorter ones.
    """
    def transport(method, url, body):
        # Sort by url_key length descending so specific paths match first
        sorted_resp = sorted(responses.items(), key=lambda x: len(x[0][1]), reverse=True)
        for (m, url_key), resp in sorted_resp:
            if m == method and url_key in url:
                return resp
        raise ValueError(f"No mock for {method} {url}")
    return transport


MOCK_ME = {"mall": {"mall_id": "testmall", "mall_name": "Test Mall"}}

MOCK_TOKEN = {
    "access_token": "new_access_token_abc",
    "refresh_token": "new_refresh_token_xyz",
    "expires_in": 7200,
}

MOCK_ORDERS = {
    "orders": [
        {
            "order_id": "20260101-0001",
            "buyer": {
                "member_id": "member001",
                "name": "김건희",
                "email": "keonhee@test.com",
                "phone": "010-1234-5678",
            },
            "order_status": "paid",
            "order_price_amount": {"order_price": 45000},
            "items": [{"product_no": "P001", "product_name": "세럼 50ml", "quantity": 2}],
            "created_date": "2026-01-01T10:00:00+09:00",
        }
    ]
}

MOCK_SINGLE_ORDER = {
    "order": {
        "order_id": "20260101-0001",
        "buyer": {
            "member_id": "member001",
            "name": "김건희",
            "email": "keonhee@test.com",
            "phone": "010-1234-5678",
        },
        "order_status": "paid",
        "order_price_amount": {"order_price": 45000},
        "items": [],
        "created_date": "2026-01-01T10:00:00+09:00",
    }
}

MOCK_CUSTOMERS = {
    "customers": [
        {
            "member_id": "member001",
            "name": "김건희",
            "email": "keonhee@test.com",
            "phone": "010-1234-5678",
            "created_date": "2025-12-01T00:00:00+09:00",
            "use_count": 3,
            "total_order_amount": 120000,
        }
    ]
}

MOCK_WEBHOOK_SUBSCRIBE = {
    "webhook": {
        "no": "WH001",
        "event": "order_paid",
        "endpoint_url": "https://myserver.com/webhooks/cafe24",
    }
}

MOCK_WEBHOOK_LIST = {
    "webhooks": [
        {"no": "WH001", "event": "order_paid", "endpoint_url": "https://myserver.com/webhooks/cafe24"}
    ]
}


def _make_client():
    mock = make_mock({
        ("GET", "/me"): MOCK_ME,
        ("POST", "oauth/token"): MOCK_TOKEN,
        ("GET", "/orders"): MOCK_ORDERS,
        ("GET", "/orders/20260101-0001"): MOCK_SINGLE_ORDER,
        ("GET", "/customers"): MOCK_CUSTOMERS,
        ("POST", "/webhooks"): MOCK_WEBHOOK_SUBSCRIBE,
        ("GET", "/webhooks"): MOCK_WEBHOOK_LIST,
    })
    return Cafe24Client(
        mall_id="testmall",
        client_id="test_client_id",
        client_secret="test_secret",
        access_token="initial_token",
        refresh_token="initial_refresh",
        _mock_transport=mock,
    )


# ------------------------------------------------------------------ #
# Tests
# ------------------------------------------------------------------ #

def test_authenticate_returns_true():
    client = _make_client()
    assert client.authenticate() is True


def test_refresh_token_updates_access_token():
    client = _make_client()
    result = client.refresh_token()
    assert result is True
    assert client.access_token == "new_access_token_abc"
    assert client._refresh_token == "new_refresh_token_xyz"


def test_list_orders_returns_normalized():
    client = _make_client()
    orders = client.list_orders()
    assert len(orders) == 1
    o = orders[0]
    assert isinstance(o, Order)
    assert o.order_id == "20260101-0001"
    assert o.platform == "cafe24"
    assert o.customer_name == "김건희"
    assert o.total_price == 45000
    assert o.status == "paid"


def test_get_order_returns_normalized():
    client = _make_client()
    o = client.get_order("20260101-0001")
    assert isinstance(o, Order)
    assert o.order_id == "20260101-0001"
    assert o.customer_email == "keonhee@test.com"


def test_list_customers_returns_normalized():
    client = _make_client()
    customers = client.list_customers()
    assert len(customers) == 1
    c = customers[0]
    assert isinstance(c, Customer)
    assert c.customer_id == "member001"
    assert c.total_spent == 120000
    assert c.total_orders == 3


def test_subscribe_webhook():
    client = _make_client()
    result = client.subscribe_webhook("order_paid", "https://myserver.com/webhooks/cafe24")
    assert "webhook" in result


def test_list_webhook_subscriptions():
    client = _make_client()
    subs = client.list_webhook_subscriptions()
    assert len(subs) == 1
    assert subs[0]["event"] == "order_paid"


def test_verify_webhook_signature_valid():
    import hmac, hashlib
    secret = "test_secret"
    payload = b'{"event_type":"order_paid"}'
    sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    client = Cafe24Client(
        mall_id="testmall",
        client_id="id",
        client_secret=secret,
        access_token="tok",
    )
    assert client.verify_webhook_signature(payload, sig) is True


def test_verify_webhook_signature_invalid():
    client = Cafe24Client(
        mall_id="testmall",
        client_id="id",
        client_secret="test_secret",
        access_token="tok",
    )
    assert client.verify_webhook_signature(b"body", "bad_signature") is False


def test_parse_webhook_event():
    client = _make_client()
    raw = {
        "event_type": "order_paid",
        "event_no": "12345",
        "resource_id": "20260101-0001",
        "resource": {"order_id": "20260101-0001"},
    }
    event = client.parse_webhook_event(raw)
    assert event.platform == "cafe24"
    assert event.event_type == "order_paid"
    assert event.event_id == "12345"


if __name__ == "__main__":
    tests = [
        test_authenticate_returns_true,
        test_refresh_token_updates_access_token,
        test_list_orders_returns_normalized,
        test_get_order_returns_normalized,
        test_list_customers_returns_normalized,
        test_subscribe_webhook,
        test_list_webhook_subscriptions,
        test_verify_webhook_signature_valid,
        test_verify_webhook_signature_invalid,
        test_parse_webhook_event,
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
