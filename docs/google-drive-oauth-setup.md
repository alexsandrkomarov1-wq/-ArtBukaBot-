# Google Drive OAuth setup

This integration starts with read-only Google Drive account metadata and quota access. It does not read file contents, upload, modify, or delete files.

## Google Cloud setup

1. Open https://console.cloud.google.com/apis/credentials and create or select a Google Cloud project.
2. Enable the Google Drive API: https://console.cloud.google.com/apis/library/drive.googleapis.com
3. Configure Google Auth Platform consent screen / branding and audience. For initial testing, use External + Testing and add the Google accounts that will test the integration as test users. Do not publish the app yet.
4. Create an OAuth client ID with application type **Web application**.

   **Important:** Google OAuth projects in External / Testing mode issue refresh tokens that expire after 7 days for Drive scopes. Use Testing only for a short initial test; before ongoing family use, review Google's production-readiness and verification requirements and publish appropriately. Do not treat a testing token as permanent storage authorization.
5. Add this exact Authorized redirect URI:

   `https://YOUR_API_HOST/api/v1/integrations/google-drive/callback`

6. Save the OAuth Client ID and Client Secret. The client secret must remain server-side.

Google's official web-server OAuth guide: https://developers.google.com/identity/protocols/oauth2/web-server

## Server environment

Set these values in the backend host's private environment/secrets manager. Never commit them to GitHub or place them in frontend code.

- `GOOGLE_OAUTH_CLIENT_ID`: OAuth client ID.
- `GOOGLE_OAUTH_CLIENT_SECRET`: OAuth client secret.
- `GOOGLE_DRIVE_REDIRECT_URI`: exact HTTPS callback URI configured above.
- `CORE_OAUTH_ENCRYPTION_KEY`: URL-safe base64 encoding of exactly 32 random bytes. Generate with:

  `python -c "import base64,secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('='))"`

Also configure the existing production variables: `DATABASE_URL`, `CORE_JWT_SECRET`, and the normal API runtime settings.

## Authorization and data handling

- OAuth uses `access_type=offline` and a one-time, 10-minute state value bound to the signed-in KOMAROVA_CORE user.
- The initial scope is only `https://www.googleapis.com/auth/drive.metadata.readonly`.
- The callback reads Google account identity and Drive quota, then discards the short-lived access token.
- The long-lived refresh token is encrypted with AES-256-GCM before it is stored in Neon. The encryption key is separate from the database.
- API responses and logs must never expose access tokens, refresh tokens, client secrets, or encryption keys.
- Each KOMAROVA_CORE user may connect multiple distinct Google accounts while signed in. Each Google identity is globally unique and cannot be linked to a second KOMAROVA_CORE user. No automatic cross-family sharing is granted.
- File contents and write scopes are deliberately out of scope for this first authorization milestone. They require a separately reviewed incremental authorization and file-operation implementation.
- Disconnect revokes the Google token and removes the local account link.

## API endpoints

All endpoints except the OAuth callback require a valid KOMAROVA_CORE bearer session:

- `GET /api/v1/integrations/google-drive/connect` returns the Google authorization URL.
- `GET /api/v1/integrations/google-drive/callback` receives Google's authorization response.
- `GET /api/v1/integrations/google-drive/status` reports all linked accounts and their quotas.
- `POST /api/v1/integrations/google-drive/accounts/{drive_account_id}/refresh-quota` refreshes one selected account quota.
- `DELETE /api/v1/integrations/google-drive/accounts/{drive_account_id}` revokes and removes only the selected account.

One KOMAROVA_CORE user may link multiple distinct Google accounts. Each has a permanent `drive_account_id`, separate encrypted refresh token and quota. A Google identity cannot be linked to a second KOMAROVA_CORE user.

## Deployment gate

Apply Alembic revision `0006_google_drive_oauth` only to a verified target database after a backup and migration review. Do not apply it to production until the VPS, HTTPS API hostname, Neon production target, and server-side secrets are confirmed. The OAuth redirect URI must point to the deployed API, not GitHub Pages.
