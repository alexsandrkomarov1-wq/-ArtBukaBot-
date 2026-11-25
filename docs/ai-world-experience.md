# KOMAROVA_CORE — AI World Experience

**Status:** implementation direction  
**Working branch:** `core-backend-foundation`  
**Scope:** extend the existing online application in place. Do not replace it with a separate demo.

## Product concept

KOMAROVA_CORE is an interactive science-fiction AI world. The user enters a navigable digital environment and reaches the existing family information system through spatial locations, portals, interactive objects, maps, and an AI guide. It is not a museum-only layout and not a decorative 3D hero.

## Experience principles

- Preserve the existing application, routes, records, APIs, and working sections. Add the 3D world as an interface layer over them.
- The spatial world is the primary immersive navigation experience; conventional accessible navigation remains available as a fallback.
- Every portal, panel, object, map marker, and tab must lead to a real section or a clearly marked not-yet-available state. No fake working controls.
- Do not create a second family database or duplicate identity/material registries.
- Never expose private family information in public pages. Apply existing authorization rules to every object and preview.
- Do not send family files to third-party AI services without explicit authorization.
- Do not require paid APIs, paid trials, payment cards, or new hosting without explicit approval.

## World structure

### Central AI hub
The entry space, orientation point, global search, world map, recent activity, quick links, and AI assistant. The assistant explains the current location, available actions, and navigation. It must not invent archive facts or claim that an operation succeeded before the application confirms it.

### Generations world
Interactive family tree and generation galleries. Each person resolves to the existing permanent PERSON-ID. A person view may expose biography, relationships, events, places, and authorized materials.

### Memory and media world
Photo, video, audio, and document collections. Each archive item resolves to the existing MATERIAL-ID. Show original and derivative relationships, metadata, access level, and verified physical storage location/provider. Originals are immutable. Enhanced/restored copies are separate materials with their own MATERIAL-ID and a link to the original. Failed scanning or processing never removes or replaces the original; failures are recorded independently.

### Geography and travel world
Interactive map with places, routes, and visit history (“where we have been”). Support walking and transport routes, route segments, dates, participants, photos/videos, and links to related events. Distinguish a planned route from a confirmed visit. Do not fabricate GPS tracks, visits, distances, or travel modes.

### Time and events world
Timeline and event constellation connecting people, dates, places, routes, documents, photos, and videos. Preserve source provenance and uncertainty for historical dates.

### Knowledge and documents world
Searchable documents and records with previews subject to permissions, metadata, relationships, and verified storage locations.

## Navigation and controls

- Mouse: orbit/look, pointer selection, hover hints, zoom, object focus.
- Keyboard: movement, camera rotation, interaction, escape/back, and keyboard-accessible menus.
- Touch: one-finger look/selection, pinch zoom, and an on-screen movement control where needed.
- AI guide: contextual text/voice-ready interface, concise hints, explanation of selected objects, and safe navigation assistance.
- Every control has a keyboard and accessible alternative. Respect reduced-motion preferences.

## Adaptive rendering

Use capability detection and runtime performance feedback rather than device-name assumptions. Prefer WebGPU when supported and stable; provide WebGL2 fallback. Scale render resolution, shadows, particles, post-processing, texture quality, and draw distance to measured frame time and memory pressure. Use a simplified scene on weak integrated GPUs and mobile devices. Provide a non-3D navigation fallback if graphics acceleration is unavailable. Avoid sustained high CPU/GPU load, thermal throttling, and excessive memory use.

## Application and data integration

- Reuse existing PERSON-ID, MATERIAL-ID, event, place, route, archive, and storage-provider records.
- Spatial objects are views of application entities, not a new source of truth.
- Resolve all displayed data through authorized application APIs.
- Preserve links between people, materials, events, places, routes, and storage locations.
- Distinguish local, remote, cached, unavailable, and verified-synchronized files. Never label an item synchronized unless the server confirms it.
- Keep provider storage (Google Drive, OneDrive, Yandex Disk, local storage) replaceable; the application registry remains authoritative.
- Respect quarantine, malware scanning, SHA-256 verification, backups, and recovery rules.

## Implementation sequence

1. Add the central navigable AI world to the existing site without removing existing pages.
2. Add world portals and working navigation to existing sections.
3. Add contextual AI guide and help hints.
4. Connect generation/person views to PERSON-ID.
5. Connect media galleries and storage locations to MATERIAL-ID and existing storage APIs.
6. Add geography, visit records, walking/transport routes, and map links.
7. Add timeline/event connections.
8. Add automatic graphics adaptation, mobile controls, accessibility, and performance safeguards.
9. Test on desktop and mobile, including weak integrated graphics, reduced-motion mode, no-WebGPU mode, and no-WebGL fallback.

## Acceptance criteria

- Existing routes and functions continue to work.
- The user can enter, navigate, and leave the 3D world using mouse, keyboard, and touch.
- Every active portal/tab opens a real section or reports its unavailable state honestly.
- Family records shown in the world come from the existing application and retain their IDs and permissions.
- A photo/video item can show its verified archive/storage location without duplicating the file or registry.
- Place, visit, and route data distinguish confirmed history from plans and estimates.
- Graphics quality adapts to actual runtime capability and offers a usable fallback.
- No original media is overwritten; no private family data is exposed publicly.
- No paid external service is introduced without approval.

## Repository constraints

- Work only on `core-backend-foundation`.
- Do not modify `main`.
- Do not delete or rewrite existing branches, backup refs, migrations, or production data.
- Extend the current application in place; do not create a disconnected showcase application.

## Homepage world interface

The homepage is the primary entry point to the AI world. The 3D scene is a navigational hub, not a decorative hero. Its eight visible portals lead to the real generations, events, geography, media/documents, AI MEDIA, assistant, private account, and project-status sections. The same destinations remain available through the conventional site navigation.

Portal links remain usable when WebGL or the external Three.js module is unavailable. The renderer reports its actual state; a failed renderer must never disable navigation. The homepage does not label backend operations as online unless a real authenticated API request confirms that state.

## Three-pass release verification

1. **Source and contract pass:** inspect route targets, DOM IDs, script bindings, accessibility labels, fallback behavior, and project privacy boundaries.
2. **Build and automated pass:** run JavaScript syntax checks, the AI-world portal contract check, Jekyll generation, and the generated local-link/anchor checker.
3. **Published runtime pass:** inspect the deployed homepage and versioned JavaScript/CSS assets, verify all portal destinations resolve, and confirm the published commit matches the tested branch head.

A green build alone is not proof that a live backend is deployed or that every protected operation is available. Report those states separately.
