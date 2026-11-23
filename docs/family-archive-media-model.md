# KOMAROVA_CORE — family archive and media data model

**Document status:** design specification, 23 November 2026  
**Scope:** private intake and preservation of photographs and other family media  
**Implementation status:** partial; authenticated photo/video quarantine intake and person links are implemented in the development backend, while the broader archive model remains unimplemented  
**Target branch:** `core-backend-foundation`

This document extends the approved product requirements and the approved private “Загрузка материалов” module. It does not replace the authoritative registry, existing PERSON-ID values, or the wider KOMAROVA_CORE architecture.

## 1. Purpose and boundaries

The family archive is a private domain service of KOMAROVA_CORE. It stores original media, descriptive metadata, relationships to people and events, derived previews, integrity evidence, and publication permissions.

The public GitHub Pages site is a separate presentation surface. It is not an upload destination, private archive, database, or binary storage service.

The first user-facing workflow is:

1. An authenticated user selects one or more photographs.
2. The system receives them into an isolated intake/quarantine area.
3. It validates the file and computes integrity metadata.
4. It creates a private preview without modifying the original.
5. The user links the photograph to one or more people and/or events.
6. A verified archive record is committed to the private registry and the original is moved to durable storage.
7. The photograph remains private unless a separate, explicit publication approval is recorded.

No automatic publication, public indexing, or automatic sharing is permitted.

## 2. Architectural invariants

1. **One authoritative registry.** Metadata and relationships live in the KOMAROVA_CORE database. Binary files may live in local or remote object storage behind a replaceable storage adapter.
2. **Permanent identity.** Every archive entity has a unique, never-recycled identifier. A real person keeps the same PERSON-ID.
3. **Immutable original.** Original bytes are never overwritten, recompressed, rotated, stripped of metadata, or “improved” in place.
4. **Separate derivatives.** A thumbnail, preview, restored image, crop, format conversion, or AI-edited result is a separate object with its own ID and provenance.
5. **Explicit relationships.** Links to people, events, places, documents, and sources are registry relationships, not filename conventions or folder names.
6. **Provenance.** Record source, uploader, ingest time, original filename, detected format, checksum, and any transformation/provider/version where applicable.
7. **Human confirmation.** Face recognition, OCR, inferred dates, location guesses, and AI descriptions are suggestions. They must not silently alter identity or family history.
8. **Private by default.** An archive record has no public URL. Public publication is a separate permissioned action.
9. **Idempotent intake.** Retrying an upload must not silently create duplicate archive entities.
10. **Portable preservation.** Export and restore must eventually include original media, derivatives selected by policy, manifests, checksums, metadata, and relationship data.

## 3. Logical data model

The following is the target logical model. It is not yet a database migration or a claim that these tables exist.

### 3.1 ArchiveItem

The common registry record for a preserved item.

| Field | Meaning |
|---|---|
| `archive_item_id` | Permanent ID, e.g. `AR-<32 uppercase hex>` |
| `item_type` | `photo`, `video`, `audio`, `document`, or another approved type |
| `title` | Optional human-readable title |
| `description` | Optional description; distinguish confirmed facts from suggestions |
| `record_status` | `intake`, `quarantined`, `verified`, `archived`, `rejected`, `archived_deleted` |
| `privacy_level` | Private by default; public status is not inferred from this field |
| `created_at`, `updated_at` | UTC timestamps |
| `created_by_user_id` | Authenticated uploader/creator |
| `source_id` | Optional link to an import source or connector record |

An ArchiveItem is the stable logical identity of the family material. A filename or storage key is not its identity.

### 3.2 PhotoAsset

Photo-specific metadata attached to an ArchiveItem whose type is `photo`.

| Field | Meaning |
|---|---|
| `photo_id` | Permanent PHOTO-ID, `PH-<32 uppercase hex>` |
| `archive_item_id` | Unique FK to ArchiveItem |
| `original_blob_id` | Link to the immutable original binary object |
| `captured_at` | Optional capture timestamp |
| `captured_at_precision` | `exact`, `day`, `month`, `year`, `approximate`, `unknown` |
| `date_source` | EXIF, supplied by user, document/source, or manually estimated |
| `camera_make_model` | Optional extracted metadata |
| `orientation` | Recorded orientation; original bytes remain unchanged |
| `width_px`, `height_px` | Detected dimensions |
| `color_profile` | Detected profile where available |
| `exif_metadata_status` | Whether metadata was read, absent, or unreadable |

