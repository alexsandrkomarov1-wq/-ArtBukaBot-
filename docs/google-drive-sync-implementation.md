# KOMAROVA_CORE — Google Drive automatic replication

**Target branch:** `core-backend-foundation`  
**Provider status:** temporary parallel copy only; not the authoritative archive  
**Implementation status:** backend adapter, transactional queue, retry worker and verification code added; deployment and live Drive authorization are still pending

## 1. Required behavior

Google Drive is a secondary replica of the private archive, not the primary registry and not a replacement for the current archive storage.

When a new original or derivative is committed to the archive, the backend must enqueue a replication job for Google Drive. The upload must run server-side. The browser must never receive OAuth refresh tokens or client secrets.

The replication flow is:

1. The existing archive intake validates the file, computes SHA-256, creates the immutable StoredBlob and Material records, and commits the primary archive copy.
2. In the same database transaction, create an outbox job containing the blob ID, SHA-256, byte size, MIME type, and source object key. Do not put personal names or local filesystem paths in the job.
3. A background worker claims pending jobs with a lease, streams the primary object to Google Drive, and writes it into the private `KOMAROVA_CORE` application folder.
4. The worker reads the uploaded object back (or downloads it) and verifies exact byte size and SHA-256.
5. On success, persist the Drive file ID, provider key, checksum, verification timestamp, and `available` state against the same Blob ID. Do not create a second ArchiveItem or Material.
6. On timeout, quota error, expired/revoked consent, or checksum mismatch, retain the primary archive copy, record a retryable/error state, and retry with bounded exponential backoff. Never mark the archive upload as successful merely because the Drive request was accepted.
7. A repeated job must be idempotent: find the existing Drive replica by stored file ID or app metadata and verify it instead of creating another copy.
8. A failed or paused Drive replica must not block viewing or using a verified primary archive copy. Disconnecting Drive must not delete primary objects or registry rows.

Originals remain immutable. An enhanced derivative is replicated as its own Blob ID and retains its existing `original_material_id` relationship.

## 2. Folder authorization

The target folder must be the private `KOMAROVA_CORE` folder in the owner's Google Drive.

The current local OAuth token was authorized with the `drive.file` scope. That scope does not grant general listing access to arbitrary folders created manually outside the OAuth application. Therefore, an empty API search result is not proof that the user's folder is absent.

Do not broaden OAuth scopes or overwrite the user's current token as a workaround. The folder must be explicitly granted to the application through a supported Google Picker flow, or the application must create/select an app-managed folder after the owner approves that behavior. Persist the selected folder ID server-side.

## 3. Server-side configuration

The deployed private backend will require these environment variables, provisioned only through the hosting provider's secret settings:

- `GOOGLE_DRIVE_SYNC_ENABLED=true`
- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `GOOGLE_DRIVE_REFRESH_TOKEN`
- `GOOGLE_DRIVE_FOLDER_ID`

Never put these values in Git, GitHub Pages, frontend JavaScript, public build artifacts, logs, or chat messages. The local files `client_secret.json` and `google_drive_token.json` must remain outside the repository. A local desktop token is not automatically available to the deployed website backend.

The worker must use least-privilege OAuth, refresh access tokens server-side, redact credentials from errors, and support pause/revoke without deleting remote data.

## 4. Required persistence

Implement a provider replica table keyed by a stable location ID, with a unique constraint on (blob_id, provider). It must record:

- Blob ID and provider key (`google_drive`);
- remote Drive file ID and selected folder ID;
- expected SHA-256 and byte size;
- state: `pending`, `uploading`, `available`, `retryable_error`, `integrity_error`, `paused`, or `revoked`;
- attempt count, next retry time, last error code (sanitized), last successful verification time;
- created/updated timestamps.

Add a transactional outbox table for jobs so a process restart cannot lose a replication request after the primary archive transaction commits. The worker must use row locking/leases so multiple workers cannot upload the same job concurrently.

## 5. User-visible status

The private archive UI must show Google Drive separately from primary storage:

- `Ожидает синхронизации`
- `Синхронизируется`
- `Сохранено и проверено`
- `Ошибка, повтор будет выполнен`
- `Приостановлено`
- `Доступ отозван`

Do not show a generic cloud-success badge until Drive read-back and SHA-256 verification have passed. Show the last verified timestamp and allow an owner to pause/resume replication and request a retry.

## 6. Acceptance tests before enabling

1. OAuth consent and refresh succeed on the deployed backend.
2. The authorized folder ID resolves to the owner's intended private folder.
3. A synthetic test file uploads and reads back with matching size and SHA-256.
4. A second run is idempotent and does not create a duplicate.
5. A transient API failure leaves the primary archive copy intact and schedules a retry.
6. Expired/revoked OAuth is reported without exposing credentials.
7. A derivative is replicated separately while preserving its original Material relationship.
8. Pause and resume work without deleting remote or primary objects.
9. A deployment restart does not lose pending outbox jobs.
10. No Google Drive credentials or personal media appear in the Git repository or public Pages bundle.

## 7. Implemented in the working branch

The backend now contains:

- GoogleDriveReplica and GoogleDriveOutbox SQLAlchemy models plus migration 0009_google_drive_replication;
- a post-ClamAV hook that writes an outbox job only after an original passes malware scanning, plus a derivative hook after its own malware scan; both jobs are committed in the same transaction as their verified material records;
- a server-side worker started with `python -m backend.app.google_drive_sync`, polling every 10 seconds;
- resumable Drive upload, application metadata for idempotency, read-back download and SHA-256/size verification;
- bounded exponential retry, sanitized error codes and expired-lease recovery.

The worker is disabled unless GOOGLE_DRIVE_SYNC_ENABLED=true and GOOGLE_DRIVE_FOLDER_ID are configured. Required hosting secrets are GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET and GOOGLE_DRIVE_REFRESH_TOKEN. Keep them in the private backend host's secret settings, never in Git or the browser. The local token file is not automatically available to the hosted backend.

The worker does not create a folder. It uses only the explicitly configured folder ID. With the current drive.file scope, a manually created folder may still be inaccessible until the owner selects/shares it through an approved Google Picker flow. Do not widen the OAuth scope or create a duplicate folder to bypass this.

## 8. Remaining deployment and acceptance gates

- Apply migration 0009_google_drive_replication to the intended backend database only after the deployment target is confirmed.
- Configure the five secrets above in the private backend host.
- Confirm the existing KOMAROVA_CORE folder is authorized to the OAuth app without creating a second folder.
- Start the worker as a private background process and verify a synthetic test file uploads, downloads back, and matches SHA-256.
- Verify duplicate retry, transient failure retry, restart recovery and pause behavior before calling synchronization operational.

## 9. Operational status

The code path is implemented in the working branch, but automatic synchronization is not active until the database migration is applied, the private backend worker is deployed, the five server-side settings are configured, and the existing folder is authorized. No upload to the owner's Drive has been performed by this implementation yet.
