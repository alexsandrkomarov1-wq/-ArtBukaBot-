# KOMAROVA_CORE — product requirements register

**Document status:** approved product scope captured from the project decisions, 23 November 2026  
**Implementation status:** requirements baseline; this document does not claim that the listed capabilities exist.

## 1. Product purpose

KOMAROVA_CORE is one family information environment: a durable family archive, identity and relationship registry, chronology, places and journeys workspace, knowledge base, media studio, and AI-assisted interface.

It must serve both present-day family communication and long-term preservation. Future generations must be able to recover and understand the archive even if this application, its hosting provider, current AI models, social networks, or storage vendors disappear.

The system is not eight separate websites. It is one product with a shared identity model, authoritative registry, permissions, audit trail, storage references, and modular domain services.

## 2. Non-negotiable architecture rules

1. One logical core and authoritative registry; physical storage may be distributed.
2. Every entity has a permanent, non-recycled identifier. A real person has one stable PERSON-ID across names, devices, accounts, and storage locations.
3. Existing identifiers and source records are never silently rewritten or discarded. ID upgrades use forward migrations and compatibility tests.
4. Originals are immutable. Previews, edited images, enhanced photographs, video edits, transcripts, OCR, and AI-generated descriptions are separate derived objects with provenance.
5. Every imported or generated record records source, time, tool/provider and version where available, transformations, and integrity metadata.
6. AI output is an assertion or derivative, not unquestionable fact. Human confirmation is required for uncertain identities, relationships, historical claims, and conflict resolution.
7. Integrations are replaceable adapters. No social network, cloud, map vendor, AI model, or media editor is the sole source of truth.
8. Private family data and credentials must never be committed to a public repository.
9. Synchronization must be idempotent, auditable, and conflict-safe. Ambiguous conflicts require human review.
10. A feature is not complete until its acceptance criteria and automated/manual verification are recorded.

## 3. Product domains

| Domain | Scope | Initial acceptance outcome | Current status |
|---|---|---|---|
| CORE — identity and registry | People, permanent IDs, aliases, duplicate resolution, organizations, objects, entity links | One person can be found through known names/aliases and remains the same entity after edits/imports | Partial |
| FAMILY_ARCHIVE | Documents, letters, correspondence, photographs, video, audio, publications, source files | Upload, classify, link to people/events, preview, download/export, checksum and preserve original | Partial |
| FAMILY_TIMELINE | Life stories, family events, dates, generations, biographies | Events can be entered, sourced, linked to people and displayed chronologically | Not implemented |
| FAMILY_PLACES | Places, walks, trips, routes, maps, photo galleries and captions | Create a walk/journey without programming; display ordered map points, route, photos and narrative | Not implemented |
| AI_ASSISTANT | Conversational assistant, logical step-by-step analysis, web research, archive search, image understanding, OCR and transcription | Answers distinguish archive facts, external sources, inference and uncertainty; citations/provenance are retained | Not implemented |
| MEDIA_STUDIO | Photo restoration/enhancement, video editing/enhancement, captions, albums and publications | Produce separate derivatives while preserving originals and recording tools/settings | Not implemented |
| KNOWLEDGE_BASE | Family knowledge, place histories, historical context, reference sources and research notes | A story about a person/place can be stored with sources and linked to archive records | Not implemented |
| SYNC_AND_STORAGE | Local/cloud/distributed storage, imports/exports, synchronization, backups and recovery | Data can be exported, verified, restored and synchronized without silent loss | Not implemented |

Cross-cutting domains retained from the approved architecture: calendar/tasks; analytics/reports; users/access; administration/audit; external connectors; web/mobile clients. These are shared capabilities, not discarded or replaced by the eight product domains above.

## 4. Functional requirements

### Identity and family graph
- REQ-CORE-001: Create and retrieve people with permanent PERSON-ID.
- REQ-CORE-002: Support names, aliases, dates, notes, source references and duplicate candidates.
- REQ-CORE-003: Link people using typed relationships with provenance and reviewable history.
- REQ-CORE-004: Preserve old IDs and references through every migration and merge.

### Archive and preservation
- REQ-ARC-006: Provide a browser-based photo viewer and native video playback interface for supported local or archived media.
- REQ-ARC-007: Support album sequence playback, slideshow, fullscreen viewing, keyboard navigation and download of an authorized original/derivative.
- REQ-ARC-008: Clearly distinguish browser-local preview from persistent server upload; never imply a selected local file has entered the family archive without a verified upload transaction.
- REQ-ARC-009: Detect and report unsupported media codecs/formats; do not promise MKV, HEVC or 4K playback solely from a filename.
- REQ-ARC-001: Ingest documents and media without altering original bytes.
- REQ-ARC-002: Store metadata, checksum, detected format, source, ingest time and object ID.
- REQ-ARC-003: Link archive objects to people, events, places, organizations and other sources.
- REQ-ARC-004: Export a portable preservation package with manifest, checksums, schema description and human-readable metadata.
- REQ-ARC-005: Verify integrity and report missing, changed or unreadable objects.