A photo may show several people and may be linked to several events. Do not put a single `person_id` directly on PhotoAsset.

### 3.3 StoredBlob

Represents one immutable binary object in a configured storage provider.

| Field | Meaning |
|---|---|
| `blob_id` | Permanent blob ID |
| `sha256` | SHA-256 of the exact stored bytes |
| `size_bytes` | Exact byte length |
| `detected_mime_type` | Type detected from content, not trusted from the filename |
| `original_filename` | Supplied filename, retained as metadata |
| `storage_provider` | Adapter/provider key |
| `storage_object_key` | Opaque object key; never exposed as a public URL |
| `storage_state` | `quarantined`, `verified`, `available`, `missing`, `integrity_error` |
| `created_at`, `last_verified_at` | UTC timestamps |

Storage keys and physical paths may change during migration. Blob IDs, archive IDs, and checksums do not.

### 3.4 MediaDerivative

A preview or transformed version is a separate record and separate StoredBlob.

Required metadata:
- permanent derivative ID;
- parent ArchiveItem ID and source blob ID;
- derivative purpose: thumbnail, screen preview, restored image, crop, conversion, or other named operation;
- output blob ID and checksum;
- tool/provider name and version;
- transformation parameters or a stable reference to them;
- creator and creation time;
- whether the derivative was human-approved.

A derivative must never replace the original. If a derivative becomes the preferred display image, that is a presentation choice, not a change to the original.

### 3.5 EntityLink

A many-to-many relationship between an ArchiveItem and another registry entity.

| Field | Meaning |
|---|---|
| `link_id` | Permanent relationship ID |
| `archive_item_id` | Archive item |
| `target_entity_type` | `person`, `event`, `place`, `organization`, `document`, etc. |
| `target_entity_id` | Existing stable entity ID, such as PERSON-ID |
| `link_role` | For a person: `depicted`, `photographer`, `owner`, `mentioned`, or another controlled value |
| `confidence` | Optional confidence for an unconfirmed suggestion |
| `confirmation_status` | `suggested`, `confirmed`, `rejected` |
| `source_note` | How the link was established |
| `created_by_user_id`, `created_at` | Audit context |

An uncertain person identification must remain `suggested` until a human confirms it. A link to an event may be confirmed independently of the people shown.

### 3.6 UploadBatch and UploadItem

A batch groups one user action that selects multiple files.

- UploadBatch: permanent batch ID, uploader, creation time, status, idempotency key, and summary.
- UploadItem: permanent intake item ID, batch ID, original filename, received size, temporary blob reference, validation result, error code, and resulting ArchiveItem ID when committed.

A partial failure must not silently discard successful items or mark failed items as archived. Each file has an independently visible result.

### 3.7 PublicationApproval

Publication is not a boolean inferred from an archive status. It is a separate, explicit approval record.

Required fields:
- approval ID;
- ArchiveItem ID and exact approved derivative/blob version;
- target site or publication destination;
- approving user ID;
- approval timestamp;
- approval scope and any restrictions;
- status: `approved`, `revoked`, `expired`;
- publication and withdrawal audit references.

Approval of one image version does not automatically approve later edits or derivatives. Revocation must trigger a recorded withdrawal workflow for the corresponding public copy.

## 4. Identifier rules

- Existing PERSON-ID values are immutable and must remain valid.
- New PHOTO-ID values use `PH-` plus 32 uppercase hexadecimal characters (128 random bits).
- ArchiveItem, StoredBlob, derivative, link, batch, upload-item, and approval records each receive their own permanent ID with a distinct prefix.
- IDs are generated once, never recycled, and never derived from a person's name, filename, date, or storage path.
- A duplicate file does not receive a second logical photo record merely because it was uploaded again. The system records the duplicate intake attempt and links it to the existing object after confirmation.
- If two separately meaningful archive records refer to identical bytes (for example, two separately annotated source copies), preserve both logical records while allowing them to reference the same content-addressed blob where policy permits.

## 5. Intake lifecycle

`selected → receiving → quarantined → validating → preview_ready → awaiting_metadata → verified → archived`

