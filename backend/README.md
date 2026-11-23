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

All authenticated endpoints use Authorization: Bearer <access_token>. The public GET /health endpoint contains no personal data. API documentation endpoints remain disabled.

## Remaining production work

This branch is not deployed. Before production use it still needs HTTPS hosting, secret management, rate limiting and abuse controls, verified backup/restore, encryption-at-rest decisions, operational monitoring, a reviewed account recovery process, and independent security review. The static GitHub Pages site is not connected to this backend. Do not use real family data in this public development repository.


## Security controls added in revision 0003

- Disabling an account revokes every active session in the same transaction. Re-enabling the account does not revive old tokens.
- A database-backed lock row serializes first-owner bootstrap and owner role/status changes across processes and supported SQL databases.
- Login throttling is persisted in the database: five failed attempts for a username and direct client IP trigger a 15-minute lockout. Forwarded IP headers are intentionally not trusted.
- SQLite backup uses the online backup API. Restore writes to a temporary file, checks integrity, and atomically replaces only the destination. The automated test restores into a separate database and checks both registry data and migration version.

These controls are not a substitute for a production WAF, monitoring, incident response, off-site encrypted backups, or a formal security review. The current lock row serializes login validation and owner administration; this is safe but may become a throughput bottleneck and should be replaced with finer-grained database locking when moving to PostgreSQL.
