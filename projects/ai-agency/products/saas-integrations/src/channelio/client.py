"""
channelio/client.py
Channel.io (채널톡) API client.

Auth: X-Access-Token header with Channel API Key.
     Different keys for different access levels:
     - Channel Access Secret: Full access (server-side only)
     - Channel Access Key:    Read-only

Channel.io REST API: https://developers.channel.io/reference/overview
Base URL: https://api.channel.io/open

Key use cases for e-commerce automation:
    - Create automated support tickets when orders have issues
    - Handoff to human agent when bot cannot resolve
    - Send proactive messages via push API
    - Retrieve conversation history for CRM sync
"""

import json
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


class ChannelIOClient:
    """
    Channel.io (채널톡) REST API client.

    Required:
        access_key    - Channel Access Key (read) or Access Secret (write)
        channel_id    - Channel.io channel ID
        webhook_token - For webhook signature verification
    """

    platform_name = "channelio"
    BASE_URL = "https://api.channel.io/open"

    def __init__(
        self,
        access_key: str,
        channel_id: str,
        webhook_token: str = "",
        _mock_transport=None,
    ):
        self.access_key = access_key
        self.channel_id = channel_id
        self.webhook_token = webhook_token
        self._mock_transport = _mock_transport

    # ------------------------------------------------------------------ #
    # Internal HTTP
    # ------------------------------------------------------------------ #

    def _headers(self) -> dict:
        return {
            "X-Access-Token": self.access_key,
            "Content-Type": "application/json",
        }

    def _get(self, path: str, params: dict = None) -> dict:
        url = f"{self.BASE_URL}{path}"
        if params:
            url = f"{url}?{urlencode(params)}"
        if self._mock_transport:
            return self._mock_transport("GET", url, None)
        req = urllib.request.Request(url, headers=self._headers())
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    def _post(self, path: str, body: dict) -> dict:
        url = f"{self.BASE_URL}{path}"
        data = json.dumps(body).encode()
        if self._mock_transport:
            return self._mock_transport("POST", url, body)
        req = urllib.request.Request(url, data=data, headers=self._headers(), method="POST")
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    def _put(self, path: str, body: dict) -> dict:
        url = f"{self.BASE_URL}{path}"
        data = json.dumps(body).encode()
        if self._mock_transport:
            return self._mock_transport("PUT", url, body)
        req = urllib.request.Request(url, data=data, headers=self._headers(), method="PUT")
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    # ------------------------------------------------------------------ #
    # Conversations
    # ------------------------------------------------------------------ #

    def list_conversations(
        self,
        state: str = "opened",
        limit: int = 50,
        since: Optional[str] = None,
    ) -> list[dict]:
        """
        List conversations (support chats).
        state: 'opened' | 'closed' | 'snoozed'
        """
        params = {"state": state, "limit": limit}
        if since:
            params["since"] = since
        resp = self._get(f"/channels/{self.channel_id}/user-chats", params)
        return resp.get("userChats", [])

    def get_conversation(self, chat_id: str) -> dict:
        resp = self._get(f"/open/user-chats/{chat_id}")
        return resp.get("userChat", resp)

    def close_conversation(self, chat_id: str) -> dict:
        """Mark conversation as resolved."""
        return self._put(f"/open/user-chats/{chat_id}/close", {})

    def open_conversation(self, chat_id: str) -> dict:
        """Re-open a closed conversation."""
        return self._put(f"/open/user-chats/{chat_id}/open", {})

    # ------------------------------------------------------------------ #
    # Messages
    # ------------------------------------------------------------------ #

    def send_message(
        self,
        chat_id: str,
        message: str,
        message_type: str = "text",
    ) -> dict:
        """
        Send a message to an existing conversation.
        message_type: 'text' | 'note' (internal note)
        """
        body = {
            "chatId": chat_id,
            "body": message,
            "type": message_type,
        }
        return self._post(f"/open/user-chats/{chat_id}/messages", body)

    def send_push(
        self,
        user_id: str,
        title: str,
        message: str,
        button_url: str = "",
    ) -> dict:
        """
        Send a proactive push message to a user (requires marketing opt-in).
        """
        body = {
            "userId": user_id,
            "message": {
                "title": title,
                "body": message,
            },
        }
        if button_url:
            body["message"]["buttonUrl"] = button_url
        return self._post(f"/channels/{self.channel_id}/push-messages", body)

    # ------------------------------------------------------------------ #
    # Handoff (human agent routing)
    # ------------------------------------------------------------------ #

    def assign_to_agent(self, chat_id: str, manager_id: str) -> dict:
        """Route conversation to a specific human agent."""
        body = {"managerId": manager_id}
        return self._put(f"/open/user-chats/{chat_id}/assign", body)

    def unassign(self, chat_id: str) -> dict:
        """Remove agent assignment (back to bot queue)."""
        return self._put(f"/open/user-chats/{chat_id}/unassign", {})

    # ------------------------------------------------------------------ #
    # Users (customers in Channel.io)
    # ------------------------------------------------------------------ #

    def get_user(self, user_id: str) -> dict:
        resp = self._get(f"/open/app-users/{user_id}")
        return resp.get("appUser", resp)

    def upsert_user(
        self,
        user_id: str,
        name: str = "",
        email: str = "",
        phone: str = "",
        profile: dict = None,
    ) -> dict:
        """Create or update a Channel.io user profile."""
        body = {
            "memberId": user_id,
            "name": name,
            "profile": profile or {},
        }
        if email:
            body["profile"]["email"] = email
        if phone:
            body["profile"]["mobileNumber"] = phone
        return self._put(f"/open/app-users/{user_id}", body)

    # ------------------------------------------------------------------ #
    # Webhooks
    # ------------------------------------------------------------------ #

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Channel.io signs with HMAC-SHA256 of payload using webhook_token.
        Header: X-SIGNATURE
        """
        expected = hmac.new(
            self.webhook_token.encode(), payload, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    def parse_webhook_event(self, raw_payload: dict) -> dict:
        """
        Channel.io webhook events arrive as:
        { "type": "userChatCreated" | "messageCreated" | ..., "entity": {...} }
        Returns normalized dict (not WebhookEvent, as Channel.io is not a store platform).
        """
        return {
            "event_type": raw_payload.get("type", "unknown"),
            "entity": raw_payload.get("entity", {}),
            "refers": raw_payload.get("refers", {}),
        }

    # ------------------------------------------------------------------ #
    # Health check
    # ------------------------------------------------------------------ #

    def health_check(self) -> dict:
        try:
            resp = self._get(f"/channels/{self.channel_id}")
            return {
                "platform": "channelio",
                "status": "ok" if "channel" in resp or resp else "error",
            }
        except Exception as e:
            return {"platform": "channelio", "status": "error", "detail": str(e)}
