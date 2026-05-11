"""
test_kakao_rate_limit.py
Tests for KakaoTalk Channel client -- messaging, bulk send, rate limit guard.
All tests use mock transport -- no real API calls.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import time

from src.kakaotalk_channel.client import KakaoTalkChannelClient, RATE_LIMIT_PER_SEC


def make_mock(responses: dict):
    def transport(method, url, body):
        for (m, url_key), resp in responses.items():
            if m == method and url_key in url:
                return resp
        raise ValueError(f"No mock for {method} {url}")
    return transport


MOCK_SEND_SUCCESS = {
    "result_code": 1,
    "message": "success",
    "msg_id": "MSG001",
}

MOCK_TEMPLATES = {
    "result_code": 1,
    "templates": [
        {"tpl_code": "ORDER_PAID_01", "tpl_name": "주문 완료 알림", "status": "A"},
        {"tpl_code": "SHIP_NOTICE_01", "tpl_name": "배송 시작 알림", "status": "A"},
    ],
}

MOCK_HISTORY = {
    "result_code": 1,
    "list": [
        {"msg_id": "MSG001", "receiver": "01012345678", "result_code": 1}
    ],
}


def _make_client():
    mock = make_mock({
        ("POST", "alimtalk/send"): MOCK_SEND_SUCCESS,
        ("POST", "alimtalk/template"): MOCK_TEMPLATES,
        ("POST", "alimtalk/history"): MOCK_HISTORY,
    })
    return KakaoTalkChannelClient(
        api_key="test_api_key",
        user_id="test_user",
        sender_key="test_sender_key",
        channel_id="@testchannel",
        _mock_transport=mock,
    )


# ------------------------------------------------------------------ #
# Tests
# ------------------------------------------------------------------ #

def test_send_alimtalk_success():
    client = _make_client()
    result = client.send_alimtalk(
        receiver_phone="01012345678",
        template_code="ORDER_PAID_01",
        template_params={"name": "김건희", "order_id": "ORD001", "amount": "45000"},
        receiver_name="김건희",
        msg="안녕하세요 김건희님, 주문이 확인되었습니다. 주문번호: ORD001",
    )
    assert result.get("result_code") == 1


def test_send_alimtalk_bulk_success():
    client = _make_client()
    recipients = [
        {"phone": "01011112222", "name": "이수진", "msg": "안녕하세요 이수진님, 배송이 시작되었습니다."},
        {"phone": "01033334444", "name": "박민준", "msg": "안녕하세요 박민준님, 배송이 시작되었습니다."},
    ]
    result = client.send_alimtalk_bulk(recipients, template_code="SHIP_NOTICE_01")
    assert result.get("result_code") == 1


def test_list_templates():
    client = _make_client()
    result = client.list_templates()
    assert result.get("result_code") == 1
    assert len(result.get("templates", [])) == 2
    assert result["templates"][0]["tpl_code"] == "ORDER_PAID_01"


def test_get_send_history():
    client = _make_client()
    result = client.get_send_history("20260201")
    assert result.get("result_code") == 1
    assert len(result.get("list", [])) == 1


def test_bulk_send_caps_at_1000():
    """Bulk send must not send more than 1000 per call."""
    call_log = []

    def transport(method, url, body):
        # Count how many receiver_N keys are in the body
        count = sum(1 for k in body if k.startswith("receiver_"))
        call_log.append(count)
        return MOCK_SEND_SUCCESS

    client = KakaoTalkChannelClient(
        api_key="k", user_id="u", sender_key="s", channel_id="@c",
        _mock_transport=transport,
    )
    recipients = [{"phone": f"0100000{i:04d}", "name": f"User{i}", "msg": "Test"} for i in range(1200)]
    client.send_alimtalk_bulk(recipients, "TPL001")
    # Should have capped at 1000
    assert call_log[0] == 1000


def test_rate_limit_state_initial():
    client = _make_client()
    state = client.check_rate_limit()
    assert state["limit_per_second"] == RATE_LIMIT_PER_SEC
    assert state["calls_this_second"] == 0


def test_rate_limit_increments_on_send():
    client = _make_client()
    client.send_alimtalk(
        receiver_phone="01012345678",
        template_code="ORDER_PAID_01",
        template_params={},
        msg="test",
    )
    state = client.check_rate_limit()
    assert state["calls_this_second"] == 1


def test_api_key_injected_in_request():
    """API key must be included in every POST body."""
    captured_bodies = []

    def transport(method, url, body):
        captured_bodies.append(body)
        return MOCK_SEND_SUCCESS

    client = KakaoTalkChannelClient(
        api_key="MY_API_KEY", user_id="MY_USER", sender_key="SK", channel_id="@ch",
        _mock_transport=transport,
    )
    client.send_alimtalk("01099998888", "TPL", {}, msg="hi")
    assert captured_bodies[0].get("apikey") == "MY_API_KEY"
    assert captured_bodies[0].get("userid") == "MY_USER"


if __name__ == "__main__":
    tests = [
        test_send_alimtalk_success,
        test_send_alimtalk_bulk_success,
        test_list_templates,
        test_get_send_history,
        test_bulk_send_caps_at_1000,
        test_rate_limit_state_initial,
        test_rate_limit_increments_on_send,
        test_api_key_injected_in_request,
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
