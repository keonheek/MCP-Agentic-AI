"""
test_channelio_handoff.py
Tests for Channel.io client -- conversations, messages, handoff, webhook sig.
All tests use mock transport -- no real API calls.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import hmac
import hashlib

from src.channelio.client import ChannelIOClient


def make_mock(responses: dict):
    def transport(method, url, body):
        sorted_resp = sorted(responses.items(), key=lambda x: len(x[0][1]), reverse=True)
        for (m, url_key), resp in sorted_resp:
            if m == method and url_key in url:
                return resp
        raise ValueError(f"No mock for {method} {url}")
    return transport


MOCK_CONVERSATIONS = {
    "userChats": [
        {
            "id": "chat001",
            "state": "opened",
            "assignee": None,
            "createdAt": 1706745600000,
            "user": {"id": "user001", "name": "테스트고객"},
        }
    ]
}

MOCK_SINGLE_CONV = {
    "userChat": {
        "id": "chat001",
        "state": "opened",
        "createdAt": 1706745600000,
    }
}

MOCK_CLOSE_CONV = {"userChat": {"id": "chat001", "state": "closed"}}
MOCK_OPEN_CONV = {"userChat": {"id": "chat001", "state": "opened"}}

MOCK_SEND_MESSAGE = {
    "message": {
        "id": "msg001",
        "chatId": "chat001",
        "body": "주문 상태를 확인해드리겠습니다.",
        "type": "text",
    }
}

MOCK_ASSIGN = {"userChat": {"id": "chat001", "assigneeId": "agent001"}}
MOCK_UNASSIGN = {"userChat": {"id": "chat001", "assigneeId": None}}

MOCK_USER = {
    "appUser": {
        "id": "user001",
        "name": "테스트고객",
        "profile": {"email": "testcustomer@test.com", "mobileNumber": "010-5555-6666"},
    }
}

MOCK_UPSERT_USER = {"appUser": {"id": "user001", "name": "업데이트고객"}}

MOCK_CHANNEL = {"channel": {"id": "CH001", "name": "스킨케어몰 채널"}}

MOCK_PUSH = {"pushMessage": {"id": "push001"}}


def _make_client():
    mock = make_mock({
        ("GET", "channels/CH001/user-chats"): MOCK_CONVERSATIONS,
        ("GET", "user-chats/chat001"): MOCK_SINGLE_CONV,
        ("PUT", "user-chats/chat001/close"): MOCK_CLOSE_CONV,
        ("PUT", "user-chats/chat001/open"): MOCK_OPEN_CONV,
        ("POST", "user-chats/chat001/messages"): MOCK_SEND_MESSAGE,
        ("PUT", "user-chats/chat001/assign"): MOCK_ASSIGN,
        ("PUT", "user-chats/chat001/unassign"): MOCK_UNASSIGN,
        ("GET", "app-users/user001"): MOCK_USER,
        ("PUT", "app-users/user001"): MOCK_UPSERT_USER,
        ("GET", "channels/CH001"): MOCK_CHANNEL,
        ("POST", "channels/CH001/push-messages"): MOCK_PUSH,
    })
    return ChannelIOClient(
        access_key="test_access_key",
        channel_id="CH001",
        webhook_token="test_webhook_token",
        _mock_transport=mock,
    )


# ------------------------------------------------------------------ #
# Tests
# ------------------------------------------------------------------ #

def test_list_conversations():
    client = _make_client()
    convs = client.list_conversations()
    assert len(convs) == 1
    assert convs[0]["id"] == "chat001"


def test_get_conversation():
    client = _make_client()
    conv = client.get_conversation("chat001")
    assert conv["id"] == "chat001"


def test_close_conversation():
    client = _make_client()
    result = client.close_conversation("chat001")
    assert result.get("userChat", {}).get("state") == "closed"


def test_open_conversation():
    client = _make_client()
    result = client.open_conversation("chat001")
    assert result.get("userChat", {}).get("state") == "opened"


def test_send_message():
    client = _make_client()
    result = client.send_message("chat001", "주문 상태를 확인해드리겠습니다.")
    assert result.get("message", {}).get("id") == "msg001"


def test_assign_to_agent():
    client = _make_client()
    result = client.assign_to_agent("chat001", "agent001")
    assert result.get("userChat", {}).get("assigneeId") == "agent001"


def test_unassign():
    client = _make_client()
    result = client.unassign("chat001")
    assert result.get("userChat", {}).get("assigneeId") is None


def test_get_user():
    client = _make_client()
    user = client.get_user("user001")
    assert user["id"] == "user001"
    assert user["profile"]["email"] == "testcustomer@test.com"


def test_upsert_user():
    client = _make_client()
    result = client.upsert_user(
        "user001",
        name="업데이트고객",
        email="updated@test.com",
        phone="010-1111-2222",
    )
    assert result.get("appUser", {}).get("id") == "user001"


def test_health_check_ok():
    client = _make_client()
    result = client.health_check()
    assert result["status"] == "ok"
    assert result["platform"] == "channelio"


def test_verify_webhook_signature_valid():
    token = "test_webhook_token"
    payload = b'{"type":"userChatCreated","entity":{}}'
    sig = hmac.new(token.encode(), payload, hashlib.sha256).hexdigest()
    client = ChannelIOClient("key", "CH001", webhook_token=token)
    assert client.verify_webhook_signature(payload, sig) is True


def test_verify_webhook_signature_invalid():
    client = ChannelIOClient("key", "CH001", webhook_token="token")
    assert client.verify_webhook_signature(b"body", "bad") is False


def test_parse_webhook_event():
    client = _make_client()
    raw = {
        "type": "userChatCreated",
        "entity": {"id": "chat001"},
        "refers": {},
    }
    result = client.parse_webhook_event(raw)
    assert result["event_type"] == "userChatCreated"
    assert result["entity"]["id"] == "chat001"


def test_send_push():
    client = _make_client()
    result = client.send_push(
        user_id="user001",
        title="배송 알림",
        message="주문하신 상품이 배송 시작되었습니다.",
    )
    assert result.get("pushMessage", {}).get("id") == "push001"


if __name__ == "__main__":
    tests = [
        test_list_conversations,
        test_get_conversation,
        test_close_conversation,
        test_open_conversation,
        test_send_message,
        test_assign_to_agent,
        test_unassign,
        test_get_user,
        test_upsert_user,
        test_health_check_ok,
        test_verify_webhook_signature_valid,
        test_verify_webhook_signature_invalid,
        test_parse_webhook_event,
        test_send_push,
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
