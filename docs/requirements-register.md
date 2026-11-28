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


## 11. Family calendar and planning

The calendar is a shared planning capability of KOMAROVA_CORE, not a separate application or a substitute for FAMILY_TIMELINE. It must be connected to the existing family identity, places, archive, access-control and audit model.

**Purpose:** let authorized family members plan future activities and appointments, coordinate participants, schedule walks and trips, manage reminders and tasks, and see the family's shared commitments. The existing places/walks capability describes routes and destinations; the calendar adds when an activity happens, who participates, preparation tasks and notifications.

### Functional scope

- **Calendar views:** month, week, day and agenda/list views; navigation by date; clear distinction between all-day and timed events.
- **Event planning:** create, edit, cancel, duplicate and archive planned events. Each event has a stable EVENT-ID, title, description, start/end, timezone, location or linked PLACE-ID, status, creator, participants and visibility.
- **Event types:** family meeting, birthday/anniversary, appointment, trip, walk, excursion, school/work commitment, reminder and custom type. Types must be configurable without changing the core schema.
- **Participants:** link existing people by PERSON-ID; record invitation/confirmation/decline status. Do not create duplicate person records when inviting someone already in the registry.
- **Walks and trips:** schedule an existing walk/trip from FAMILY_PLACES, or create a draft walk from a calendar event. Preserve one canonical event and one canonical place/route record, linked by IDs; do not copy the same details into competing records.
- **Tasks and preparation:** attach checklist items and responsible people to an event, with due dates, completion status and optional notes. Tasks must also be available in a unified family task list.
- **Recurrence:** support repeat rules (daily, weekly, monthly, yearly, custom interval), end date or occurrence limit, and exceptions. Editing one occurrence must not silently rewrite the entire series.
- **Reminders and notifications:** configurable reminders before an event and task deadline; in-app notifications first, with optional email/push adapters later. Notification delivery status and failures must be visible; never claim a reminder was sent without provider confirmation.
- **Conflict detection:** warn about overlapping events for the same participant and allow the user to review conflicts. Do not automatically delete, move or reject events.
- **Search and filters:** filter by date range, participant, event type, place, status and calendar; search titles and descriptions subject to access permissions.
- **Shared calendars:** support family-wide and restricted calendars, with explicit read, create, edit, invite and administration permissions. Guest access is read-only unless separately granted.
- **External calendar access:** design replaceable adapters for importing/exporting standard calendar data (ICS) and, after provider review and user authorization, connecting external calendars. External calendars are not the authoritative family registry.
- **Accessibility and clients:** responsive desktop/mobile calendar, keyboard navigation, readable event labels and timezone-aware display.
- **Audit and recovery:** record event creation, edits, cancellation, participant changes, permission changes and synchronization conflicts. Preserve event history and stable IDs.

### Data and architecture rules

- Calendar scheduling records are future/planned commitments; FAMILY_TIMELINE records sourced life events and historical chronology. A completed calendar activity may be linked to a timeline event, but the two records have distinct purposes and must not be conflated.
- A calendar event may link to PERSON-ID, PLACE-ID, ARCHIVE-ID and a walk/trip record. References must use the authoritative IDs from the shared registry.
- Store timestamps in a timezone-safe form and retain the event's intended timezone. All-day events must remain date-based and must not shift dates when viewed in another timezone.
- Recurrence, reminders, invitations and external synchronization must be idempotent and auditable. Conflicts require user review.
- Calendar data follows the same backup, export, privacy, access-control and retention rules as other family records.
- Do not introduce a second people registry, independent calendar database or new cloud project for this capability.

### Homepage family dashboard and city discovery

The authenticated home page is the family's shared planning workspace. It must not expose private family plans on the public landing page.

