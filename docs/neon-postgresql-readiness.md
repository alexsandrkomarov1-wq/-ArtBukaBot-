# Neon PostgreSQL readiness

Status: implementation preparation only. No Neon project has been inspected or modified by this repository change.

## Purpose

Neon is the managed PostgreSQL database for KOMAROVA_CORE. It stores structured records and metadata: people and permanent PERSON-ID values, relationships, accounts, sessions, audit events, and archive metadata. It is not the binary family-media archive.

## Runtime connection

Set `DATABASE_URL` in the hosting provider's encrypted environment-variable settings. Use the Neon pooled connection string for the application runtime when available. The application accepts Neon’s standard `postgresql://` URL and normalizes it to SQLAlchemy's `postgresql+psycopg://` driver.

Keep the direct (non-pooled) Neon connection string separately for one-off Alembic migrations. Do not commit either connection string, database password, API key, or local environment file.

## Migration procedure

1. Confirm the target Neon project and database with the account owner.
2. Confirm that the target database is empty or has been backed up and explicitly approved for migration.
3. Set the direct Neon URL as `DATABASE_URL` in a protected one-off migration environment.
4. Run `python -m backend.app.migrate` once.
5. Verify Alembic revision is `0005_private_media_intake`, inspect all expected tables, and run read/write smoke tests.
6. Configure the runtime with the pooled Neon URL and verify health, authentication, people, relationships, and audit operations.

Never run migrations against an unverified project or overwrite existing data.

## Important storage boundary

The current media-intake implementation still writes quarantined binary files to a local filesystem directory. Neon stores only relational metadata. Cloudflare R2 integration is a separate required implementation before family photos, videos, audio, and documents can be durably stored in the cloud. Do not use ephemeral application disk for family originals.

## Deployment boundary

This repository change does not provision Neon, deploy the API, or configure Vercel/another application host. Credentials must be entered by the account owner into the provider's protected settings after the project and hosting environment are verified.
