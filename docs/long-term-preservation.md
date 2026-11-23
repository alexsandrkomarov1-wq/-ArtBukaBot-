# KOMAROVA_CORE: long-term preservation and survivability

Status: architecture requirements and gap assessment, 23 November 2026.
This document is a design control, not a claim that the current application is durable or production-ready.

## 1. The honest answer about centuries

No website, database, storage provider, company, programming language, or cryptographic algorithm can be promised to work forever. A system can, however, be designed so that its information can be recovered and migrated by future people after the current application, vendor, server, or database has disappeared.

The long-term asset is the family archive and its documented meaning, not the current website code. The application is replaceable. The data, identity links, provenance, and preservation instructions must remain understandable without it.

The target is **recoverable, verifiable, portable, and migratable**, not technically immortal.

## 2. Preserve the approved KOMAROVA_CORE model

The following approved concepts remain architectural invariants:

- One logical family information core and one authoritative registry, even when physical files are stored in several locations.
- Permanent PERSON-ID values that do not change when a person's name, device, account, or storage location changes.
- Distinct records for people, relationships, documents, correspondence, photographs, events, sources, organizations, and other entities.
- Explicit links between records rather than relying on filenames or folder paths as identity.
- Modular domains and connectors. A social network, cloud provider, or website must never become the only copy or authoritative source of family information.
- Role-based access, audit history, controlled synchronization, and human confirmation for ambiguous conflicts.
- Versioned schemas and forward migrations. Existing identifiers and source records must not be silently rewritten or discarded.

These principles are preserved; implementation details may be replaced as technology changes.

### Approved domain implementation status

The conceptual architecture is broader than the current backend. The following status prevents a design decision from being mistaken for a finished feature:

| Approved domain | Current implementation status |
|---|---|
| Identity and people | Partial: person records and stable-in-record IDs exist; aliases, duplicate resolution, merge history, and external identities are not implemented. |
| Family and social relationships | Partial: basic directed relationship records exist; typed relationship governance and richer social graph rules remain. |
| Documents and sources | Not implemented. |
| Events and chronology | Not implemented. |
| Calendar and tasks | Not implemented. |
| Notes and knowledge base | Not implemented. |
| Analytics and reports | Not implemented. |
| Users and access | Partial: four roles, sessions, password change, bootstrap, audit events, and role controls exist; recovery, succession, MFA, and independent security review remain. |
| Storage and synchronization | Not implemented as a production capability. |
| Administration and audit | Partial: audit records and migrations exist; tamper evidence, retention, monitoring, and operational controls remain. |
| External connectors | Not implemented. |
| Web/mobile clients | Not implemented as connected clients. The GitHub Pages Jekyll site remains a static shell, not the family application. |

No module should be marked "implemented" merely because its name appears in the approved architecture or its future interface has been discussed.

## 3. Critical gaps found in the current foundation

| Area | Current state | Required before real family data |
|---|---|---|
| Person identity | PERSON-ID is currently `P-` plus 12 hexadecimal characters (48 random bits) | Move new identifiers to at least 128-bit globally unique IDs. Preserve all existing IDs and provide an explicit compatibility migration. Never recycle IDs. |
| Database | SQLite is the development default; its file path can depend on the process working directory | Use an explicitly configured production database URL, managed migrations, documented restore, and a tested PostgreSQL deployment path. |
| Attachments | No durable binary-object repository is implemented | Add a storage abstraction and content-addressed object store. Keep original bytes immutable; store previews and converted derivatives separately. |
| Integrity | Database audit events exist, but there is no archive-wide checksum inventory | Create SHA-256 manifests at ingest, periodically verify every stored object, retain verification logs, and repair from a known-good independent copy. |
| Backups | SQLite online backup and restore helper has a separate-database test | Add scheduled encrypted off-site copies, immutable/offline retention, backup manifests, restore drills, and recovery-point/recovery-time objectives. |
| Encryption | No verified encryption-at-rest or key recovery process | Encrypt devices, disks, backups, and object storage. Document key rotation, offline recovery material, and succession access. |
| Audit | Audit rows are application-written but not tamper-evident against a database administrator | Add append-only controls and tamper-evident chained or signed audit exports, with independent copies. |
| Concurrency | Database lock row serializes bootstrap and account administration | Keep concurrency tests on every supported database. The current single lock row is safe-oriented but can become a throughput bottleneck. |
| Authorization | Four-role API matrix tests are being expanded | Maintain a route-by-role matrix for every new endpoint, including negative tests and tests after role/status changes. |
| Synchronization | No production sync engine | Add idempotent operation IDs, explicit conflict records, tombstones, version vectors or equivalent causal metadata, and replay tests. Never silently overwrite conflicting family records. |
| External services | No production social/cloud connectors | Treat connectors as optional imports/exports. Store provider IDs and provenance, not provider dependencies. Re-authorize and re-check permissions after API changes. |
| Operations | No production deployment, monitoring, alerting, or independent security review | Add operational runbooks, health/backup/integrity alerts, dependency and vulnerability review, disaster-recovery exercises, and independent penetration testing. |

### Identifier warning

The present 48-bit PERSON-ID generator is acceptable only as a temporary development implementation. It is not the right long-horizon choice for a growing registry that may contain many millions of entities over generations. The upgrade must be done before production use, with existing IDs retained exactly. A new 128-bit identifier format should be introduced by a forward migration and tested against all foreign keys, audit records, imports, exports, and old references.

