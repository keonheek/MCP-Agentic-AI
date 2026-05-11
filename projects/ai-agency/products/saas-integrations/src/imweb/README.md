# Imweb Integration

API: https://api.imweb.me/v2/doc

## Required API Credentials

| Credential | Where to Get |
|---|---|
| API Key | Imweb dashboard > Settings > Developer > API |
| API Secret | Same page |

No OAuth redirect required. Credential-based auth only.

## Auth Flow

1. Get API Key and Secret from Imweb dashboard.
2. Call POST `/v2/api/auth/token` with key + secret.
3. Store returned `access_token` (valid 24 hours).
4. Attach as header: `access-token: {token}`.
5. `ImwebClient.authenticate()` handles this automatically.

## Webhook Setup

1. Register endpoint in Imweb dashboard > Settings > Developer > Webhook.
2. Or call `subscribe_webhook(event_type, callback_url)`.
3. Verify with `X-IMWEB-SIGNATURE` header (HMAC-SHA256 of body using api_secret).

## Required Permissions

Set in Imweb dashboard under API permissions:
- Order read/write
- Member read
- Webhook management
- Product read

## Rate Limits

- 60 requests per minute per site
- No documented burst limit

## Environment Variables

```
IMWEB_API_KEY=your_api_key
IMWEB_API_SECRET=your_api_secret
```
