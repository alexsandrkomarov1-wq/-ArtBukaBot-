# KOMAROVA_CORE backend foundation

This branch contains the first executable backend foundation for the family information core. It is development software, not yet a deployed or production-certified private service.

## Local setup

Python 3.11+ is recommended.

~~~bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
~~~

Configure secrets outside the repository. Do not commit real credentials or family data. Apply migrations before launching the API:

~~~bash
python -m backend.app.migrate
~~~

PowerShell example:

~~~powershell
$env:CORE_JWT_SECRET = "<random-secret-at-least-32-characters>"
$env:CORE_BOOTSTRAP_TOKEN = "<separate-one-time-bootstrap-secret>"
$env:DATABASE_URL = "sqlite:///./komarova_core.db"
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8081
~~~

Apply Alembic migrations once before starting API workers. The API checks that the database is at the current migration head and refuses to start if it is not. This avoids multiple worker processes racing to apply migrations. Run the migration command shown below. The initial migration can adopt the previous complete create_all schema without replacing existing records. Partial or structurally incompatible legacy schemas are rejected. The initial schema migration is intentionally forward-only because downgrading it would destroy registry and audit data.

## First owner account

1. Start the backend with both secrets configured.
2. Call POST /api/v1/auth/bootstrap once with X-Core-Bootstrap-Token and JSON containing username and password. Passwords must contain at least 12 characters.
3. Sign in through POST /api/v1/auth/login.
4. Remove CORE_BOOTSTRAP_TOKEN from the runtime environment after the owner account has been created. Bootstrap is also blocked automatically once any account exists.

The JWT signing secret must contain at least 32 characters. Access tokens expire after 30 minutes. Sessions are stored in the database and checked on every authenticated request; logout, password changes, and account disabling revoke active sessions. Login failures are tracked in the database: five failures for the same username and direct client IP trigger a 15-minute lockout. Bootstrap and owner-administration writes use a database lock row so concurrent workers serialize these security-sensitive changes.

## Accounts and roles

Four roles are implemented:

| Role | Permissions |
| --- | --- |
| owner | Full account administration, role assignment, and registry write access |
| moderator | Create/manage family-member and guest accounts; registry write access, but cannot grant roles or manage owner/moderator accounts |
| family_member | Read the registry, add people, and create relationships |
| guest | Read-only registry access |

Only the owner can change account roles. The last active owner cannot be disabled or demoted. Usernames are unique and normalized to lowercase. Passwords are stored as Argon2 hashes, never in plaintext.

## API endpoints

- POST /api/v1/auth/bootstrap — create the first owner account.
- POST /api/v1/auth/login — create a 30-minute bearer session.
- GET /api/v1/auth/me — current account.
- POST /api/v1/auth/logout — revoke the current session.
- POST /api/v1/auth/change-password — change password and revoke all active sessions.
- GET /api/v1/auth/sessions — list current user's sessions.
- POST /api/v1/users — create an account according to the caller's role.
- GET /api/v1/users — list accounts for owner/moderator.
- PATCH /api/v1/users/{user_id} — update account role/status under the role rules.
- POST /api/v1/people — create a person with permanent PERSON-ID.
- GET /api/v1/people — list active people; include_archived=true includes archived entries.
- GET /api/v1/people/{person_id} — retrieve a person.
- PATCH /api/v1/people/{person_id} — change display name without changing PERSON-ID.
- DELETE /api/v1/people/{person_id} — soft archive.
- POST /api/v1/relationships — link two existing people.
- GET /api/v1/people/{person_id}/relationships — list links for a person.
- GET /api/v1/navigation — authenticated, role-aware navigation manifest for capabilities that currently exist in the private API.
- GET /api/v1/search?q=... — authenticated search of active people by display name or PERSON-ID; supports Cyrillic case-insensitive matching and returns entity IDs plus API detail endpoints.

All authenticated endpoints use Authorization: Bearer <access_token>. The public GET /health endpoint contains no personal data. API documentation endpoints remain disabled.

## Remaining production work

This branch is not deployed. Before production use it still needs HTTPS hosting, secret management, rate limiting and abuse controls, verified backup/restore, encryption-at-rest decisions, operational monitoring, a reviewed account recovery process, and independent security review. The static GitHub Pages site is not connected to this backend. Do not use real family data in this public development repository.


## Security controls added in revision 0003

- Disabling an account revokes every active session in the same transaction. Re-enabling the account does not revive old tokens.
- A database-backed lock row serializes first-owner bootstrap and owner role/status changes across processes and supported SQL databases.
- Login throttling is persisted in the database: five failed attempts for a username and direct client IP trigger a 15-minute lockout. Forwarded IP headers are intentionally not trusted.
- SQLite backup uses the online backup API. Restore validates the source and creates a new destination atomically; it refuses to overwrite an existing file. The portable database archive adds a SHA-256 manifest and verifies schema and foreign-key integrity.

