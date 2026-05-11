"""
kakaotalk_channel/client.py
KakaoTalk Channel (카카오톡 채널) Business Message API client.

Auth: REST API key from Kakao Developers console.
     Also requires Channel ID and Channel Secret for some operations.

Kakao Talk Channel API sends messages through:
1. KakaoTalk Channel Message (채널 메시지) - requires user consent (opt-in)
2. Alimtalk (알림톡) - transactional, template-based, does not require opt-in
   For Alimtalk, a separate bizmessage API key is needed.

Docs:
    채널 메시지: https://developers.kakao.com/docs/latest/ko/message/message-template
    알림톡: https://business.kakao.com/info/bizmessage/

NOTE: This client covers the Alimtalk flow (most common for e-commerce automation).
REST API host: https://kakaoapi.aligo.in (Aligo reseller - most accessible for new businesses)
Official KakaoTalk Notification API: https://developers.kakao.com/docs/latest/ko/kakaotalk-channel
"""

import json
import time
import hmac
import hashlib
from typing import Optional
import urllib.request
import urllib.error
from urllib.parse import urlencode

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from src.unified import PlatformAdapter, Order, Customer, WebhookEvent


# Alimtalk message types
MSG_TYPE_ALIMTALK = "AT"
MSG_TYPE_FRIENDTALK = "FT"

# Rate limit: 500 messages per second (Kakao official limit for approved senders)
RATE_LIMIT_PER_SEC = 500


class KakaoTalkChannelClient:
    """
    KakaoTalk Alimtalk sender via Aligo reseller API.

    For direct Kakao Business API, register at:
    https://business.kakao.com/info/bizmessage/

    Required:
        api_key        - Aligo API key (or Kakao Bizmessage API key)
        user_id        - Aligo user ID
        sender_key     - Kakao Channel sender key (발신 프로파일 키)
        channel_id     - Kakao Channel ID (@channel_name)
    """

    platform_name = "kakaotalk_channel"
    BASE_URL = "https://kakaoapi.aligo.in"

    def __init__(
        self,
        api_key: str,
        user_id: str,
        sender_key: str,
        channel_id: str,
        _mock_transport=None,
    ):
        self.api_key = api_key
        self.user_id = user_id
        self.sender_key = sender_key
        self.channel_id = channel_id
        self._mock_transport = _mock_transport
        self._last_call_time: float = 0
        self._call_count_this_sec: int = 0

    # ------------------------------------------------------------------ #
    # Internal HTTP
    # ------------------------------------------------------------------ #

    def _post_form(self, path: str, body: dict) -> dict:
        url = f"{self.BASE_URL}{path}"
        body["apikey"] = self.api_key
        body["userid"] = self.user_id
        if self._mock_transport:
            return self._mock_transport("POST", url, body)
        data = urlencode(body).encode()
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    def _throttle(self):
        """Basic rate limit guard: max 500 calls/second."""
        now = time.time()
        if now - self._last_call_time >= 1.0:
            self._last_call_time = now
            self._call_count_this_sec = 0
        self._call_count_this_sec += 1
        if self._call_count_this_sec > RATE_LIMIT_PER_SEC:
            time.sleep(1.0 - (now - self._last_call_time))
            self._call_count_this_sec = 0

    # ------------------------------------------------------------------ #
    # Messaging
    # ------------------------------------------------------------------ #

    def send_alimtalk(
        self,
        receiver_phone: str,
        template_code: str,
        template_params: dict,
        receiver_name: str = "",
        msg: str = "",
    ) -> dict:
        """
        Send Alimtalk (알림톡) to a single recipient.

        Args:
            receiver_phone: Phone number in format 01012345678
            template_code:  Approved Alimtalk template code
            template_params: Dict of #{variable} replacements
            receiver_name:  Recipient name (for logging)
            msg:            Full message body (with #{variables} replaced)
        """
        self._throttle()
        body = {
            "senderkey": self.sender_key,
            "tpl_code": template_code,
            "sender": self.channel_id,
            "receiver_1": receiver_phone,
            "recvname_1": receiver_name,
            "subject_1": "알림",
            "message_1": msg or self._render_template(template_params),
        }
        return self._post_form("/akv10/alimtalk/send/", body)

    def send_alimtalk_bulk(
        self,
        recipients: list[dict],
        template_code: str,
    ) -> dict:
        """
        Send Alimtalk to multiple recipients.
        Each recipient: {"phone": str, "name": str, "msg": str}
        Max 1,000 per API call.
        """
        self._throttle()
        body = {
            "senderkey": self.sender_key,
            "tpl_code": template_code,
            "sender": self.channel_id,
        }
        for i, r in enumerate(recipients[:1000], start=1):
            body[f"receiver_{i}"] = r["phone"]
            body[f"recvname_{i}"] = r.get("name", "")
            body[f"subject_{i}"] = r.get("subject", "알림")
            body[f"message_{i}"] = r.get("msg", "")
        return self._post_form("/akv10/alimtalk/send/", body)

    def _render_template(self, params: dict) -> str:
        """Replace #{key} tokens with param values. Fallback if msg not pre-rendered."""
        result = ""
        for k, v in params.items():
            result = result.replace(f"#{{{k}}}", str(v))
        return result

    def get_send_history(self, date: str) -> dict:
        """
        Retrieve send history for a given date (YYYYMMDD).
        """
        body = {"date": date}
        return self._post_form("/akv10/alimtalk/history/", body)

    def list_templates(self) -> dict:
        """List registered Alimtalk templates."""
        return self._post_form("/akv10/alimtalk/template/", {})

    # ------------------------------------------------------------------ #
    # Rate limit test helper
    # ------------------------------------------------------------------ #

    def check_rate_limit(self) -> dict:
        """Return current rate limit state (for tests)."""
        return {
            "calls_this_second": self._call_count_this_sec,
            "limit_per_second": RATE_LIMIT_PER_SEC,
            "last_call_time": self._last_call_time,
        }
