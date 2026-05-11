"""
test_smartstore_orders.py
Tests for Naver Smart Store client -- auth, orders, notifications.
All tests use mock transport -- no real API calls.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import hmac
import hashlib
import base64
import time

from src.smartstore.client import SmartStoreClient
from src.smartstore.webhooks import (
    SmartStoreWebhookRouter,
    parse_smartstore_payload,
    PAYMENT_DONE,
    PURCHASE_DECIDED,
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


MOCK_TOKEN = {
    "access_token": "mock_naver_token",
    "token_type": "Bearer",
    "expires_in": 1800,
}

MOCK_ORDERS = {
    "data": {
        "contents": [
            {
                "productOrderId": "2026011500001",
                "productOrderStatus": "PAYMENT_DONE",
                "productId": "NAV-P001",
                "productName": "수분 크림 50g",
                "quantity": 1,
                "unitPrice": 29000,
                "totalPaymentAmount": 29000,
                "paymentDate": "2026-01-15T10:00:00+09:00",
                "order": {
                    "ordererId": "NAVER_USER_001",
                    "ordererName": "박민준",
                    "ordererEmail": "minjun@test.com",
                    "ordererTel": "010-7777-6666",
                },
            }
        ]
    }
}

MOCK_SINGLE_ORDER = {
    "data": {
        "productOrderId": "2026011500001",
        "productOrderStatus": "PAYMENT_DONE",
        "totalPaymentAmount": 29000,
        "paymentDate": "2026-01-15T10:00:00+09:00",
        "order": {
            "ordererId": "NAVER_USER_001",
            "ordererName": "박민준",
            "ordererEmail": "minjun@test.com",
            "ordererTel": "010-7777-6666",
        },
    }
}

MOCK_NOTIFICATION_REGISTER = {"data": {"notificationId": "NOTI001"}}
MOCK_NOTIFICATION_LIST = {
    "data": [{"notificationId": "NOTI001", "notificationStatus": "PAYMENT_DONE"}]
}


def _make_client():
    mock = make_mock({
        ("POST", "oauth2/token"): MOCK_TOKEN,
        ("POST", "pay-order/seller/product-orders/query"): MOCK_ORDERS,
        ("GET", "pay-order/seller/product-orders/2026011500001"): MOCK_SINGLE_ORDER,
        ("POST", "notification/register"): MOCK_NOTIFICATION_REGISTER,
        ("GET", "notification/list"): MOCK_NOTIFICATION_LIST,
    })
    return SmartStoreClient(
        application_id="test_app_id",
        application_secret="test_app_secret",
        access_token="pre_set_token",
        _mock_transport=mock,
    )


# ------------------------------------------------------------------ #
# Tests
# ------------------------------------------------------------------ #

def test_authenticate_returns_true():
    client = _make_client()
    client.access_token = ""
    result = client.authenticate()
    assert result is True
    assert client.access_token == "mock_naver_token"


def test_signature_generation():
    """Smart Store signature = Base64(HMAC-SHA256(app_id_timestamp, secret))."""
    client = SmartStoreClient("myappid", "mysecret")
    timestamp = 1700000000000
    sig = client._generate_signature(timestamp)
    expected_msg = f"myappid_{timestamp}".encode()
    expected_sig = base64.b64encode(
        hmac.new("mysecret".encode(), expected_msg, hashlib.sha256).digest()
    ).decode()
    assert sig == expected_sig


def test_list_orders_normalized():
    client = _make_client()
    # Pre-set token so auth skipped
    client._token_expires_at = time.time() + 3600
    orders = client.list_orders()
    assert len(orders) == 1
    o = orders[0]
    assert isinstance(o, Order)
    assert o.order_id == "2026011500001"
    assert o.platform == "smartstore"
    assert o.customer_name == "박민준"
    assert o.total_price == 29000
    assert o.status == "PAYMENT_DONE"


def test_get_order_normalized():
    client = _make_client()
    client._token_expires_at = time.time() + 3600
    o = client.get_order("2026011500001")
    assert isinstance(o, Order)
    assert o.customer_email == "minjun@test.com"


def test_list_customers_from_orders():
    """Smart Store derives customers from orders (no direct endpoint)."""
    client = _make_client()
    client._token_expires_at = time.time() + 3600
    customers = client.list_customers()
    assert len(customers) == 1
    c = customers[0]
    assert isinstance(c, Customer)
    assert c.customer_id == "NAVER_USER_001"
    assert c.platform == "smartstore"


def test_subscribe_webhook():
    client = _make_client()
    client._token_expires_at = time.time() + 3600
    result = client.subscribe_webhook("PAYMENT_DONE", "https://myserver.com/webhooks/naver")
    assert "data" in result


def test_list_webhook_subscriptions():
    client = _make_client()
    client._token_expires_at = time.time() + 3600
    subs = client.list_webhook_subscriptions()
    assert len(subs) == 1
    assert subs[0]["notificationStatus"] == "PAYMENT_DONE"


def test_verify_webhook_signature_valid():
    secret = "test_app_secret"
    payload = b'{"notificationStatus":"PAYMENT_DONE"}'
    sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    client = SmartStoreClient("id", secret, access_token="tok")
    assert client.verify_webhook_signature(payload, sig) is True


def test_verify_webhook_signature_invalid():
    client = SmartStoreClient("id", "test_app_secret", access_token="tok")
    assert client.verify_webhook_signature(b"body", "wrong") is False


def test_parse_webhook_event():
    client = _make_client()
    raw = {
        "notificationStatus": "PAYMENT_DONE",
        "notificationId": "NOTI001",
        "productOrderId": "2026011500001",
        "data": {},
    }
    event = client.parse_webhook_event(raw)
    assert event.platform == "smartstore"
    assert event.event_type == "PAYMENT_DONE"
    assert event.event_id == "NOTI001"


def test_webhook_router_dispatches():
    router = SmartStoreWebhookRouter()
    received = []
    router.on(PAYMENT_DONE, lambda p: received.append(p.notification_status))
    router.dispatch({
        "notificationStatus": "PAYMENT_DONE",
        "notificationId": "1",
        "productOrderId": "ORD001",
        "data": {},
    })
    assert received == ["PAYMENT_DONE"]


if __name__ == "__main__":
    tests = [
        test_authenticate_returns_true,
        test_signature_generation,
        test_list_orders_normalized,
        test_get_order_normalized,
        test_list_customers_from_orders,
        test_subscribe_webhook,
        test_list_webhook_subscriptions,
        test_verify_webhook_signature_valid,
        test_verify_webhook_signature_invalid,
        test_parse_webhook_event,
        test_webhook_router_dispatches,
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