Alternative terminal or recovery states:
- `rejected`: invalid, unsupported, corrupt, or disallowed file;
- `duplicate_review`: exact or probable duplicate needs resolution;
- `retry_required`: transient storage or processing failure;
- `cancelled`: user cancelled before commit.

Rules:
1. Upload to a non-public quarantine location first.
2. Enforce configured size/count limits and an allowlist of supported formats.
3. Detect file type from content; do not trust extension or browser MIME alone.
4. Reject path traversal, malformed files, decompression bombs, and unsupported payloads.
5. Compute SHA-256 while streaming; do not load unbounded files into memory.
6. Decode images in an isolated processing step before generating previews.
7. Preserve the original bytes exactly; preview generation works from a copy.
8. Check exact duplicates by checksum. Perceptual similarity may suggest a duplicate but must not auto-merge records.
9. Show preview and metadata to the user; allow correction of title, date, date precision, and links.
10. Commit the registry record and verified storage object as one recoverable workflow. If one side fails, retain a visible retry/reconciliation state rather than claiming success.
11. Record every state transition and failure in the audit trail.

## 6. User interface contract

Private section: **Загрузка материалов**.

Minimum screen flow:
1. authenticated entry;
2. button **Выбрать фотографии** (multi-select);
3. upload progress and per-file status;
4. preview grid with a full-size preview;
5. metadata fields: title, description, capture date and date precision;
6. person selector backed by the existing people registry;
7. event selector backed by the event registry;
8. confirmation summary;
9. **Сохранить в семейный архив** action;
10. final result with ArchiveItem ID, PHOTO-ID, and any validation/duplicate warnings.

The UI must not offer a public-post action in the same primary save flow. A separate publication workflow is outside the first upload release.

The interface must support keyboard navigation, clear errors, cancellation before commit, and retry without creating duplicate records.

## 7. Authorization and privacy

The existing account roles are owner, moderator, family_member, and guest. Every archive API route must have an explicit route-by-role rule and negative tests.

Minimum security requirements:
- no anonymous archive access;
- no access to private files through GitHub Pages or guessable storage URLs;
- authorize every preview, download, metadata read, update, and delete request server-side;
- use short-lived or proxied download access where object storage requires signed URLs;
- revoke access when a user is disabled or a session is revoked;
- keep secrets, real family files, and production database copies out of Git;
- do not expose EXIF GPS coordinates or sensitive metadata in public previews;
- record who viewed, uploaded, changed, approved, revoked, exported, or deleted an item where appropriate.

The exact write permissions for each family role must be locked in the API authorization matrix before endpoints are implemented. Until then, implementation must use the most restrictive rule and must not infer public access from a family role.

## 8. Storage and preservation

- Provide a storage adapter interface; do not bind the domain model to a single vendor.
- Store originals outside the public web root and outside the Git repository.
- Use opaque storage keys and a database mapping from Blob ID to provider/key.
- Keep at least one independent backup of original media, separate from the primary storage failure domain.
- Periodically verify checksums and record verification results.
- Include media objects in the future portable archive format with a manifest linking each blob to its IDs, checksum, size, MIME type, metadata, and relationships.
- Restore must verify all checksums and foreign-key/relationship references before declaring the archive restored.
- A missing object must be reported as missing; never silently substitute a preview for an original.

Current archive format v1 is database-only. A future media-inclusive archive format must be versioned separately and must remain backward compatible with v1 database archives.

## 9. API contract outline

Names below are proposed route shapes, not implemented endpoints.

- `POST /api/v1/archive/uploads` — create an upload batch.
- `POST /api/v1/archive/uploads/{batch_id}/items` — receive file content.
- `GET /api/v1/archive/uploads/{batch_id}` — retrieve batch and per-file states.
- `POST /api/v1/archive/uploads/{batch_id}/commit` — commit verified items and metadata.
- `GET /api/v1/archive/items` — list authorized archive records.
- `GET /api/v1/archive/items/{archive_item_id}` — retrieve metadata and links.
- `GET /api/v1/archive/items/{archive_item_id}/preview` — authorized preview.
- `GET /api/v1/archive/items/{archive_item_id}/original` — authorized original download.
- `POST /api/v1/archive/items/{archive_item_id}/links` — add a confirmed or suggested entity link.