These controls are not a substitute for a production WAF, monitoring, incident response, off-site encrypted backups, or a formal security review. The current lock row serializes login validation and owner administration; this is safe but may become a throughput bottleneck and should be replaced with finer-grained database locking when moving to PostgreSQL.

## Portable database archive (format v1)

The code now supports a portable ZIP-based database archive with a JSON manifest and SHA-256 checksum. It verifies the archive structure, database checksum, SQLite integrity, required KOMAROVA_CORE tables, foreign-key consistency, and Alembic schema revision.

Set `DATABASE_URL` to the SQLite database to export, then run:

~~~bash
python -m backend.app.archive_cli export /safe/location/family-core.kca
python -m backend.app.archive_cli verify /safe/location/family-core.kca
python -m backend.app.archive_cli restore /safe/location/family-core.kca /safe/location/restored-core.sqlite3
~~~

PowerShell example:

~~~powershell
$env:DATABASE_URL = "sqlite:///./komarova_core.db"
python -m backend.app.archive_cli export "D:\FamilyBackups\family-core.kca"
python -m backend.app.archive_cli verify "D:\FamilyBackups\family-core.kca"
python -m backend.app.archive_cli restore "D:\FamilyBackups\family-core.kca" "D:\FamilyBackups\restored-core.sqlite3"
~~~

Exports and restores refuse to overwrite existing destination files. Restore always targets a new database file. Keep archives outside the public GitHub repository and protect them as sensitive family data.

**Scope limitation:** archive format v1 contains the relational SQLite database only. The project's binary media/object-storage layer has not yet been implemented, so photographs, videos, audio and document file contents are not yet packaged. They must be added as separately checksummed archive members before this can be called a complete family-library export.


## Integrated navigation and search API

The private API now exposes a single role-aware navigation manifest and a search endpoint over the existing people registry. The manifest does not advertise unimplemented destinations: account administration is omitted for family-member and guest roles. Search is authenticated and returns only active people; it does not expose the private registry to the public GitHub Pages site.

Search currently covers only the implemented `people` entity. Events, places, journeys, photographs, documents and family stories are not searchable until their data models and access rules exist. The API manifest is a backend contract for the private application, not a claim that a complete browser-based private UI has already been built. Search currently performs Unicode case-fold matching in application code to support Cyrillic names on SQLite; for very large registries this should be replaced with an indexed normalized search field in a reviewed database migration.


## Private photo/video intake API (development only)

The API now contains a first authenticated media-intake slice. Apply migration `0005_private_media_intake` using the existing migration command before starting the application.

Set `CORE_MEDIA_ROOT` to a private, persistent directory outside the Git checkout and public web root. Example PowerShell configuration:

~~~powershell
$env:CORE_MEDIA_ROOT = "D:\\KOMAROVA_PRIVATE_MEDIA"
python -m backend.app.migrate
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8081
~~~

Endpoints (all require a valid bearer session):
- `POST /api/v1/archive/items` — authenticated multipart photo/video upload; owner, moderator and family_member roles only.
- `GET /api/v1/archive/items` — list archive metadata.
- `GET /api/v1/archive/items/{archive_item_id}` — read one archive metadata record.
- `POST /api/v1/archive/items/{archive_item_id}/links` — link to an existing active PERSON-ID.
- `GET /api/v1/archive/items/{archive_item_id}/links` — list confirmed person links.

The upload endpoint streams in 1 MiB chunks, enforces a 100 MiB maximum, checks a supported file signature, calculates SHA-256 and rejects exact duplicate content. Original bytes are placed in a private quarantine directory. The response does not disclose storage paths or object keys.

**Quarantine is intentional.** No antivirus scanner, isolated media decoder, derivative generation, preview/download/stream route, event/place registry, cloud storage adapter, browser private UI, or production deployment is configured. The service does not yet make quarantined files viewable. Do not upload real family media to this development repository or an unreviewed host. A persistent private volume and backup policy are mandatory; ephemeral container disk is not durable storage.

The old root-level `komarova_file_engine.py` remains a separate legacy tool for a different SQLite schema. It is not used by the API and must not be pointed at the backend database.


## Orientation-aware media derivatives (development utility)

backend.app.media_processing contains post-scan derivative utilities:
- normalize_photo(..., scanner_state="clean") applies EXIF Orientation and writes a WebP derivative. HEIC/HEIF support uses pillow-heif.
- normalize_video(..., scanner_state="clean") uses FFprobe and FFmpeg to autorotate and transcode to H.264/AAC MP4.

Both utilities refuse quarantined input and never overwrite the original. They are not called by the upload endpoint or a worker yet. FFmpeg/FFprobe must be installed on the private worker. Do not expose derivatives until a scanner, derivative registry, checksum persistence and authorized preview route are implemented.