## 4. Preservation architecture

### 4.1 Separate the archive from the application

- Relational database: authoritative structured metadata, identifiers, relationships, permissions, event indexes, and references to stored objects.
- Object storage: original documents, photographs, video, audio, exports, and other binary content.
- Preservation package: a portable directory or archive containing content, a manifest, checksums, metadata, and a versioned schema description.
- Application: one replaceable way to view and edit the archive.

A future maintainer must be able to recover the archive without running KOMAROVA_CORE.

### 4.2 Multiple copies and different failure domains

Adopt a 3-2-1-1-0 style policy as an operational target:

- at least three complete copies;
- at least two different storage types or independently managed systems;
- at least one geographically separate copy;
- at least one offline or immutable copy;
- zero unresolved integrity errors after verification and restore testing.

Do not count two folders on one disk, two accounts at one provider, or two replicas in one data centre as independent disaster copies.

### 4.3 Integrity and provenance

For every ingested object, preserve:
- permanent object ID;
- original filename and source location as metadata, not identity;
- ingest time and source/provenance;
- media type, size, and detected format;
- SHA-256 checksum;
- relationships to people, events, documents, and other objects;
- every migration, conversion, or repair as a logged event.

Never replace an original with a converted file. Keep the original and create a separately identified derivative with its own checksum and conversion record.

### 4.4 File formats and future migrations

Prefer documented, widely implemented, open formats where practical. Maintain an inventory of formats actually present. Do not assume any format is immortal. When a format becomes difficult to read, create a verified derivative while retaining the original, tool/version details, validation results, and before/after checksums.

Structured data must have documented exports (for example JSON, CSV, and SQL dumps where appropriate), with a versioned schema and human-readable data dictionary. Avoid making proprietary application state the only representation of a record.

### 4.5 Synchronization and conflict safety

Every replicated write should have a stable operation ID and origin. Retries must be idempotent. Deletions should be represented by durable tombstones until all replicas have acknowledged them. Conflicts must retain both candidates, their authors, timestamps, and provenance until an authorized person resolves them. Clock time alone must not decide which family fact is true.

### 4.6 Security and succession

The archive needs more than one recoverable path to administration. Define owner succession, emergency access, account recovery, key recovery, and revocation. Keep recovery material outside the primary server and outside the same cloud account. Record who is authorized to act and how that authority can be transferred. Do not put secrets, personal records, private keys, or family attachments in the public source repository.

## 5. Operational preservation schedule

Proposed baseline once the production archive exists:

- On every ingest: checksum, format detection, metadata capture, malware scan where appropriate, and verification of the stored copy.
- Daily: database and object-store backup according to change volume; verify that backup jobs completed.
- Monthly: automated checksum sampling or full verification according to archive size; inspect failures.
- Quarterly: restore a representative backup into an isolated environment and test application-independent export.
- Annually: full disaster-recovery exercise, key-recovery exercise, owner succession review, dependency/security review, and storage inventory.
- Every 2-3 years: review media health, storage vendors, file-format risks, export readability, and migration needs.
- At every major schema release: test upgrade from the previous supported schema, export/import round trip, rollback or recovery strategy, and preservation of all stable identifiers.

The schedule must be automated where possible and documented so another person can continue it.

## 6. Development rules learned from earlier mistakes

1. Never claim a component is installed, deployed, synchronized, backed up, or verified without a real check and recorded result.
2. Never edit an already released migration. Add a new forward migration.
3. Never use a green CI badge as proof of production safety. Inspect test output and add tests for each discovered failure mode.
4. Never test recovery only by checking that a backup file exists. Restore it into a separate database and inspect records, schema version, and integrity.
5. Never assume SQLite and PostgreSQL have identical transaction behavior. Run concurrency and migration tests on every supported production database.
6. Never weaken tests to make a build green. Fix the code or correct a demonstrably wrong test expectation.
7. Keep public source code separate from private data and runtime secrets.
8. Keep the old local project untouched until a separately approved migration plan exists.

## 7. Current release boundary

As of this document's date, the repository branch `core-backend-foundation` is a development backend foundation. It is not a deployed private family site. GitHub Pages is a static Jekyll shell and is not connected to the API or database. The current SQLite backup helper is a tested starting point, not an off-site disaster-recovery system. No real family archive should be placed in this public repository.

The next architectural gates, in order:

1. Finish and verify account/session/rate-limit/bootstrap/role hardening.
2. Test concurrency and migrations on SQLite and PostgreSQL.
3. Upgrade new permanent identifiers to 128-bit while preserving legacy IDs.
4. Define the object-store interface, preservation package, checksums, and full export/import.
5. Build encrypted backup, independent restore, and key-recovery workflows.
6. Add sync and connector boundaries with explicit provenance and conflict handling.
7. Deploy privately only after security review, operations runbooks, and disaster-recovery tests.

## 8. Reference standards and guidance

- [NDSA Levels of Digital Preservation, version 2.1](https://www.ndsa.org/publications/levels-of-digital-preservation/) — storage and geographic separation, fixity, information security, metadata, formats, and sustainability guidance.
- [Digital Preservation Coalition: Fixity and checksums](https://www.dpconline.org/handbook/technical-solutions-and-tools/fixity-and-checksums) — integrity verification and checksum practice.
- [CCSDS / OAIS Reference Model](https://ccsds.org/Pubs/650x0m3.pdf) — preservation packages, information representation, and digital migration concepts.

These are reference frameworks, not a certification claim.
