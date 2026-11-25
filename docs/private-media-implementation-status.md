# KOMAROVA_CORE — private media implementation status

**Audit date:** 25 November 2026  
**Audit base:** `core-backend-foundation`  
**Implementation branch:** `feature/private-media-access-and-recovery`  
**Scope:** family portrait persistence, private object storage, PERSON-ID links, consent, recovery and security.

## 1. Verified repository baseline

The backend source is present, but it is development software and is not deployed as a production private service.

| Capability | Existing code | Operational status |
|---|---|---|
| Authenticated API | FastAPI auth, sessions, roles and rate-limited login | Implemented in source; backend not deployed |
| Media intake | `POST /api/v1/archive/items`, streaming upload, 100 MiB limit, basic file-signature allowlist, SHA-256, duplicate detection | Implemented as development quarantine intake |
| Storage adapter | `PrivateMediaStorage` supports local-private and S3-compatible configuration | Adapter exists; no production persistent volume or S3 provider configured |
| Media metadata | `StoredBlob`, `ArchiveItem` | Migration `0005_private_media_intake` exists |
| PERSON-ID association | Optional `person_id` on intake and authenticated link/list endpoints; API verifies an active Person record | Backend association slice exists; portrait browser UI is not integrated |
| Per-person consent | No consent/approval entity or participant-to-account authority model | Not implemented |
| Public publication | No publication workflow or public media URL | Not implemented; media remains quarantined |
| Database backup | SQLite online backup and verified restore; portable database archive v1 | Implemented for database only |
| Media backup/restore | Binary objects are not included in database backup/archive v1 | Not implemented |
| Malware scanning | No scanner or isolated scanning worker | Not implemented; quarantine blocks viewing |
| Production security | Several source-level controls exist; production hosting, secret management, monitoring and independent review remain pending | Not production-ready |

## 2. Important corrections to the status register

The six top-level labels must distinguish source code from an operationally available service:

1. **Permanent saving:** a development upload endpoint writes originals into quarantine. This is not yet a deployed, durable family archive.
2. **Private storage:** local-private and S3-compatible adapters exist in source. No approved production storage endpoint, persistent volume, credentials or read-back verification is configured.
3. **PERSON-ID:** the backend already supports linking an uploaded archive item to an existing PERSON-ID. The portrait picker on GitHub Pages does not yet call this API.
4. **Permissions:** existing API role checks protect endpoints. They are not equivalent to item-level access grants or the depicted person's consent to storage, family viewing or public publication.
5. **Backup and restore:** database-only backup/restore exists. It does not include the binary media objects and therefore is not a complete family archive recovery.
6. **Security:** upload size/signature checks, SHA-256, duplicate detection, quarantine and authenticated routes exist. Malware scanning, production deployment hardening, operational monitoring, and a full media recovery drill remain outstanding.

## 3. Delivery sequence

### Phase A — deployable private foundation
- Keep the existing FastAPI backend and migration history.
- Confirm the approved runtime host and a durable private media volume or S3-compatible bucket.
- Keep all credentials outside GitHub and browser code.
- Configure HTTPS, CORS allowlist, health monitoring and persistent storage.
- Run migrations against a disposable test database before any production database.

### Phase B — media identity and permissions
- Preserve existing `StoredBlob`, `ArchiveItem` and archive IDs.
- Preserve the existing PERSON-ID link API and integrate the portrait interface with it.
- Add an explicit participant/account association and a reviewed authority model before implementing self-consent or guardian consent.
- Store separate, revocable permissions for archive storage, family viewing and public publication.
- Default to deny. A family role or successful upload must never imply publication consent.
- Do not implement a public media route until the consent and withdrawal workflow is tested.

### Phase C — media safety and delivery
- Add an isolated malware-scanning process and explicit state transitions out of quarantine.
- Generate previews/derivatives only from verified clean originals; never overwrite originals.
- Add authorized private preview/download endpoints with no public object URLs.
- Integrate upload, replacement, retrieval and deletion in the portrait UI.
- Audit every upload, link, view, permission change, export and deletion.

### Phase D — complete backup and recovery
- Extend portable archive format with a versioned media manifest and original binary objects.
- Include stable IDs, SHA-256, byte size, detected MIME type, object metadata and PERSON-ID links.
- Verify every object on export and restore.
- Support restore to a different compatible storage provider without changing PERSON-ID or archive IDs.
- Perform a documented restore drill before production acceptance.

### Phase E — security acceptance
- Test unauthenticated and unauthorized read/write attempts.
- Test cross-person access denial and revoked consent.
- Test malformed, mismatched, oversized and hostile media.
- Test interrupted upload, storage outage, duplicate upload and partial deletion.
- Verify private cache headers, no public URLs, no secrets in logs and no media in the public repository.
- Verify encrypted off-server backup and full media restore.

## 4. Infrastructure constraints

- GitHub Pages is only the public static presentation layer; it is not the private API or media store.
- The backend hosting proposal records that no production VPS has been provisioned.
- The existing Neon project is in Ohio; the EU data-region decision must be made before real family data is stored there.
- Do not create a paid server, start a paid plan, create a replacement database project, move data or register a domain without the required explicit approval.
- The current repository is public. No real family photographs, personal records, tokens or credentials may be committed to it.
- A provider adapter in source code is not evidence that a provider is connected or that its storage is durable.

## 5. Completion rule

A capability is marked **implemented** only after code and automated tests pass. It is marked **operational** only after the intended private environment is configured and an authenticated end-to-end check succeeds. It is marked **verified** only after the relevant failure, security and recovery tests pass.

Do not merge this work into `main`. Continue from `core-backend-foundation` through a dedicated feature branch and pull request.
