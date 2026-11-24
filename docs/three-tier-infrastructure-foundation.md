# KOMAROVA_CORE — three-tier infrastructure foundation

**Decision status:** approved by project owner, 24 November 2026  
**Implementation status:** architecture baseline; provider connections remain pending  
**Target branch:** `core-backend-foundation`

## 1. Approved infrastructure boundaries

KOMAROVA_CORE is organized into three independent infrastructure layers:

| Layer | Responsibility | Provider / current status |
|---|---|---|
| Application runtime | FastAPI, API, background workers, application configuration and operational logs | Simafri VPS application submitted; approval and provisioning pending |
| Authoritative registry | People, permanent PERSON-ID values, relationships, accounts, permissions, settings, audit history, file metadata and quota accounting | Neon PostgreSQL; production database configuration and migrations require verification |
| Family file storage | Private documents, photographs, selected mail attachments and family archive objects | Four individually authorized Google Drive accounts; OAuth/API integration not implemented |

GitHub Pages remains the public, static presentation layer. It is not the private application server, database, credential store or family file repository.

## 2. Google Drive capacity model

The planning ceiling is 4 accounts × up to 15 GB = up to 60 GB aggregate.

This is not one shared 60 GB bucket. Each Google account has its own independent quota, and Google's 15 GB allowance is shared across Gmail, Google Drive and Google Photos. Actual available Drive capacity must be read from each connected account and may be lower.

Rules:
- Each account owner connects their own Google account through Google's official OAuth consent flow.
- Do not request or store Google passwords, app passwords, browser cookies or manually pasted authorization codes.
- Keep OAuth access and refresh tokens server-side in a protected secret store or encrypted credential vault. Never put tokens in Git, static assets, browser storage, logs or issue comments.
- Default access is owner-only. Sharing requires an explicit grant, a named audience, narrow permissions and an audit event.
- The registry stores provider/account references, object metadata, ownership, permission grants, checksums and quota observations. File bytes remain in the corresponding owner's Drive.
- Do not promise a unified physical 60 GB pool. The UI must show per-account capacity and the combined observed total separately.
- Do not upload or migrate existing family files until a member has connected an account and approved the target folder and import action.

## 3. Neon registry responsibilities

Neon PostgreSQL remains the authoritative index for:
- stable PERSON-ID and other permanent entity identifiers;
- family members and typed relationships;
- account ownership, roles and access grants;
- Google Drive connection metadata (never plaintext OAuth secrets);
- file records, provider object references, checksums and provenance;
- per-account quota observations and application-level usage accounting;
- audit events for connect, disconnect, upload, share, download and delete actions.

Before changing the live schema, inspect the existing migrations and current database state. Create a reviewed migration, apply it to a test branch, run tests, and only then plan production rollout. Do not recreate or replace the existing database.

## 4. Simafri runtime responsibilities

The proposed Simafri VPS hosts the FastAPI application and background workers. The application must be deployable without placing family files on the VPS disk.

Simafri application status is **pending provider review**. A submitted request is not an awarded or provisioned server. Do not configure production deployment as successful until access, operating system, network, DNS, secrets, backups and health checks have been verified.

The VPS disk is for the operating system, application, dependencies, temporary processing, logs and operational headroom. It is not the family archive and must not be described as an additional 50 GB of Google-compatible storage.

## 5. Delivery sequence and gates

### Phase A — repository and database baseline
1. Verify the current branch, migrations, runtime entry point, configuration and automated tests.
2. Verify the Neon production and test branches without printing credentials.
3. Establish migration and backup/restore procedures.
4. Add provider-neutral storage account, object reference, permission and quota models only after schema review.

### Phase B — Google Drive pilot
1. Verify current official Google Drive API and OAuth requirements.
2. Create/configure a Google Cloud OAuth client only with the account owner's explicit action; do not invent credentials.
3. Connect one consenting adult account first, using the minimum scopes and a private test folder.
4. Implement account identity, quota readout and a harmless metadata/list test.
5. Implement upload/download/delete only after ownership checks, audit logging, duplicate handling and tests are in place.
6. Add the remaining family accounts individually after each owner consents.

### Phase C — runtime deployment
1. Wait for Simafri's decision and actual VPS provisioning.
2. Deploy the tested application to the VPS using server-side environment secrets.
3. Configure HTTPS, health checks, process supervision, logs and off-server backups.
4. Verify Neon connectivity and Google Drive API connectivity independently.
5. Publish the private application URL only after authentication and authorization tests pass.

## 6. Security and non-goals

- No paid plan, card entry, subscription or charge is authorized by this decision.
- Do not bypass provider billing or eligibility restrictions.
- Do not place private family data in public GitHub issues, README files or static Pages assets.
- Do not enable mailbox-wide synchronization or send mail as part of this storage milestone.
- Quarantined uploads remain inaccessible until a separately approved and tested file-verification/release workflow exists. No antivirus is being installed as part of this decision.
- Do not mark a provider as connected, a database as configured, or a service as deployed until a real authenticated check succeeds.
- Preserve the existing architecture and permanent identifiers. Avoid unrelated refactors.

## 7. Acceptance criteria

1. The public site contains no private family records or credentials.
2. Neon is the authoritative registry and migrations are reproducible.
3. Each Google Drive account is independently connected and revocable by its owner.
4. Per-account capacity is obtained from the provider; aggregate capacity is calculated from live observations, not assumed to be 60 GB available.
5. A user cannot list, read, modify or delete another account's files without an explicit access grant.
6. Every file operation is authorized server-side and audited.
7. Tokens and secrets never appear in Git, browser storage, client bundles, logs or public pages.
8. Simafri remains marked pending until a real VPS is provisioned and verified.
9. The application remains usable if Google Drive or one mailbox provider is unavailable.
10. No phase is marked complete without code, tests and successful verification evidence.