#### Family home dashboard
- Show a concise upcoming schedule for the next days/weeks, shared family plans, pending invitations, tasks and reminders.
- Each participant can create a personal plan, mark selected time as available/busy, and choose whether an item is private, visible to selected people, or visible to all family members.
- Family-wide plans are visible to all authorized family participants. Personal events are visible only according to the owner's explicit visibility setting and the viewer's role.
- Show who is interested, invited, confirmed, declined or still undecided for each joint activity.
- Allow a participant to propose a joint walk, excursion, museum/theatre visit or trip from the home page and invite all or selected family members.
- Provide a shared availability view that reveals only free/busy information for private events, not their titles, locations or descriptions.
- Provide filters by person, date, city, activity type and participation status.
- Keep the public home page free of private schedule data. The authenticated family dashboard is rendered only after successful session and authorization checks.

#### City culture, events and listings
- Provide a unified discovery area for museums, galleries, exhibitions, theatres, concerts, festivals, lectures, children's activities, parks, historical sites and other local attractions.
- Provide an events poster/agenda view with date, start time, venue, city, age guidance, language where available, accessibility information, price or free-entry status, booking/ticket link and source.
- Support searches by city, date range, category, interests, age suitability, budget, indoor/outdoor and accessibility needs.
- Show currentness: source, last checked time, event date and a clear unavailable/expired state. Do not invent schedules, ticket prices, availability or opening hours.
- Prefer official venue, museum, theatre, city and ticket-provider sources. Preserve source links and distinguish official information from third-party listings.
- Allow a user to save a place/event, suggest it to the family, attach it to a calendar event and add it to a draft trip or walk.
- Support more than one family city. Each participant may set a preferred city or choose a city for a particular search; location access must be optional and explicit. Do not assume all family members live in the same city.

#### AI family activity planner
- AI may propose shared activities by combining participants' explicitly shared availability, selected city, interests, age suitability, budget, duration, weather or indoor/outdoor preference when those data are available and authorized.
- AI recommendations must explain why an activity was suggested, identify which family members it may suit, show conflicts/unknowns and cite the source of event/place information.
- AI may draft one-day or multi-day itineraries, group nearby attractions, estimate visit duration and propose alternatives for bad weather, closures or schedule conflicts.
- AI may suggest a date/time only from available family free/busy data and must ask for confirmation before creating or changing calendar events, sending invitations, booking tickets or spending money.
- AI must not reveal private events, personal interests or location data to other participants unless the owner has shared them.
- Family members can accept, reject, edit or ignore suggestions. Rejections and preference feedback may tune future recommendations only under the relevant privacy settings.
- If live event data, weather or route data cannot be verified, label the result as an unverified suggestion rather than presenting it as current fact.

#### Maps and route planning
- Every place/event card should offer a map view and route from a user-selected starting point or an explicitly authorized saved starting point.
- Offer separate route modes: public transport, walking and, where supported later, cycling/car. Public transport and walking are required for the first route-planning release.
- Public transport routes should show route legs, transport mode, line/route number, stop/station names, transfers, estimated duration, walking segments and service-data timestamp where provider data supports them.
- Walking routes should show distance, estimated walking time, route geometry/map link and accessibility or surface notes where available.
- Allow a user to choose a departure time or arrival-by time. Show route alternatives and explain when live disruption data is unavailable.
- Keep map and routing providers replaceable. Select providers only after reviewing API coverage, licensing, privacy, cost and service availability for each city.
- Do not expose a participant's home address or live location to other family members by default. Use an explicit origin selection and privacy controls.
- Store canonical PLACE-ID and route references in KOMAROVA_CORE; provider-specific place/route identifiers remain external references, not new family entities.

#### Architecture and delivery rules
- The home dashboard consumes the existing authoritative people registry, family calendar, places, access control and audit services. It must not create parallel people, calendar, places or event registries.
- City listings and external event feeds are cached external discovery data with source/provenance and expiry; they are not authoritative family records until a participant saves or links them.
- AI, event listings, maps, public transport and geocoding are replaceable adapters. Do not introduce a separate cloud project or database for these capabilities.
- Personal availability, saved interests, preferred cities, starting points and location permissions are protected personal data with explicit visibility and retention controls.
- The first delivery must work without continuous location tracking. Manual city and starting-point selection is a supported baseline.
- Do not enable real family data until authentication, role-based authorization, private hosting, audit, backups and restore gates pass.

