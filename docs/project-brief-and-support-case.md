# KOMAROVA_CORE: project brief, technical scope and support case

**Status date:** 28 November 2026  
**Maintainer:** independent individual maintainer  
**Project type:** non-commercial, privacy-first, open-source family archive software  
**Public source:** https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-  
**Public showcase:** https://alexsandrkomarov1-wq.github.io/-ArtBukaBot-/

## 1. The problem

Family photographs, scanned documents, oral histories and place/event records are commonly scattered across phones, social networks, messaging exports and consumer cloud accounts. Links expire, accounts are lost, formats become obsolete, and edited copies can silently replace originals. Families also need a way to share selected stories without exposing private originals or personal data.

KOMAROVA_CORE is being developed to address that preservation and access problem with a portable registry, immutable originals, traceable derivatives, controlled sharing and verifiable backups.

This is not a public dataset project. Family materials remain private and are not published as training data or exposed in the public repository.

## 2. What the software is intended to do

- Maintain stable PERSON-ID, EVENT-ID, PLACE-ID and MATERIAL-ID records and their relationships.
- Keep an original file immutable and store every restored/enhanced version as a separate derivative linked to its source MATERIAL-ID.
- Record SHA-256, byte size, media type, provenance and processing history.
- Accept private media into quarantine before it becomes available to normal archive workflows.
- Apply authentication and role-based access, with revocable sessions and an auditable record of important actions.
- Export a portable archive, verify its checksum and database integrity, and restore to a new destination without overwriting an existing archive.
- Replicate encrypted/private archive objects to independently configured storage providers and mark a replica available only after read-back verification.
- Offer open-source media restoration tools without requiring a paid per-image AI API.

## 3. What exists in the repository today

The public repository contains an executable Python backend foundation, database migrations, API routes, registry models, backup/archive code, provider adapters, media-processing code, frontend modules and automated tests.

Implemented code includes:
- account bootstrap, login, revocable sessions, role checks and persisted login throttling;
- family-person and relationship registry APIs;
- event, place, visit, material and entity-link data models;
- private media intake and quarantine/scan workflow code;
- portable archive export/verification/restore primitives;
- Google Drive replication queue code and provider-neutral OneDrive/ Yandex Disk replication worker code;
- AI media worker code using local/open-source components, including Real-ESRGAN NCNN Vulkan and FFmpeg-based processing paths.

**Repository code is not the same as a live production service.** As of this status date, the private backend and replication workers are not confirmed deployed on a public server. Personal cloud credentials have not been placed in the repository and no live multi-provider upload is claimed. AI worker code requires its external binaries/models and a suitable runtime; production inference is not claimed until a real test job is completed and its output is verified.

The GitHub Pages site is a public showcase only. It is not the private archive server and must never be used to store family originals.

## 4. Why infrastructure support is needed

A persistent Linux host is required to run the private API, database, background workers, scheduled integrity checks and restore tests. Static hosting cannot execute these services. The requested initial footprint is deliberately modest:

- 2 vCPU;
- 4 GB RAM;
- approximately 50 GB SSD/NVMe;
- Debian or Ubuntu;
- secure remote administration and network access;
- a documented backup/export path.

This is a starting point for the API, relational metadata and background jobs, not a claim that it can host an unlimited media archive or heavy GPU inference.

A separate GPU-capable machine or donated compute time may be useful for AI restoration experiments. The project does not require a paid proprietary AI subscription: the intended approach is to use open-source models and local inference where licensing, hardware and quality tests permit. CPU-compatible fallbacks and bounded job sizes are required so the archive remains usable without a GPU.

## 5. Why AI compute is relevant

AI is a supporting preservation tool, not the product's only purpose. Old family photographs may be blurred, noisy, faded or low-resolution. Local restoration models can help create a more legible derivative while retaining the source unchanged.

