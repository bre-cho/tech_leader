# Accounts + AI Engine Settings Patch

## Adds

### Frontend

```text
/accounts
/settings/ai-engine
```

### Backend API

```text
GET  /api/settings/google-accounts
POST /api/settings/google-accounts
PATCH /api/settings/google-accounts/:id
DELETE /api/settings/google-accounts/:id
POST /api/settings/google-accounts/:id/refresh
POST /api/settings/google-accounts/rotation

GET   /api/settings/openrouter
PATCH /api/settings/openrouter
POST  /api/settings/openrouter/test
```

### Provider Runtime

```text
POST /api/providers/google-managed/nano-banana/generate
POST /api/providers/google-managed/veo/generate
```

## Google Accounts

Use Accounts tab to add, remove, or refresh Google AI accounts.

Enable Account Rotation to auto-cycle per scene:

```text
scene 0 → account A
scene 1 → account B
scene 2 → account C
scene 3 → account A
```

Capabilities:

```text
nano_banana
veo_3_1
```

## OpenRouter Settings

Use Settings → AI Engine to update OpenRouter key or switch models.

OpenRouter uses Bearer token auth:

```text
Authorization: Bearer <OPENROUTER_API_KEY>
```

Optional attribution headers:

```text
HTTP-Referer
X-Title
```

## Security

Keys are never returned to frontend in raw form.

Stored data:

```text
storage/settings/google-accounts.json
storage/settings/openrouter.json
```

Secrets are encrypted with AES-256-GCM using:

```bash
APP_SECRET=change-me
```

## Notes

- Nano Banana uses Gemini image generation models such as `gemini-3.1-flash-image-preview`.
- Veo 3.1 uses Gemini API video generation long-running operations.
- This patch writes operation manifests for Veo and image artifacts for Nano Banana.
