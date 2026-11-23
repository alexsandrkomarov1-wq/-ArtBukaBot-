# KOMAROVA_CORE — site architecture, navigation and relationship map

**Status:** architecture specification, 23 November 2026  
**Target branch:** core-backend-foundation  
**Implementation status:** designed, not yet implemented.

## 1. Product decision

KOMAROVA_CORE is one family information system, not a collection of unrelated pages. Every module must use the same authoritative identity registry, event/place/media model, permissions, audit trail, and permanent identifiers.

The system has two separate surfaces:

1. **Public family website:** curated, approved content only. It must never contain private records, secrets, private API responses, or private original media.
2. **Private family application:** authenticated application connected to the backend, private database, and private media storage. It owns editing, family records, uploads, archive search, access management, and integrations.

GitHub Pages is a static presentation host. It cannot by itself provide secure authentication, private file delivery, database writes, or a private archive. Do not simulate these capabilities with hidden links or client-side flags. A separate backend and private application hosting are required before private workflows can be operational.

## 2. Global navigation

Navigation must come from one centralized route registry, not from independently copied menus.

### Public navigation target

| Key | Label | Canonical path | Purpose |
|---|---|---|---|
| home | Главная | / | Project overview and approved highlights |
| about | О проекте | /about/ | Purpose, principles and privacy boundary |
| family-history | История семьи | /family-history/ | Approved family history and generations |
| people | Люди | /people/ | Public biographies only where approved |
| timeline | Хронология | /timeline/ | Approved dated events |
| journeys | Путешествия | /journeys/ | Curated trips and city walks |
| places | Места | /places/ | Place stories and map entries |
| gallery | Фотогалерея | /gallery/ | Approved image collections |
| stories | Истории и публикации | /stories/ | Curated articles and narratives |
| telegram | Наш Telegram | /telegram/ | Approved external Telegram links |
| status | Состояние проекта | /status/ | Honest implementation status and evidence |

These are target routes, not a claim that the pages currently exist. A route must not appear as an active link until its page exists and content is reviewed. Otherwise omit it or label it as in development. No blank pages or dead-end links.

### Private application navigation target

| Key | Label | Canonical path | Purpose |
|---|---|---|---|
| app-home | Обзор | /app/ | Authorized dashboard |
| app-people | Реестр людей | /app/people/ | People, aliases, PERSON-ID, relationships |
| app-events | События | /app/events/ | Event creation and chronology |
| app-places | Места и маршруты | /app/places/ | Places, walks and trips |
| app-archive | Семейный архив | /app/archive/ | Private archive search and records |
| app-upload | Загрузка материалов | /app/archive/upload/ | Quarantine, preview and metadata |
| app-albums | Альбомы | /app/albums/ | Private collections |
| app-stories | Семейные истории | /app/stories/ | Drafts, sources and linked entities |
| app-telegram | Telegram | /app/integrations/telegram/ | Connector status and selected-item intake |
| app-search | Поиск | /app/search/ | Unified authorized search |
| app-admin | Управление | /app/admin/ | Users, roles, audit and settings |

Private routes require backend authorization on every request. Hiding a navigation link is not access control. A direct URL while logged out must lead to sign-in and then return to the originally requested safe route.

## 3. Route and link contract

Every internal link must resolve to a registered route. Every route must define:
- stable route key and canonical path;
- public/private visibility and required permission;
- page title, navigation label, parent and breadcrumb behavior;
- canonical entity parameter(s), where applicable;
- loading, empty, not-found, forbidden and failure states;
- owning module and acceptance tests.

Rules:
1. Use canonical paths and base-URL-aware helpers compatible with GitHub Pages.
2. Never build identity URLs from display names or filenames.
3. Use permanent IDs in entity URLs.
4. Preserve filters, sorting, pagination and safe return paths when navigating back.
5. Mark external links as external and use safe browser behavior.
6. Missing or unauthorized entities show explicit not-found/forbidden states.
7. No empty buttons, dead hash links, placeholder JavaScript links or links to unimplemented routes.
8. Route registry and local-link checks run in CI.

## 4. Entity pages and navigation chains

### Person detail
Target: /app/people/{PERSON-ID}/

Connect aliases, relationships and their provenance, biography, source documents, events, photographs, journeys, places and authorized records. Suggested/uncertain photo identifications must be distinguished from confirmed links.

### Event detail
Target: /app/events/{EVENT-ID}/

Connect date and date precision, participants, places, ordered route stops, photos/videos, documents, sources and neighboring chronological events.

