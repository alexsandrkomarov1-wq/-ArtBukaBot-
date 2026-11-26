# Neon Auth integration for KOMAROVA_CORE

## Chosen integration model

Neon Managed Auth is the identity provider. KOMAROVA_CORE remains the authorization authority:
- Neon verifies sign-in and issues short-lived EdDSA access tokens.
- The API verifies tokens against the configured Neon JWKS endpoint and issuer.
- An explicit row in `external_identities` maps the immutable Neon subject to an existing local `users.user_id`.
- The local `users.role` and `users.status` remain authoritative. Client metadata and email addresses never grant roles or link accounts.
- Existing KOMAROVA_CORE username/password JWT sessions remain valid during the transition.

## Required API environment

Set these server-side only:
- `NEON_AUTH_BASE_URL`: exact Managed Auth base URL for the selected Neon branch (issuer).
- `NEON_AUTH_JWKS_URL`: JWKS URL returned by that branch's Neon Auth configuration.
- Keep `CORE_JWT_SECRET` during the transition so existing sessions and the secure linking step continue to work.

Never place these values in Git, browser JavaScript, or public GitHub Pages assets. The URLs are not passwords, but must match the intended branch exactly.

## One-time account linking

1. The user signs in with their existing KOMAROVA_CORE account.
2. The browser signs in to Neon Auth and obtains a fresh access token using the Managed `@neon/auth` client.
3. While sending the existing KOMAROVA_CORE bearer token, POST `{"neon_access_token":"<token>"}` to `/api/v1/auth/neon/link`.
4. The API validates signature, issuer and expiry using Neon JWKS, then links the token's `sub` to the already authenticated local account.
5. Subsequent protected API requests may use the Neon bearer token. Local role and disabled-account checks still run on every request.

No email matching, automatic user creation, password migration, or role copying occurs. A Neon identity already linked to another local account is rejected.

## Cutover and production

Do not remove the legacy login/session tables or `CORE_JWT_SECRET` until all accounts are linked, recovery has been tested, and the owner explicitly approves a later cutover. Use the integration branch first. Production must have a verified custom SMTP setup, trusted production origin, and closed/controlled signup policy before public launch.
