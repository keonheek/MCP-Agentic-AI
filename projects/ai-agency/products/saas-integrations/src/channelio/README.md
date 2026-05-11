# Channel.io Integration

API: https://developers.channel.io/reference/overview
Base URL: https://api.channel.io/open

## Required Credentials

| Credential | Where to Get |
|---|---|
| Access Secret | Channel.io Settings > Developers > Channel Access Secret |
| Channel ID | Settings > Developers (or URL slug) |
| Webhook Token | Settings > Developers > Webhooks |

## Access Key Types

| Key | Permissions |
|---|---|
| Channel Access Secret | Full read/write (use server-side only) |
| Channel Access Key | Read-only (safe for logging/reporting scripts) |

Never expose Access Secret on client side or in frontend code.

## Webhook Setup

1. Go to Channel.io Settings > Developers > Webhooks.
2. Add your endpoint URL.
3. Select event types to receive.
4. Copy the signing token for signature verification.
5. Verify all incoming requests with X-SIGNATURE header.

## Key Webhook Event Types

| Event | Description |
|---|---|
| userChatCreated | New support conversation started |
| messageCreated | New message in any conversation |
| userChatClosed | Conversation closed/resolved |
| workflowButtonClicked | Bot workflow button clicked |

## Handoff Pattern for E-commerce

1. Customer contacts via Channel.io chat.
2. Bot handles FAQ (order status, shipping).
3. If issue unresolved: `assign_to_agent()` routes to human.
4. After resolution: `close_conversation()`.
5. CRM sync: `upsert_user()` keeps customer profile updated.

## Rate Limits

- 100 requests per second per channel
- No published daily limit

## Environment Variables

```
CHANNELIO_ACCESS_KEY=your_channel_access_secret
CHANNELIO_CHANNEL_ID=your_channel_id
CHANNELIO_WEBHOOK_TOKEN=your_webhook_signing_token
```
