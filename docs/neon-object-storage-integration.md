# Private media storage integration

The API supports two private storage backends:

- `local` (default): private filesystem storage, suitable for local development and tests.
- `s3`: S3-compatible object storage, including Neon Object Storage.

For Neon Object Storage, configure these runtime environment variables. Never commit real values:

- `CORE_STORAGE_BACKEND=s3`
- `CORE_S3_ENDPOINT_URL`: branch-specific endpoint from Neon
- `CORE_S3_REGION`: for this Neon project, `us-east-2`
- `CORE_S3_BUCKET=uploads`
- `CORE_S3_ACCESS_KEY_ID`: scoped Neon storage credential
- `CORE_S3_SECRET_ACCESS_KEY`: scoped Neon storage credential secret

The credential should be limited to `storage:read` and `storage:write`, scoped to the intended branch, and stored only in the deployment provider's secret manager. Test-branch credentials must never be reused for production.

The existing authenticated archive endpoint keeps its current validation and quarantine workflow. It computes SHA-256 and validates the media signature before storage, then uses a conditional S3 write so an existing content-addressed object is not overwritten. The API currently receives the upload body; a browser-to-object-store presigned upload flow is a separate follow-up because it needs a carefully designed finalize/checksum protocol.

The database records the provider and object key, not a public URL. Buckets remain private. No public-read ACL or public bucket is used.

## PostgreSQL CI

The backend workflow runs the complete Alembic chain against a disposable PostgreSQL 18 service and compares the resulting table set with SQLAlchemy metadata. This is a migration compatibility check, not a migration of the production Neon branch.