### Family bulletin board and visited / nearby places map

The authenticated homepage includes a shared, interactive family bulletin board and a map-based memory/discovery layer. These are connected views over the same family records, not independent mini-applications.

#### Interactive family bulletin board
- Provide a chronological and filterable board feed for family announcements, questions, proposals, invitations, trip/walk ideas, recommendations, photos from completed activities and practical notes.
- Each post has a stable POST-ID, author PERSON-ID, created/updated timestamps, content, optional attachments, visibility, linked EVENT-ID/PLACE-ID and moderation/audit history.
- Support comments, replies, reactions or lightweight votes, pinning important posts, editing/deleting own posts, and marking a proposal as accepted, declined, postponed or completed.
- A post can become a calendar event or draft trip/walk without copying the content into duplicate entities.
- Allow mentions/invitations only to authorized family members. Notify participants according to their settings.
- Board visibility follows family roles and per-post visibility. It is private to the family by default; nothing is published publicly unless explicitly approved.
- Provide board filters: all family, my posts, proposals, upcoming, completed, places, photos and announcements.

#### Family map: visited, planned and nearby
- Provide an interactive map with distinct, filterable states: visited, want to visit, proposed to family, planned, and temporarily unavailable/closed where source data confirms it.
- Visit history is a separate record per person and visit date, not a single boolean on the place. One family member may have visited while another has not.
- Each visit record links PERSON-ID, canonical PLACE-ID, optional EVENT-ID, visit date/time, notes, rating, photos/ARCHIVE-ID and source/provenance.
- Let family members mark a place as visited, add a short memory/photo, or add it to a personal or shared wishlist.
- Nearby discovery uses a user-selected city, map center or explicitly granted one-time location. It must work without continuous GPS tracking.
- Allow radius selection and categories such as museums, theatres, exhibitions, parks, monuments, nature, cafés and family attractions.
- Show nearby places not yet visited by the selected participant(s), and distinguish places never visited by anyone in the family from places visited by some members.
- Filters include distance, category, opening status when verified, budget, age suitability, accessibility, wishlist status and family visit history.
- From a map marker, open the place card, source details, family notes, visit history, proposed dates and route options.
- Provide list and map modes, clustering at wider zoom levels, and a clear legend. Do not imply a place was visited based only on GPS proximity; a participant must confirm the visit.
- Map markers and visit history reference canonical PLACE-ID and PERSON-ID. External map-provider IDs remain source metadata.

#### Integration rules
- The board, calendar, family places and archive share the authoritative registry and audit model. A post, place, event, route, visit and media file each retain their own stable ID and typed links.
- AI may draft a board proposal, suggest nearby places not yet visited by relevant family members, or turn a discussion into a draft plan. A human must approve publication, invitations and calendar changes.
- Search and recommendations must respect each participant's visibility permissions. Do not leak private plans, visit history, location or interests into another member's AI response.
- Keep the map provider and place-discovery source replaceable. Cache external data with source, retrieval time and expiry; preserve attribution and usage conditions.
- No separate family places database or new cloud project. The board and map are modules of KOMAROVA_CORE.

### Family board and map acceptance requirements
- REQ-BOARD-001: Create and display a private family announcement/proposal feed with stable POST-ID and author PERSON-ID.
- REQ-BOARD-002: Support comments, replies, reactions/votes, pinning and proposal lifecycle states with audit history.
- REQ-BOARD-003: Link board posts to canonical EVENT-ID, PLACE-ID and ARCHIVE-ID without duplicate records.
- REQ-BOARD-004: Enforce per-post visibility and role permissions; public publication requires explicit approval.
- REQ-MAP-001: Display saved places on an interactive map with visited, wishlist, proposed, planned and verified unavailable states.
- REQ-MAP-002: Track visits per person and date; distinguish places visited by some family members from places not visited by anyone.
- REQ-MAP-003: Allow a participant to confirm a visit and attach notes, rating and archive photos.
- REQ-MAP-004: Discover nearby places by selected city, map center or explicit one-time location, with adjustable radius and categories.
- REQ-MAP-005: Filter nearby places by family visit history, distance, category and verified availability; do not infer a visit from GPS proximity.
- REQ-MAP-006: Provide map/list modes, marker clustering, a legend and place cards linked to canonical PLACE-ID.
- REQ-PRIV-002: Prevent private board posts, visit history, location and interests from being exposed through maps, notifications or AI recommendations.

