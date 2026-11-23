# KOMAROVA_CORE backend foundation

This is the first executable backend slice: people registry, immutable PERSON-ID values, directed relationship records, soft archival, API-token gate, and an audit trail.

## Run locally

Python 3.11+ is recommended.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
```

Set a private API token before starting the server:

```bash
# PowerShell
$env:CORE_API_TOKEN = "replace-with-a-long-random-secret"
$env:DATABASE_URL = "sqlite:///./komarova_core.db"
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8081
```

The health endpoint is `GET /health`. All data endpoints require the `X-Core-Token` header. API documentation endpoints are disabled in this initial private-data foundation.

## API

- `POST /api/v1/people` — create a person; server assigns a permanent `P-...` identifier.
- `GET /api/v1/people` — list active people; `include_archived=true` includes archived entries.
- `GET /api/v1/people/{person_id}` — retrieve a person.
- `PATCH /api/v1/people/{person_id}` — change display name without changing PERSON-ID.
- `DELETE /api/v1/people/{person_id}` — archive, never physically delete.
- `POST /api/v1/relationships` — link two existing people.
- `GET /api/v1/people/{person_id}/relationships` — list links for a person.

The optional `X-Actor-ID` header is recorded in the audit trail. Do not use real family data in this development build.

## Current limitations

This is not production-ready. API-token access is a temporary single-secret gate, not the approved multi-user role model. Database migrations, encryption at rest, backup/restore automation, rate limiting, account lifecycle, and independent security review are not implemented yet. The SQLite schema is initialized on startup for this first slice; schema migrations must be introduced before production use.
