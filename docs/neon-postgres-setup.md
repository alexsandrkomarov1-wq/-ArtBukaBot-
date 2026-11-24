# KOMAROVA_CORE — Neon PostgreSQL deployment

**Status:** implementation-ready configuration; no Neon project has been provisioned or connected by this commit.

## Purpose

Neon is the managed PostgreSQL database for the authoritative KOMAROVA_CORE registry. It stores structured records (people, permanent PERSON-IDs, relationships, accounts, audit events and later family events/places). It is not the binary family archive. Photos, videos and document bytes belong in a separate private object store such as Cloudflare R2.

## Application configuration

Set `DATABASE_URL` to Neon's PostgreSQL connection string. Prefer the pooled connection string (the hostname normally contains `-pooler`) for the web application. The connection string must include TLS, normally `sslmode=require`.

The backend accepts Neon's standard `postgresql://` URL and normalizes it to SQLAlchemy's explicit `postgresql+psycopg://` driver. The psycopg 3 driver is installed by `requirements.txt`.

Set these server-side secrets as deployment environment variables; never commit them:
- `DATABASE_URL` — Neon pooled connection string for application traffic.
- `CORE_JWT_SECRET` — random secret of at least 32 characters.
- `CORE_BOOTSTRAP_TOKEN` — one-time owner bootstrap secret; remove/rotate after owner creation according to the operational procedure.

Do not expose any of these variables to browser/client code or prefix them with a public frontend variable name.

## Schema deployment

Run migrations once as a controlled release step, not independently in every application worker:

```bash
python -m backend.app.migrate
```

Then deploy/start the API. Startup verifies that the database is already at the current Alembic migration head and fails closed if it is not.

Do not create tables manually in the Neon SQL editor. The repository migrations are the schema authority. Do not point the migration command at an existing production database until its contents and backup state have been checked.

## Connection pooling

For serverless hosting, set `VERCEL=1` (provided automatically by Vercel) and use Neon's pooled connection URL. The application uses SQLAlchemy `NullPool` in serverless mode so each invocation does not retain idle connections. For a long-running service, the default pool is small (3 connections plus at most 2 overflow); adjust only after checking the Neon plan's connection limits.

## Migration and compatibility gate

The current application and migration suite were originally developed against SQLite. PostgreSQL support must be proven by a disposable Neon development project before any family data is imported. Specifically verify:
1. all Alembic revisions apply cleanly to an empty PostgreSQL database;
2. API tests for people, relationships, users, sessions and archive metadata pass against PostgreSQL;
3. concurrent bootstrap/login/role-change behavior remains correct;
4. backup/export and restore procedures are tested for PostgreSQL (the current `.kca` archive is SQLite-only and must not be represented as a PostgreSQL backup);
5. database backup and point-in-time recovery settings are documented for the chosen Neon plan.

No real family data should be used for the first cloud validation. Keep the existing SQLite database unchanged as a separate source until a reviewed migration and checksum reconciliation are completed.