The project will:
1. preserve and hash the source before processing;
2. scan the input and reject unsupported or unsafe files;
3. run a versioned open-source processing pipeline;
4. store the output as a new material with a new MATERIAL-ID and a link to the original;
5. record model/engine, parameters, timestamps and output hash;
6. allow comparison and export of both source and derivative;
7. never claim that AI reconstruction is historically accurate.

No family image is required to be made public to demonstrate the software. Public demonstrations should use synthetic, public-domain or explicitly consented sample images.

## 6. Public benefit and openness

The software and technical documentation are intended to be publicly inspectable and reusable. The private family archive is not open data. The project separates:
- **open software:** source code, schemas, tests, deployment instructions and generic sample data;
- **private content:** family photos, documents, names, contact details, account data and private metadata.

Potential benefits include long-term digital preservation, reduced dependence on a single commercial platform, transparent file integrity, portable backups, and accessible tools for families who cannot afford recurring AI restoration services.

The project is independently maintained and is not represented as a registered charity, NGO, university or research institution.

## 7. Delivery milestones and acceptance evidence

| Milestone | Deliverable | Acceptance evidence |
| --- | --- | --- |
| A. Backend foundation | Reproducible installation, migrations, authentication and registry API | CI tests, clean install log, API smoke tests |
| B. Preservation core | Immutable originals, derivative lineage, SHA-256 and audit trail | Tests proving original hash unchanged and derivative linked |
| C. Recovery | Portable export, verification and restore to a new destination | Automated round-trip, checksum and foreign-key tests |
| D. Cloud replication | Independent provider queues and verified copies | Test doubles plus live opt-in upload/read-back for each provider |
| E. AI restoration | Reproducible open-source image/video worker | Sample input/output, model/license record, before/after comparison, source hash unchanged |
| F. Private deployment | HTTPS, secrets, monitoring, access controls and operational backups | Deployment checklist, health checks, restore drill and security review |
| G. Public showcase | Accessible public explanation and safe demo materials | Pages build, link checks and no private data in repository |

A milestone is complete only when its acceptance evidence exists. A code module, mock screen or green syntax check alone is not proof of a working deployed feature.

## 8. Security and privacy commitments

- No real family documents, photos, OAuth tokens, passwords or private database dumps in Git.
- Originals are never overwritten by enhancement or replication.
- Private storage must not be exposed through the public static site.
- Uploads enter quarantine and must pass validation/scanning before normal use.
- Replicas are not marked successful until downloaded and hash-verified.
- Backups must be tested by restoring to a new location.
- Access must be revocable and least-privilege.
- Public demo material must be synthetic, public-domain or explicitly consented.
- Any security incident or data-loss risk must be documented honestly.

## 9. What support is being requested

The project seeks in-kind infrastructure and, if available, donated compute credits or access to a GPU worker. It is not asking a provider to host an unlimited amount of private family data indefinitely.

Any support offer must state:
- exact physical hosting location and service region;
- resources and storage limits;
- whether the support is fully free, including setup, membership, bandwidth, backups and renewal;
- duration, review and renewal conditions;
- acceptable use and data-processing terms;
- backup responsibility, export procedure and termination notice;
- whether GPU/AI compute is included or separately available.

The maintainer cannot accept undisclosed recurring fees or automatic paid conversion. If support is time-limited, it will be described as time-limited.

## 10. Current limitations and next engineering priorities

The next priorities are not additional visual effects. They are:
1. keep CI green and expand tests around provider adapters, retry safety and failure recovery;
2. validate worker/database/storage contracts end-to-end before enabling cloud replication;
3. complete the private backend deployment and secret management;
4. implement resumable browser uploads and raise file-size limits only with tested streaming/backpressure controls;
5. complete a real backup restore drill;
6. run AI processing against safe sample media on the actual target hardware and record resource use;
7. publish only features that have passed their acceptance checks.

The project will publish limitations alongside progress rather than presenting planned work as completed.