### Place detail
Target: /app/places/{PLACE-ID}/

Connect canonical name and aliases, coordinates, history and sources, events, journeys, people, galleries, captions and map context.

### Journey detail
Target: /app/journeys/{JOURNEY-ID}/

Connect narrative, dates, participants, ordered route stops referencing PLACE-ID, route geometry, selected photos referencing PHOTO-ID, event records and related journeys.

### Photo detail
Target: /app/archive/photos/{PHOTO-ID}/

Connect immutable original blob and integrity status, separate previews/derivatives, capture date and precision, confirmed/suggested people, event and place links, source provenance, upload batch, album membership, journey placement and publication approval.

Originals must never be replaced by previews or edited derivatives. Public pages may display only an explicitly approved public derivative, never a private original storage path.

## 5. Shared registry and relationships

The authoritative registry is the source of truth. Main entity families:

- Person: permanent PERSON-ID.
- Event: permanent EVENT-ID.
- Place: permanent PLACE-ID.
- Journey: permanent JOURNEY-ID.
- ArchiveItem / PhotoAsset: permanent archive ID and PHOTO-ID.
- StoredBlob: immutable binary object ID and checksum.
- MediaDerivative: separate derivative ID and provenance.
- Album / Collection: permanent collection ID.
- Story / Publication: permanent content ID.
- Source: source record ID and provenance.
- Relationship: permanent typed link ID.
- ExternalAccount / ConnectorReference: internal connector record with provider IDs stored only as provenance.
- User / Role / Permission / AuditEvent: security and accountability records.

Relationships are typed and many-to-many where appropriate. They carry provenance, creation time, creator and confirmation state. Do not encode relationships in filenames, folder names or manually maintained lists.

Required relationship examples:
- Person ↔ Person: family or other typed relationship.
- Person ↔ Event: participant, organizer, witness, author.
- Event ↔ Place: occurred-at, start, destination, stop.
- Photo ↔ Person: depicted, photographer, owner, mentioned.
- Photo ↔ Event: illustrates, created-during, documents.
- Photo ↔ Place: captured-at, depicts.
- Journey ↔ Place: ordered stop.
- Journey ↔ Photo: selected gallery item with ordering and caption.
- Story ↔ Person/Event/Place/Photo/Source: subject, context, illustration, citation.
- ArchiveItem ↔ Source: imported-from or documented-by.
- Telegram item ↔ ArchiveItem: provenance only, if explicitly selected and imported later.

All real people use existing PERSON-ID values. Never create a new person because a spelling, Telegram username or photo appears.

## 6. Photo and gallery behavior

A gallery is a presentation of references to archive records, not a second uncontrolled media store.

Required behaviors:
- responsive thumbnail grid and lazy loading;
- authorized full-size preview/lightbox with next/previous navigation;
- keyboard Escape and arrow support, plus visible close control;
- captions, dates, places and linked people where permitted;
- filtering by person, event, place, journey, album and date;
- deterministic sorting and pagination;
- loading, empty, unavailable and broken-image states;
- no private original URLs in public HTML;
- public gallery queries only records with active approval for the exact displayed derivative.

If a file is missing or checksum validation fails, show an integrity warning. Never silently substitute another image or a preview for the original.

## 7. Search, breadcrumbs and return paths

Unified private search covers authorized people, events, places, journeys, photos, stories and documents. It must never reveal unauthorized records or their metadata.

Every detail page has breadcrumbs and contextual links. Example chains:
- Главная → Люди → Человек → Событие → Фотография.
- Главная → Путешествия → Поездка → Место → Фотография.
- Главная → Фотогалерея → Фотография → Человек/Событие.

Back navigation should preserve the previous list's filters and page position where feasible. Deep links must work in a new browser tab after authentication.

## 8. Telegram Web browser workflow