### Timeline and places
- REQ-TIME-001: Create sourced events with date precision/uncertainty and links to participants.
- REQ-PLACE-001: Create a walk or trip through a no-code editor.
- REQ-PLACE-002: Attach ordered places, routes, map coordinates, photographs, captions and narrative.
- REQ-PLACE-003: Support a place-based story using the place name or photographs, with source links and uncertainty labels.

### AI and research
- REQ-AI-001: Support pluggable AI providers/models; the core must not depend on one vendor or model.
- REQ-AI-002: Search the family archive and distinguish retrieved facts from model inference.
- REQ-AI-003: Support web research with source links, publication dates and claim-level citations.
- REQ-AI-004: Analyze supplied images: zoom/crop/rotate, OCR, visual description and comparison where supported.
- REQ-AI-005: Mark uncertain recognition and require confirmation before changing identity or relationship records.
- REQ-AI-006: Preserve prompts/outputs or a suitable audit record according to privacy settings and retention policy.

### Media studio
- REQ-MEDIA-001: Support photo enhancement/restoration through replaceable adapters or user-assisted workflows.
- REQ-MEDIA-002: Support video editing/enhancement workflows, including stabilization, resolution conversion, trimming, captions and music where licensing permits.
- REQ-MEDIA-003: Preserve source media; every derivative has its own ID, checksum, tool/version and transformation record.
- REQ-MEDIA-004: Do not claim a provider integration exists until API access, licensing, cost, privacy and technical feasibility have been verified.

### Connectors and clients
- REQ-CONN-001: Design optional connectors for Telegram, Facebook, WhatsApp, YouTube, VK, VK Video, Odnoklassniki, Yandex Zen and other approved sources.
- REQ-CONN-002: Check each provider's current API, permissions, export options, OAuth requirements and terms before implementation.
- REQ-CONN-003: Store provider identifiers and provenance while retaining the internal entity ID as authoritative.
- REQ-CLIENT-001: Deliver a connected responsive web application before treating the static GitHub Pages shell as a usable product.
- REQ-CLIENT-002: Plan Windows, Android and iOS access against the same identity, permission and API model.

### Security, sync and operations
- REQ-SEC-001: Maintain a route-by-role authorization matrix for owner, moderator, family_member and guest.
- REQ-SEC-002: Test account disable, role change, session revocation, bootstrap races, login throttling and recovery.
- REQ-SYNC-001: Use stable operation IDs, idempotent writes, tombstones and explicit conflict records.
- REQ-OPS-001: Provide encrypted independent backups, integrity verification and tested restore procedures.
- REQ-OPS-002: Provide deployment, monitoring, incident response and disaster recovery runbooks.

## 5. Provider choices and integration status

The initial family archive storage provider set is approved:
- Microsoft OneDrive (`microsoft_onedrive`);
- Google Drive (`google_drive`);
- Yandex Disk (`yandex_disk`);
- private local storage adapter (`local_private`) for development and controlled staging.

These are approved provider targets, not claims of live account connections. OAuth app registrations, credentials, provider adapters, transfer verification, and restore tests remain outstanding. Mail services (Microsoft mail, Gmail, Yandex Mail) are separate connectors and are not binary storage providers.

Other provider examples named during product planning:
- AI: GPT-4o, o3, Claude and successor models.
- Photo: Topaz Photo AI, Luminar Neo, Remini.
- Video: CapCut, Topaz Video AI, Runway.
- Maps and social networks: select after API, privacy, export, availability and cost review.

Storage requirements and the provider lifecycle are specified in `docs/storage-provider-configuration.md`. The architecture must allow a provider to be replaced without changing the authoritative registry or rewriting family data. Where no supported API exists, provide a documented manual import/export path rather than pretending full synchronization is available.

## 6. Delivery gates and status vocabulary

Use only these statuses:

- **Planned:** accepted requirement, no design or implementation yet.
- **Designed:** interfaces, data model, dependencies and failure cases documented.
- **Approved:** design accepted for implementation.
- **Implemented:** code exists, but may not yet be verified.
- **Verified:** acceptance tests and relevant security/integration checks pass.
- **Operational:** deployed in the intended environment, monitored, backed up and recoverable.

A green unit-test run does not make a feature operational. A mock connector does not count as a live integration. A static page does not count as a connected application.

## 7. Implementation order and release gates

