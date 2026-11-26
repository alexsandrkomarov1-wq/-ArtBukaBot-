# KOMAROVA_CORE — cloud and archive storage configuration

**Status:** approved storage requirements and provider design  
**Date:** 23 November 2026  
**Target branch:** `core-backend-foundation`  
**Implementation status:** designed; live provider authorization, transfer, and restore are not yet implemented.

## 1. Purpose

This document records the storage configuration for KOMAROVA_CORE. It extends the existing family archive model and does not replace the authoritative registry, existing PERSON-ID values, or the local DELL archive structure.

The archive must remain usable if any one cloud account, vendor, subscription, or connector is disconnected.

## 2. Non-negotiable storage rules

1. The family archive is owned by the family, not by Microsoft, Google, Yandex, GitHub, or a hosting vendor.
2. Original files remain on the device and in the source location of their owner. KOMAROVA_CORE stores a separate copy only after an explicit import/share action.
3. A cloud provider is a storage location, not the authoritative registry. The authoritative metadata, permanent IDs, relationships, permissions, and audit trail belong to KOMAROVA_CORE.
4. External storage connectors are optional, independently pausable, replaceable, and removable. Disconnecting one provider must not delete archive records or copies held by another provider.
5. No provider may be the only location of a family original or the only route to recover the archive.
6. Original bytes are immutable. A preview, conversion, restoration, or AI-edited file is a separate derivative with its own ID and provenance.
7. Never commit OAuth client secrets, refresh tokens, passwords, real family files, manifests containing personal paths, or provider credentials to Git.
8. No silent move or deletion of a source file. Import means copy. Source deletion, if ever offered, requires a separate explicit confirmation after integrity verification.
9. All provider transfers are private by default and use authenticated, least-privilege access.
10. A connector is not marked connected until an actual OAuth round trip, file write, file read-back, checksum comparison, disconnect, and reconnect test have passed.

## 3. Configured provider set

The initial provider set is:

| Provider key | Service | Role | Initial status |
|---|---|---|---|
| `microsoft_onedrive` | Microsoft OneDrive | Optional external copy of family archive objects | Designed; not connected |
| `google_drive` | Google Drive | Optional external copy of family archive objects | Designed; not connected |
| `yandex_disk` | Yandex Disk | Optional external copy of family archive objects | Designed; not connected |
| `local_private` | Private local/server storage | Development and staging storage adapter; not a durable production guarantee | Implemented in current archive intake, deployment-dependent |
| `supabase_storage` | Supabase Storage + PostgreSQL metadata | Candidate private media target for the current web archive | Client and SQL schema prepared; project credentials, RLS, upload/read-back and restore tests still pending |

Microsoft Outlook/Hotmail, Gmail, and Yandex Mail are mail services, not file-storage destinations. Mail integration is a separate connector with separate consent and scopes. This storage configuration covers OneDrive, Google Drive, and Yandex Disk only.

## 4. Logical storage layout

The local DELL project structure already established by the user remains the local workspace and must not be replaced:

```text
KOMAROVA_CORE/
  storage/
    local/
    family_archive/
    external_connectors/
      microsoft_onedrive/
      google_drive/
      yandex_disk/
    backup/
    recovery/
    incoming/
    quarantine/
    verified/
    import_logs/
  core/
    data_registry/
    identity/
    permissions/
    synchronization/
  protocols/
    storage_api/
    synchronization/
```

These directories are a local organizational structure. Their presence does not mean cloud accounts are authenticated or synchronized.

In each provider account, create a private application folder named `KOMAROVA_CORE`. Within it, objects use opaque generated keys, not names, email addresses, PERSON-IDs, or original filesystem paths. The database maps each Blob ID to one or more provider object references.

## 5. Registry and object model

The existing `StoredBlob` remains the logical record for immutable bytes:
- permanent `blob_id`;
- SHA-256 and exact byte size;
- detected MIME type and original filename;
- one or more provider object references;
- availability and integrity state;
- creation and last verification timestamps.

A provider location is a replica/location record, not a new archive identity. Replicating an object to three providers must not create three ArchiveItem records or three PHOTO-IDs.