### Homepage and discovery acceptance requirements
- REQ-HOME-001: Render a private family dashboard only after authenticated session and authorization checks; keep the public landing page free of private plans.
- REQ-HOME-002: Show upcoming shared events, invitations, tasks and reminders from the authoritative family calendar.
- REQ-HOME-003: Let each participant control personal event visibility: private, selected family members or all authorized family members.
- REQ-HOME-004: Provide a privacy-safe shared availability view that reveals free/busy only for private events.
- REQ-HOME-005: Let participants propose joint trips, walks and cultural visits and manage invitations/responses.
- REQ-DISC-001: Search and display museums, exhibitions, theatres, concerts, festivals, parks, historic sites and family activities by city and date.
- REQ-DISC-002: Display event date/time, venue, price, age/language/accessibility details, ticket link, source and last-checked time when available.
- REQ-DISC-003: Save a discovery result and link it to a canonical PLACE-ID and calendar EVENT-ID without creating duplicate records.
- REQ-AI-008: Generate explainable family activity suggestions from authorized availability, city, interests and constraints; require human confirmation before committing plans or purchases.
- REQ-ROUTE-001: Offer public-transport and walking routes with duration, route legs, transfers/stops or walking distance, and data freshness where supported.
- REQ-ROUTE-002: Support explicit origin and departure/arrival time selection without exposing home addresses or live location by default.
- REQ-PRIV-001: Enforce privacy and authorization for schedule, availability, interests, preferred cities, starting points and location data across UI, API, AI prompts and audit records.

### Acceptance criteria and status

- REQ-CAL-001: Create, view, edit, cancel and archive calendar events with stable EVENT-ID.
- REQ-CAL-002: Display month, week, day and agenda views on supported screen sizes.
- REQ-CAL-003: Link events to existing PERSON-ID and place/walk records without duplicate entities.
- REQ-CAL-004: Manage participants and invitation responses under role-based permissions.
- REQ-CAL-005: Create event checklists and assign tasks with deadlines and completion states.
- REQ-CAL-006: Support recurring events, exceptions and safe single-occurrence/series editing.
- REQ-CAL-007: Configure reminders and report actual notification delivery/failure.
- REQ-CAL-008: Detect participant schedule overlaps and present them as warnings for human resolution.
- REQ-CAL-009: Enforce shared-calendar visibility and separate read/create/edit/invite/admin permissions.
- REQ-CAL-010: Import/export ICS and verify round-trip behavior before enabling external calendar synchronization.
- REQ-CAL-011: Preserve timezone and all-day event semantics across clients and exports.
- REQ-CAL-012: Maintain audit history, stable IDs, backup and restore coverage for calendar records.

**Current implementation status: Planned.** Repository inspection found no calendar page, calendar-specific JavaScript, calendar API routes or calendar data tables in the current working branch. The places gallery is a separate existing interface and does not provide calendar planning. This section records approved product requirements only; it does not claim that the calendar has been implemented.


### New acceptance requirements
- REQ-ARC-010: Detect actual media type and codec/container metadata independently of filename extension; preserve original filename as provenance.
- REQ-ARC-011: Apply EXIF orientation and video display-matrix rotation to separately stored derivatives after malware scanning; never modify originals.
- REQ-ARC-012: Create browser-compatible image/video derivatives with verified output metadata and separate checksums.
- REQ-CLIENT-003: Provide contextual page-aware navigation hints and accessible popovers without exposing private records.
- REQ-AI-007: Provide a provider-neutral conversational site assistant only through a protected backend; distinguish verified system facts from guidance and model inference.


### Family board and discovery map — first browser prototype