The Telegram perimeter contains six distinct source references with separate connector identities and authorization states: `TG-BOT-ARTBUKABOT` (`@ArtBukaBot`), `TG-BOT-BULAKOVARTYOM` (`@bulakovartyom_bot`), `TG-GROUP-FAMILY` (the private family group), `TG-USER-IRINA` (`@irina_wecanship`, daughter's personal account), `TG-USER-ARTYOM` (`@artjurobr`, son's personal account), and `TG-CHAT-MOTHER` (mother's private chat/group locator `-5128386600`, exact peer type to verify). These are source references in the architecture, not live connections or database rows. The two bots remain unchanged. The daughter and son accounts are personal user accounts, not Bot API bots; access requires the respective account owner's authorization and appropriate safeguards. The mother's negative numeric peer ID does not identify its peer type or prove it is a personal account; verify the chat display identity and type in Telegram Web before implementation.

Telegram Web access is designed around the normal browser interface and an account owner's own authenticated session. This is distinct from Bot API integration. A session may be used only for chats/files that account can legitimately access and that the content owner has authorized for the stated purpose.

Target workflow:
1. Open https://web.telegram.org/k/ in the owner's controlled browser profile.
2. The owner enters their Telegram password and confirmation code directly in Telegram Web. KOMAROVA_CORE must never request or store these credentials.
3. Use only the authenticated account's existing access and permissions. For the daughter's personal source, require her explicit, informed authorization of the specific chats, content and date range; she may perform the selection/export herself. Never request or transfer her password, OTP, cookies or session data.
4. For the son's personal source, apply age-appropriate consent and guardian oversight. Never request or transfer his password, OTP, cookies or session data.
5. For the mother's numeric locator, verify the exact peer type and display identity in Telegram Web before designing access.
6. Let the authorized account owner select an attachment or approve a bounded batch of messages/files for intake.
5. Download selected photos/videos/documents through the authorized browser session.
6. Copy them to the local intake path `KOMAROVA_CORE/intake/telegram/attachments` and hand them to File Engine.
7. File Engine validates content, calculates SHA-256, checks duplicates, records source provenance and registers MATERIAL-ID before reporting successful intake.
8. Archive preservation and public publication remain separate decisions. No automatic publication.

Security: never store or export Telegram passwords, one-time codes, session cookies, auth keys or browser profile data in Git, logs, project documentation, public hosting or frontend JavaScript. Do not bypass Telegram access controls, CAPTCHA, rate limits or privacy restrictions. If authentication expires, pause for the owner to sign in interactively. Do not expose the authenticated browser profile to the public website or backend clients.

The ability to access Telegram Web does not authorize downloading the entire group history. At this stage there is no bulk download or continuous monitoring. Support deliberate item selection or a bounded batch approved by the owner. Any future automatic rule for new posts requires a separate specification and explicit activation.

The supplied group Web Telegram locator is not a public invite URL. Do not expose the group publicly until a valid invitation URL and visibility approval exist. The daughter's and son's account links, mother's numeric chat locator and all private chats remain private and must not appear on the public site. Telegram IDs remain provenance only, never PERSON-ID, PHOTO-ID, EVENT-ID or primary registry keys. Telegram API integration is optional and is not required for this browser-based workflow.

The two bot sources may later use Bot API adapters after a read-only audit of the existing bot deployments, credentials custody and update delivery. Group ingestion through a bot depends on actual membership and privacy settings and must not trigger permission changes without approval. The daughter's and son's personal user-account sources cannot be treated as Bot API bots; any MTProto/user-session connector is a separate, consent-gated design. The mother's source must first be classified by its actual Telegram peer type.

## 9. Authorization and publication

Public and private surfaces are separate security domains.

- Public routes return approved publication records only.
- Private routes require authenticated sessions and route-level permissions.
- Owner, moderator, family_member and guest permissions must be specified in a route/action matrix before private CRUD is implemented.
- No anonymous archive browsing, preview, download, search or upload.
- Publication approval is tied to an exact derivative/version and destination.
- Revocation triggers a withdrawal process and audit record.
- A public person, album or event page does not make every linked private record public.

## 10. Error and operational states

Every module defines and tests loading, empty, invalid input, missing entity, forbidden access, backend unavailable, storage unavailable, partial batch failure, stale/revoked link, withdrawn publication, duplicate candidate and integrity failure.

Errors must be human-readable and include a trace/reference ID. Never expose stack traces, tokens, private filesystem paths or raw database errors.

## 11. Delivery phases

### Phase A — audit and route baseline
Inventory current pages, layouts, styles, scripts, API endpoints and tests. Define one route registry and link checks. Separate public pages from future private routes. Fix links only after confirming their intended destinations.

### Phase B — backend domain foundation
Verify people, users, sessions and audit models. Define event, place, journey, story, album and archive records with stable IDs. Define typed relationships and migrations. Approve role-by-route/action matrix.

### Phase C — connected application shell
Implement responsive authenticated shell, route guards, breadcrumbs, global search and error states. Connect frontend to real backend APIs. No mock data presented as saved records. Verify direct navigation, refresh, deep links and return paths.

### Phase D — family graph and timeline
Implement person, event and place detail pages, relationship navigation and chronology. Verify every relationship path in both directions where semantically appropriate.

### Phase E — media and journeys
Implement private media storage, upload quarantine, checksum, preview, duplicate review and photo detail. Then albums, journey editor, ordered route stops, maps and photo selection. Keep private galleries and approved public renditions separate.

### Phase F — external connectors
Add optional Telegram selected-item connector only after security and permissions are approved. Do not rewrite bots or bulk import the group. Report connector availability honestly.

### Phase G — release verification
Run route/link checks, backend and frontend tests, accessibility checks, authorization tests, media integrity checks, backup/restore tests and end-to-end journeys. Update status only with evidence from the exact commit and workflow. A green static-site build does not verify private APIs, database, authentication or media storage.

## 12. Acceptance test catalogue

1. Every visible internal link resolves to an implemented registered route.
2. Every external link has a valid destination and safe behavior.
3. No visible control is inert or points to a dead placeholder.
4. Every page has a title, canonical path, breadcrumb policy and not-found state.
5. Public routes never expose private metadata, API responses, originals or group links.
6. Private routes reject anonymous and unauthorized requests server-side.
7. Deep links survive refresh and return to the originally requested route after sign-in.
8. Person → event → place → journey → photo navigation resolves correct permanent IDs.
9. Galleries open the selected image and support next/previous/close/keyboard navigation.
10. Photo details show original/derivative distinction and integrity status.
11. Removed links do not leave misleading stale UI relationships.
12. Missing media is reported and never silently replaced.
13. Search returns only records the current user may access.
14. Public pages display only the exact approved derivative.
15. Revoked publication is withdrawn and auditable.
16. Approved public Telegram bot links work without API credentials.
16a. The private family group, daughter and son personal accounts, and mother's private chat locator are not exposed on public pages.
16b. Any import from a personal account has a recorded consent scope and an auditable user-initiated selection.
16c. The mother's numeric peer locator has a verified Telegram peer type and display identity before any connector is enabled.
17. No group media is downloaded unless individually selected through an approved workflow.
18. End-to-end test: create/find person, add event/place, upload photo, link entities, search, open authorized gallery.
19. Route/link tests run in CI on every relevant change.
20. Every status claim is backed by commit, workflow and test evidence.

## 13. Current implementation boundary

The repository currently contains a Jekyll public site with a small number of public pages, a backend foundation with people/accounts/sessions/audit and SQLite archive functionality, and architecture documents for media and Telegram boundaries.

The complete route map, authenticated private frontend, all entity detail pages, event/place/journey services, media storage/upload, galleries, maps, cross-entity unified search, Telegram connectors for all six registered sources and end-to-end navigation are not implemented by the existence of this document.

This document defines the target architecture and delivery contract. Implementation status changes only after code and tests exist.


## 14. Family mail and feedback architecture

The family mail module is specified in [docs/family-mail-architecture.md](family-mail-architecture.md). It is a provider-neutral private subsystem, not a public list of family email addresses. The current family providers remain mixed by choice: Yandex Mail for the mother's mailbox and Gmail for the father's and son's mailboxes. No mailbox migration, forwarding, or provider change is implied.

The first delivery step is a local compose action (mailto/deep link) from the private application, clearly labelled as opening the user's configured mail client rather than sending through KOMAROVA_CORE. Public feedback must use a separate project contact address and protected server-side intake; it must never reveal or route directly to private family mailboxes. Reading, searching, drafting and server-side sending require a later, separately authorized provider connection for each mailbox owner.

Mailbox content, addresses, provider identifiers, OAuth scopes, tokens and message metadata are private. They must not be embedded in GitHub Pages HTML, JavaScript bundles, public API responses, logs or public documentation. Each mailbox owner controls consent and scopes; access by one family member does not grant access to another mailbox. The son's account requires age-appropriate consent and guardian oversight. Credentials and tokens remain in a dedicated secrets vault or protected runtime secret store, never in Git.

Mail records may link to existing PERSON-ID, EVENT-ID, PLACE-ID, JOURNEY-ID, STORY-ID and archive records through typed relationships with provenance and access checks. Email addresses are contact attributes, never identity keys. Duplicate contacts must resolve to the existing person record rather than creating a second person.

Mail connector outages must not affect the public site or core family registry. Imported message bodies and attachments enter a controlled intake/quarantine process; attachments pass through File Engine, checksum and duplicate review before archive registration. No automatic ingestion, mailbox-wide indexing or cross-mailbox sharing is enabled by this architecture alone.
