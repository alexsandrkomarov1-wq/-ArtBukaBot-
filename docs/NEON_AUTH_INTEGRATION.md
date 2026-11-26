# KOMAROVA_CORE — Neon Auth integration

**Date:** 26 November 2026  
**Git branch:** `core-backend-foundation`  
**Neon project:** `wandering-unit-05985607`  
**Status:** Neon Auth is provisioned on the integration database branch; application-level authentication cutover is not complete.

## Existing Neon infrastructure

A Neon project already existed, so a duplicate database was not created.

- Project: `wandering-unit-05985607`
- Region: `aws-us-east-2`
- PostgreSQL: 18
- Default branch: `production`
- Neon Auth provider: Managed Better Auth
- Auth schema: `neon_auth`

The project is on the Neon Free plan. No paid AI Gateway usage is required for authentication.

## Dedicated integration branch

Created a separate branch from the existing application-schema test branch:

- Name: `komarova-core-auth-integration`
- Branch ID: `br-bold-unit-bd2pnbpn`
- Parent: `komarova-core-schema-test`
- Purpose: isolated integration and verification only; not production.

The branch contains both the Managed Auth schema and the KOMAROVA_CORE application schema. Its Alembic revision was advanced from `0005_private_media_intake` to `0007_entity_graph`, matching the current source migrations. The migration added the MATERIAL-ID registry and event/place/entity graph tables. No family records were imported.

The following trusted origin was added to this branch:

- `https://alexsandrkomarov1-wq.github.io`

The Neon Auth application display name is `KOMAROVA_CORE`.

## Current Auth settings on the integration branch

- Managed Better Auth: enabled.
- Email/password: enabled.
- Email verification: currently disabled.
- New account sign-up: currently enabled.
- Shared Neon SMTP: configured for development.
- Localhost origins: allowed for development.
- Google: Neon shared development OAuth provider.

These are development settings, not production approval. Do not invite family members or expose private archive functions until email verification, account provisioning, role assignment, and protected API access have been implemented and tested.

## Application integration boundary

The current web frontend is a static GitHub Pages/Jekyll site. The existing API source is Python/FastAPI and is not deployed yet.

The API currently authenticates with its own HS256 JWT implementation and its own `users` / `auth_sessions` tables. Neon Auth users and sessions are separate records in `neon_auth`. Merely provisioning Neon Auth does not make the existing API accept Neon sessions.

Required implementation before claiming login is live:

1. Add a supported, pinned `@neon/auth` browser client to the private application UI.
2. Verify Managed Auth JWTs in FastAPI using the branch JWKS endpoint and strict issuer/algorithm/expiry validation.
3. Add an explicit identity link from Neon Auth user ID to the internal KOMAROVA_CORE user/role record.
4. Preserve the four application roles: owner, moderator, family_member, guest. Never grant owner or other roles automatically from public sign-up.
5. Enforce authorization on every private API route. A valid Neon session alone must not grant access to another person's records.
6. Keep legacy login available until the Neon Auth flow passes tests; only then plan a reviewed cutover.
7. Test sign-up, sign-in, sign-out, session restoration after reload, wrong-password handling, and direct unauthenticated access to protected endpoints.

## Deployment and privacy gates

- Do not put Neon secrets, database connection strings, or server credentials in GitHub Pages or the public repository.
- GitHub Pages is not the private backend and must not store original family files.
- Do not declare the application login complete until a Python/FastAPI backend is deployed over HTTPS and the browser-to-API flow is verified.
- Keep this Neon branch isolated for integration. Do not change the default `production` branch or import real family data as part of this step.
- Before real family records are stored, resolve the existing database-region decision. The current project is in Ohio; Neon project regions cannot be changed in place.
- Production should use a verified email provider and an explicit owner-controlled account invitation/provisioning process.

## Verification recorded

- Neon Auth config read successfully on `komarova-core-auth-integration`.
- The branch's trusted-origin allowlist contains the GitHub Pages origin.
- The application schema reports Alembic revision `0007_entity_graph`.
- Both `neon_auth` and KOMAROVA_CORE application tables are present.
- The branch was created from the schema-test branch; the default production branch was not modified by this integration setup.