**Approved module name:** Семейная интерактивная доска объявлений + карта семейных открытий.

**Prototype delivery:** A public, non-sensitive demonstration page is being added to the static site so the interaction can be inspected before private backend deployment. It is not the authenticated family board and must not contain real family information.

- The demo supports creating/filtering/pinning/deleting sample posts, local comments and lightweight reactions.
- The map supports per-demo-participant place states, map/list selection, city geocoding and on-demand nearby POI discovery through OpenStreetMap.
- Demo records use clearly marked demo identifiers and browser-local storage only. They are not inserted into the authoritative registry, Neon database or cloud storage.
- The map uses OpenStreetMap tiles and attribution. Nearby POI search is an explicit request to the public Overpass API; no continuous GPS tracking is used.
- No real family members, visit history, addresses, private plans or archive media are preloaded.
- The prototype does not provide authentication, cross-device synchronization, server persistence, role permissions, production audit, or verified notifications.

**Implementation status:** Browser prototype, pending CI and live-page verification. Production family functionality remains planned until the backend, private hosting, access control, authoritative IDs, backup/restore and integration tests are available.


## 12. System time and timezone policy

- KOMAROVA_CORE must not query public websites, third-party APIs, browser widgets or external time services to obtain or synchronize the current time.
- Browser-facing local date/time displays and local user actions use the device's operating-system clock through the browser's native date/time facilities. The application must not hardcode the Netherlands offset or any other fixed UTC offset.
- Backend audit and record-creation timestamps use the backend host operating-system clock and are normalized/stored as timezone-aware UTC values. UTC normalization is a representation rule; it is not an instruction to fetch time from the internet.
- Historical event dates, photo capture dates and place-visit dates are user/source data. They must not be silently replaced with the current date or inferred from the time of upload.
- Calendar events must preserve the timezone/all-day semantics supplied by the user or source. Display conversion uses the viewer's device timezone unless the event explicitly carries another timezone.
- If a device/server clock is incorrect or unavailable, the application must not silently substitute an online clock. It should expose the limitation and retain source timestamps/provenance where available.
- Automated tests must use an injected/frozen clock where deterministic behavior is required; production code must retain the operating-system clock as its time source.

**Implementation note:** the current backend helper `utc_now()` uses Python `datetime.now(timezone.utc)`, which reads the host OS clock and represents that value in UTC. This is not network time synchronization. Browser `Date` APIs likewise use the device clock. No external time provider is required for these operations.


## 13. Photo geography and capture-time analysis

- REQ-PHOTO-GEO-001: Use `Europe/Amsterdam` as the project default timezone, without hardcoding a UTC offset. Apply it only when photo location/timezone evidence is absent and label the result as an assumption.
- REQ-PHOTO-GEO-002: Read EXIF DateTimeOriginal, OffsetTimeOriginal, GPS coordinates, GPSDateStamp and GPSTimeStamp without modifying the original file.
- REQ-PHOTO-GEO-003: Resolve the timezone at the photo's GPS coordinates using an offline IANA timezone boundary database; apply the historical daylight-saving rules for the capture date.
- REQ-PHOTO-GEO-004: Prefer GPS UTC capture time, then explicit EXIF UTC offset, then the GPS-location timezone. If GPS is present but its timezone cannot be resolved, do not silently substitute Amsterdam.
- REQ-PHOTO-GEO-005: Store raw EXIF date, coordinates, resolved timezone, derived local/UTC timestamps, provenance and confidence separately.
- REQ-PHOTO-GEO-006: Do not send private photo coordinates to public reverse-geocoding services. A named place must come from an approved offline gazetteer or explicit user confirmation.
- REQ-PHOTO-GEO-007: Unknown or conflicting metadata must remain unknown/conflicting; never invent a place or time.

**Implementation status:** read-only extraction module added at `backend/app/photo_metadata.py`. Automatic archive persistence and upload/enhancement integration are not yet implemented. The optional `timezonefinder` dependency must be installed and covered by tests before location-based timezone resolution is available in the running service.