1. **Foundation safety:** 128-bit identifiers for new entities with compatibility for existing PERSON-IDs; complete migration tests; PostgreSQL compatibility; authorization and concurrency test coverage; complete backup/restore round-trip.
2. **Usable application:** connected responsive frontend, authentication/session lifecycle, people registry, relationship management, audit and administrator workflows.
3. **Family archive:** binary storage abstraction, immutable originals, metadata, checksums, upload/download, portable export and restore.
4. **Timeline and places:** sourced events, family chronology, no-code walk/trip editor, maps and galleries.
5. **Knowledge and AI:** archive search, source-backed research, image analysis/OCR, assistant with uncertainty and human confirmation.
6. **Media studio:** controlled photo/video derivative workflows and verified provider adapters.
7. **Connectors and sync:** provider-by-provider permission review, import/export, idempotent synchronization and conflict handling.
8. **Operational release:** private hosting, encrypted off-site backups, monitoring, restore drills, security review and documented recovery.

Do not expose real family data until the security, storage, backup and deployment gates are met. Do not merge this foundation branch into main merely because documentation or tests pass.

## 8. Definition of done for every requirement

Each requirement must have:
- a unique stable requirement ID;
- an owner/domain and dependencies;
- a documented data/API/UI contract where applicable;
- positive, negative and failure-path acceptance tests;
- authorization and privacy checks;
- migration and backward-compatibility checks where data changes;
- a verified status and evidence (commit, CI run, test result or operational check);
- known limitations and recovery behavior.

This register is the product baseline. New requests are added as new requirements or explicit amendments; existing requirements are not silently removed.


## 9. Media viewer first delivery slice (23 November 2026)

The first browser-facing media viewer is intentionally local-only. It allows a visitor to select photo/video files from the current device, preview images, play browser-supported video, move between selected files, run a photo slideshow, enter fullscreen and download the selected local file. Object URLs are released when the page is closed or the selection is replaced.

This slice is not a persistent family archive. It does not upload files, store shared albums, synchronize devices, generate AI descriptions, attach PERSON-ID/EVENT-ID/PLACE-ID, create ZIP exports, or provide private access control. Those capabilities remain gated on authenticated private hosting, object storage, immutable originals, metadata registry and audit trail.


## 10. Private media intake backend slice (23 November 2026)

The first private media API slice adds authenticated photo/video intake to a local private quarantine directory and registers metadata in the same SQLAlchemy database as people and accounts. It is not a production archive release.

Implemented in code on the feature branch:
- Alembic revision `0005_private_media_intake` adds `stored_blobs`, `archive_items` and `archive_entity_links` without rewriting existing PERSON-ID values.
- `POST /api/v1/archive/items` streams uploads in 1 MiB chunks, enforces a 100 MiB limit, checks an allowlisted extension against basic file signatures, calculates SHA-256 and registers the exact original bytes.
- Exact duplicate content is rejected with HTTP 409 and the existing archive item ID; a second item is not silently created.
- Original bytes are stored under a private, non-public local quarantine root configured by `CORE_MEDIA_ROOT`. Storage paths and object keys are not returned by the API.
- `GET /api/v1/archive/items` and `GET /api/v1/archive/items/{ARCHIVE-ID}` return private metadata only.
- `POST /api/v1/archive/items/{ARCHIVE-ID}/links` and the matching GET route support confirmed links to existing active PERSON-ID records. Event and place links are not enabled because those registries do not yet exist in the backend.
- Upload and person-link actions write audit events. Owner, moderator and family_member may upload/link; guest is read-only.

Explicit limitations:
- New uploads remain `quarantined`. Malware scanning, isolated media decoding, thumbnail generation, safe preview, download/stream endpoints, retention/reconciliation jobs, cloud object-storage adapters and production deployment are not implemented.
- No upload is available from the public GitHub Pages site. No real family media should be sent to this development API.
- Local filesystem persistence depends on a separately configured durable private volume. A container's ephemeral disk is not a family archive.
- The separate legacy `komarova_file_engine.py` is not wired into this API; it targets a different SQLite schema and must not be pointed at the backend database.
- Passing CI does not make this service operational. Production use still requires a private host, persistent storage, malware scanning, backup/restore of binary objects, security review and an end-to-end upload/restore drill.

Requirement status remains partial until the above controls and operational gates are verified.


### New acceptance requirements
- REQ-ARC-010: Detect actual media type and codec/container metadata independently of filename extension; preserve original filename as provenance.
- REQ-ARC-011: Apply EXIF orientation and video display-matrix rotation to separately stored derivatives after malware scanning; never modify originals.
- REQ-ARC-012: Create browser-compatible image/video derivatives with verified output metadata and separate checksums.
- REQ-CLIENT-003: Provide contextual page-aware navigation hints and accessible popovers without exposing private records.
- REQ-AI-007: Provide a provider-neutral conversational site assistant only through a protected backend; distinguish verified system facts from guidance and model inference.