Each provider object record must include:
- stable internal location ID;
- provider key;
- provider account/connection ID (never the user's password or raw email);
- opaque remote object ID/path;
- object size and checksum when provider supports it;
- state: `pending`, `available`, `paused`, `missing`, `integrity_error`, or `revoked`;
- last successful write/read verification;
- audit reference.

## 6. Account authorization

Each person authorizes their own provider account through the provider's official OAuth consent screen. The application must not ask for or store the user's provider password.

- Microsoft: Microsoft identity platform OAuth 2.0 / Microsoft Graph OneDrive APIs.
- Google: Google OAuth 2.0 / Google Drive API.
- Yandex: Yandex OAuth / Yandex Disk REST API.

Use least-privilege scopes and request only the access required for the selected archive folder and operations. Use authorization-code flow with state validation and PKCE where supported. Refresh tokens, where issued, must be encrypted at rest and kept only in the server-side secret store/database encryption layer. Access tokens must never be exposed to browser JavaScript, GitHub Pages, logs, or repository files.

OAuth application registration, redirect URI configuration, provider verification requirements, and secret provisioning are deployment prerequisites. They are not inferred from the user's email address and cannot be completed by writing a repository file alone.

## 7. Connector lifecycle and user controls

Every provider connection has independent controls:
- Connect account;
- show provider/account label and granted permissions;
- test connection;
- select or create the private `KOMAROVA_CORE` folder;
- pause/resume replication;
- run integrity check;
- disconnect and revoke authorization;
- inspect transfer and error history.

Pausing a provider stops new transfers to that provider but does not disable the family archive, local import, registry, or other providers.

Disconnecting a provider marks its locations as unavailable/revoked. It must not silently delete remote files or delete registry metadata. Remote deletion is a separate, explicit operation with confirmation and audit.

## 8. Import and replication workflow

1. User selects files/folders they are authorized to access.
2. KOMAROVA_CORE copies selected files into its private intake area; it does not move or delete source files.
3. The server validates content, streams SHA-256, records source metadata, and quarantines unsafe or unsupported items.
4. User confirms the import and any PERSON-ID/event links.
5. The authoritative registry creates or reuses the correct ArchiveItem and StoredBlob identity.
6. The primary private archive copy is written and read back; its checksum must match.
7. Enabled provider connectors replicate the same immutable bytes using the same Blob ID and checksum.
8. Each provider replica is independently verified and reported. A failed provider transfer remains retryable and does not roll back a verified copy elsewhere.
9. The UI shows per-provider state. It must never display a generic “saved to cloud” success if only one step succeeded.

Exact duplicates are detected by SHA-256. A duplicate does not silently create a second logical archive object. Similarity-based duplicate suggestions require human review.

## 9. Backup and recovery

The system must support a portable export containing:
- database snapshot and schema/version information;
- ArchiveItem and StoredBlob metadata;
- PERSON-ID and entity relationships;
- provider location references without live credentials;
- original binary objects;
- manifest with SHA-256, byte size, MIME type, and stable IDs;
- audit and import history according to retention policy.

Restore must be possible without the original provider account. The recovery process must be able to import the portable package into a different compatible storage provider or local storage. A restore is complete only after object checksums and registry relationships are verified.

## 10. Security and privacy

- Provider folders are private; no public/share links by default.
- No personal email addresses, source absolute paths, GPS metadata, or family filenames in public repository artifacts or logs.
- OAuth callback endpoints require state/nonce validation, exact redirect URI allowlists, CSRF protection, and secure cookie/session handling.
- Tokens are encrypted at rest, redacted from logs, and revocable.
- Every upload, download, replication, pause, reconnect, revoke, export, and deletion is audited.
- Provider rate limits, quota errors, revoked consent, expired tokens, and partial uploads are explicit states with safe retry behavior.

## 11. Delivery gates

| Gate | Acceptance evidence | Status |
|---|---|---|
| Storage rules and provider set | This approved design and provider registry | Designed |
| Provider app registrations | Client IDs, exact redirect URIs, documented scopes; secrets stored outside Git | Not configured |
| OAuth authorization | Real consent and token refresh tests for each provider | Not implemented |
| Provider adapters | Upload, list, download/read-back, checksum, pause, revoke, retry tests | Not implemented |
| Archive integration | Existing StoredBlob and ArchiveItem records use provider locations without changing IDs | Not implemented |
| Backup and restore | Portable export restored without the original provider account | Not verified |
| Operational release | Private deployment, encrypted secrets, monitoring, backup schedule, restore drill | Not operational |

A GitHub Actions success for the static Pages workflow is not evidence of cloud storage. Run `45120930170` is a GitHub Pages build/deployment run; it does not provision OneDrive, Google Drive, Yandex Disk, or a backend storage service. Storage implementation belongs in the backend and its deployment configuration, not in the Pages artifact.

## 12. Next implementation sequence

1. Implement a provider-neutral storage-location interface around the existing `StoredBlob` and archive intake. Preserve the current local adapter and all existing IDs.
2. Add provider connection records and encrypted token handling without committing secrets.
3. Implement and test Microsoft OneDrive, Google Drive, and Yandex Disk adapters one by one.
4. Add the account connection UI and per-provider pause/status controls.
5. Implement portable export and restore across providers.
6. Only then mark any provider as verified or operational.

No real family data is to be used in public development tests.

## 12. Supabase integration boundary

Supabase is being prepared as the private media-storage target for the web archive. The first integration is deliberately isolated from the existing Neon identity/database configuration.

- Browser configuration may contain only the project URL and public anon/publishable key. The service_role key must never be placed in GitHub Pages, JavaScript, HTML, or a browser field.
- The media bucket komarova_core_private must remain private. Row Level Security is required for both public.archive_items and storage.objects.
- The initial client policy is owner-scoped: an authenticated user can list and upload only objects under their own Supabase Auth user ID. Family-wide shared access requires a separately reviewed membership/role model.
- The first web release stores original files and metadata references only. It does not claim ClamAV scanning, AI enhancement, shared family permissions, full archive export, or verified off-site backup.
- Do not migrate the authoritative people/events/places registry or disable Neon Auth merely because a Supabase project exists. A database/auth migration requires a separately tested identity mapping, complete export, checksum comparison, restore test, and explicit approval.
- Supabase is considered connected only after project health, Auth login, private bucket verification, upload, authenticated read-back, SHA-256 comparison, and backup/restore checks pass.

