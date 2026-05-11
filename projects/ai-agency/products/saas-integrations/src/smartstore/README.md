# Smart Store / Naver Commerce Integration

API: https://apicenter.commerce.naver.com
Docs: https://apicenter.commerce.naver.com/ko/basic/commerce-API-guide

## Required Credentials

| Credential | Where to Get |
|---|---|
| Application ID | Naver Developer Center > My Apps > Commerce API |
| Application Secret | Same page |

Apply at: https://developer.naver.com (Commerce API requires seller account + business registration)

## Auth Flow

Signature-based client credentials (no user redirect needed for seller APIs):

1. Generate timestamp (milliseconds).
2. Build message: `{application_id}_{timestamp}`.
3. HMAC-SHA256 sign with application_secret, Base64-encode.
4. POST to `/v1/oauth2/token` with `grant_type=client_credentials`.
5. Token valid for 30 minutes. `SmartStoreClient._ensure_token()` auto-refreshes.

## Notification (Webhook) Setup

1. Register endpoint via `subscribe_webhook()` or in seller center.
2. Naver calls your `notificationUrl` for each status change.
3. Verify with `X-Naver-Signature` header.

## Important Limitation

Smart Store does NOT have a standalone customer list endpoint. Customer data is extracted from order records only.

## Required API Permissions

- Commerce API: Order inquiry, Product order inquiry
- Notification registration

## Rate Limits

- 10 requests per second (order query)
- 1 request per second (notification registration)
- Daily limits apply per seller account

## Environment Variables

```
SMARTSTORE_APPLICATION_ID=your_application_id
SMARTSTORE_APPLICATION_SECRET=your_application_secret
```
