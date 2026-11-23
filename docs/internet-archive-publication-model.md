# Internet Archive publication model

**Project:** KOMAROVA_CORE  
**Status:** architecture specification, 23 November 2026  
**Target branch:** core-backend-foundation  
**Implementation status:** designed only; no Internet Archive account, collection, connector, or upload workflow is configured by this document.

## 1. Purpose and boundary

Internet Archive is an optional external publication and discovery destination for selected, rights-cleared family-history materials. It is not the authoritative KOMAROVA_CORE registry, not the private family archive, and not the only preservation copy.

KOMAROVA_CORE remains the system of record for permanent entity identifiers, relationships, original files, immutable checksums, provenance, metadata corrections, family permissions, publication approvals and publication history.

Internet Archive may host public copies of approved items and provide item pages, readers, playback, search and sharing links. Each published item is linked back to its KOMAROVA_CORE publication record.

## 2. Suitable publication types

Potential public materials, subject to rights and approval:
- family-history essays and researched biographies;
- digitized letters, diaries and documents where publication is authorized;
- historical photographs and curated albums;
- oral-history audio and video recordings with informed participant consent;
- family chronologies, maps, research notes and bibliographies;
- public-domain or openly licensed source material with correct attribution.

Do not publish private correspondence or mailbox exports; identity, financial, medical or other sensitive documents; home addresses, private phone numbers, private account identifiers or exposing location metadata; material involving living people without appropriate documented approval; content where copyright, ownership, license or permission is uncertain; or private originals merely because a public derivative exists.

A family member's consent to preserve an item in the private archive is not consent to publish it on the open Internet.

## 3. Publication workflow

Publication is separate from intake and preservation:

1. Select an existing ArchiveItem or Story by permanent ID.
2. Check provenance, creator, copyright holder, source, date and rights evidence.
3. Confirm consent for every identifiable living person where required.
4. Prepare a publication derivative or export package. Never upload the private master by default.
5. Scan for personal data, EXIF GPS, hidden document metadata, embedded comments, tracked changes and unintended attachments.
6. Prepare descriptive metadata and a rights/license statement. Never invent a license.
7. Record explicit approval for the exact file checksum, metadata version, destination and publication scope.
8. Upload through an account controlled by the project owner. Initial delivery may be manual through the official Internet Archive interface; no automated connector is implied.
9. Verify the resulting item page, files, metadata, visibility and playback/download behavior.
10. Store the external item identifier, URL, uploaded file checksum, timestamp and verification result in KOMAROVA_CORE.
11. Add the external link to the public website only after verification and approval.
12. If approval is revoked or an error is found, record a withdrawal request and verify the external outcome. Do not promise immediate or guaranteed deletion by the external provider.

## 4. External item metadata

Each external publication record should retain:
- PUBLICATION-ID: permanent KOMAROVA_CORE identifier;
- ARCHIVE-ITEM-ID or STORY-ID: source record;
- destination_provider: internet_archive;
- external_identifier: Internet Archive item identifier, once assigned;
- external_url: verified item details URL;
- published_blob_sha256: exact public file checksum;
- metadata_version: version of approved descriptive metadata;
- rights_statement and license: only when verified and approved;
- approval_id, approver and approval timestamp;
- publication_state: draft, approved, uploading, published, verification_failed, withdrawal_requested, withdrawn, or unknown;
- last verification timestamp and result.

Internet Archive identifiers are external identifiers. They must never replace PHOTO-ID, PERSON-ID, STORY-ID or any other internal permanent ID.

## 5. Rights, visibility and user expectations

Treat every upload as potentially public, searchable, downloadable and shareable. Do not rely on obscurity of an item URL as a privacy control.

The uploader must have the right to contribute the material and must choose a truthful rights/license statement. A Creative Commons license can permit reuse under specified conditions; it must not be selected merely to make an upload form complete. Where rights are unclear, do not publish until resolved.

Internet Archive help material explains account-based uploading, item metadata and public sharing. Its collection policy states that hosted items are organized into collections and that creation of a dedicated collection is subject to Internet Archive staff criteria and approval. KOMAROVA_CORE must not assume it can create a named collection immediately or that every item can be assigned to a custom collection.

## 6. Preservation and dependency rules

- Keep the authoritative original in KOMAROVA_CORE-controlled storage and independent backups.
- Keep a separate publication derivative and its SHA-256.
- Never treat Internet Archive as the sole backup or guarantee of perpetual availability.
- Periodically verify external item URL and file availability.
- Record external provider outages and changes without corrupting the internal archive.
- Maintain a portable local export of metadata and published derivatives.
- External deletion, moderation, item restrictions or account loss must not destroy the internal master or registry record.

## 7. Security

- No Internet Archive credentials, cookies, access tokens or recovery codes in Git, public HTML, browser JavaScript or logs.
- No upload from GitHub Pages. Any future automated uploader must run server-side with narrowly scoped secrets and explicit human approval.
- No automatic bulk publishing or synchronization.
- No public links until the exact external item has been checked.
- Do not include private family identifiers in item identifiers, descriptions, filenames or metadata.

## 8. Delivery stages

### IA-0 — architecture
This document and the publication approval boundary. No uploads or live connection.

### IA-1 — manual publication
Human-reviewed export package, metadata checklist, manual upload, verification and recording of the resulting external URL. This is the preferred first release.

### IA-2 — publication register
Private backend records for publication IDs, approvals, external identifiers, checksums and verification history.

### IA-3 — optional server-side adapter
Only after IA-1 and IA-2 are tested. Use official documented APIs, a dedicated account, secret storage, audit logs, idempotency, rate-limit handling and explicit approval for every upload. No public-site credential exposure.

## 9. Acceptance criteria

1. A private archive item cannot be published without separate approval.
2. Approval is bound to the exact derivative checksum, metadata version and destination.
3. A changed derivative or metadata requires renewed review where it changes published content.
4. No sensitive personal data or private original path appears in the public export.
5. The rights statement is verified and not invented.
6. The uploaded item is opened and checked before a public link is shown.
7. The external item ID and URL are stored against a permanent internal publication ID.
8. External unavailability does not affect the internal archive.
9. Withdrawal requests and outcomes are auditable.
10. No Internet Archive connector or automated upload is considered implemented until code, secrets handling, tests and a verified end-to-end upload exist.

## 10. Official references

- Internet Archive account and upload overview: https://archivesupport.zendesk.com/hc/en-us/articles/360016378232-Accounts-A-Basic-Guide
- Uploading a basic item: https://archivesupport.zendesk.com/hc/en-us/articles/360002360111-Uploading-A-Basic-Guide
- Upload tips, formats and licensing: https://archivesupport.zendesk.com/hc/en-us/articles/360016475032-Uploading-Tips
- Collections and eligibility: https://archivesupport.zendesk.com/hc/en-us/articles/360016399952-Collections-A-Basic-Guide
- Sharing and embedding: https://archivesupport.zendesk.com/hc/en-us/articles/360016634811-Managing-and-Editing-Your-Items-Tips-Troubleshooting
- Developer APIs: https://archive.org/developers/