All write operations require authentication, authorization, input validation, audit logging, and an idempotency strategy. Exact route names may change during implementation without changing the logical model.

## 10. Acceptance tests

The first verified release must demonstrate at least:

1. An authenticated user can select and upload multiple supported photographs.
2. An unauthenticated user cannot upload, list, preview, or download archive content.
3. A user without the required role cannot perform a write or read operation.
4. Unsupported, corrupt, oversized, malformed, and mismatched-extension files are rejected safely.
5. The stored original checksum equals the checksum computed at intake.
6. Preview generation does not modify original bytes.
7. Exact duplicate upload is detected and does not silently create a duplicate logical photo.
8. A probable visual duplicate is flagged for human review, not auto-merged.
9. A photo can link to multiple existing PERSON-ID records and multiple events.
10. A nonexistent person/event ID is rejected without partial commit.
11. An uncertain identification remains suggested until a user confirms it.
12. A failed storage write leaves a recoverable failed/retry state and no false “archived” success.
13. Every successful upload and metadata change creates an audit event.
14. No upload appears on the public website or in the Git repository.
15. No public URL exists without a separate PublicationApproval.
16. Revoking publication approval records the action and initiates withdrawal of the approved public copy.
17. Export/restore tests eventually include original media and verify every checksum; until then the system must clearly label v1 exports as database-only.

## 11. Delivery sequence

1. Approve the logical model and the role matrix.
2. Define storage adapter contract and quarantine/verified storage behavior.
3. Add forward-only database migration for archive metadata and links.
4. Implement file validation, checksum, duplicate detection, and preview generation.
5. Implement authenticated API and role-by-route tests.
6. Implement private upload UI and end-to-end tests.
7. Add media-inclusive export/restore and integrity verification.
8. Only after the private workflow is verified, design a separate publication/withdrawal workflow.

Do not implement social-network synchronization, AI face identification, bulk publication, or video editing as part of the first photo-upload release.

## 12. Current status

- Approved concept: private “Загрузка материалов” section with photo selection, preview, links to people/events, and no automatic publication.
- This document: detailed target data model and acceptance contract.
- Existing backend: people registry, account roles/sessions, audit foundation, migrations, and database-only archive v1 exist on the development branch.
- Not implemented: archive/media tables, binary storage adapter, photo intake, validation pipeline, previews, photo/event links, private upload UI, media-inclusive export/restore, and publication approvals.

A successful GitHub Pages workflow verifies the public-site build/deployment only. It does not verify any of the private archive capabilities above.


## 14. Implemented development slice: private intake (23 November 2026)

The current backend implements a deliberately narrow subset of this model:

| Model element | Development implementation | Boundary |
|---|---|---|
| StoredBlob | `stored_blobs` | SHA-256, byte size, detected MIME, original filename, provider key, quarantine state |
| ArchiveItem | `archive_items` | Permanent ARCHIVE-ID, photo/video type, title, uploader and quarantine state |
| EntityLink | `archive_entity_links` | Confirmed links to existing PERSON-ID only |
| UploadBatch / UploadItem | Not implemented | Multi-file transactional batch and per-file retry states remain future work |
| MediaDerivative | Not implemented | No thumbnails, transcoding or AI-generated derivatives |
| PublicationApproval | Not implemented | No public publishing or public media URL |

The private API accepts photo/video uploads only. It streams the request into a private local quarantine area, validates a basic signature allowlist, computes SHA-256, rejects exact duplicate bytes, and commits the registry metadata with an audit event. The original is not transformed. The API returns metadata, never a filesystem path or storage object key.

All received files remain quarantined because antivirus/malware scanning and isolated media processing are not yet configured. No preview, playback, download, public publication or automatic archive promotion is provided by this backend slice. A successful HTTP upload means only that the file was received into private quarantine and registered, not that it passed a security scan or became a preserved archive master.

The current local filesystem adapter is a development adapter. Configure `CORE_MEDIA_ROOT` to a private persistent volume outside the repository. Do not use ephemeral container storage for family records. A future object-storage adapter must preserve the same blob IDs, checksums, immutable-original rules and authorization contract.

The separate legacy `komarova_file_engine.py` uses an independent SQLite schema and is not an adapter for the backend database. It must not be pointed at the backend database or used as an alternative registry.
