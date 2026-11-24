# KOMAROVA_CORE — hosting, backend and domain decision

**Date:** 24 November 2026  
**Branch:** `core-backend-foundation`  
**Status:** deployment target proposed; no production server or domain purchased.

## Current verified state

- The public frontend is published through GitHub Pages from `core-backend-foundation`.
- The FastAPI backend source exists in `backend/app`, with Alembic migrations through `0005_private_media_intake`.
- The backend is not deployed. The connected Render workspace currently has no services and no Postgres instances. The previous Render create attempt returned HTTP 402 because payment information was required.
- The Neon project `wandering-unit-05985607` is in `aws-us-east-2` (Ohio). Its production branch contains only Neon Auth tables; no KOMAROVA_CORE application schema or family records were found there.
- The non-production branch `komarova-core-schema-test` has application schema revision `0005_private_media_intake`; counts checked on 24 November 2026: 0 users, 0 people, 0 audit events.
- The test branch has no deployed Neon Functions. Neon Functions run Node.js 24, while the existing API is Python/FastAPI; replacing the current backend with a separate Node rewrite solely to avoid provisioning a server is not approved.
- The public site footer now displays the project contact address `alexsandr.komarov@outlook.com`. This is a public contact address only; it is not yet an application login or verified owner-account email.

## Proposed hosting topology

1. Public site: GitHub Pages, later mapped to `www.<chosen-name>.su`.
2. API: one Linux VPS in Germany (Frankfurt/Nuremberg/Falkenstein), mapped to `api.<chosen-name>.su`.
3. Reverse proxy and TLS: Caddy or Nginx with automated Let's Encrypt certificates.
4. Runtime: existing Python FastAPI backend, systemd or Docker, health check at `/health`.
5. Database: existing Neon PostgreSQL architecture, with region/residency decision made before any real family data is inserted.
6. Media: private persistent storage only; no family media in the public GitHub repository or ephemeral container filesystem.
7. Backups: encrypted off-server backups and a tested restore procedure before production acceptance.

## VPS sizing proposal

A reasonable first server for the API and private web application is 2 vCPU, 4 GB RAM, and 80 GB NVMe. Hetzner's CPX22 Germany plan is listed at €19.49/month excluding VAT (€23.19 including 19% German VAT), with 2 vCPU, 4 GB RAM, 80 GB NVMe and 20 TB included traffic as of the checked 2026 price table. Price and availability must be reconfirmed at checkout. This is an unmanaged VPS: OS patching, firewall, monitoring and backups remain our responsibility.

No VPS has been ordered or created. Do not infer purchase approval from this proposal.

## Neon region decision

The existing Neon project is in Ohio. Neon project regions cannot be changed in place. If the family application and data are to be hosted in the EU, the supported route is a new Frankfurt-region Neon project, schema/data migration, verification, application cutover, and only then retirement of the old project. The existing production branch currently has no application records, so this decision should be made before importing real family data. Do not create the replacement project or delete the existing one without explicit approval.

## .SU domain

- The `.SU` zone is active and administered by ROSNIIROS; IANA lists its registration date as 19 September 1990.
- Before registration, confirm the exact second-level label and current registrar rules. From 1 September 2026, registrar information states that .SU registrants must complete Gosuslugi/ESIA identification or use an eligible trustee arrangement. Availability and eligibility must be checked at the chosen registrar before payment.
- Do not assume that a listed promotional price is the renewal price or that every registrar can accept a new registration.
- Domain ownership, registrar account, recovery email and DNS access must remain under the user's control.

## Production acceptance gate

Do not call the backend launched until all of the following are true:
- a VPS exists and its monthly cost is confirmed;
- deployment uses the intended branch and pinned dependencies;
- secrets are stored outside GitHub and the image;
- TLS and domain DNS are verified;
- migrations are applied only to the approved non-production database first;
- `/health`, login, bootstrap disablement, role checks, people API, archive quarantine and CORS are tested over the public HTTPS URL;
- backup and restore are verified;
- frontend points to the deployed API and no demo-only local storage is represented as server persistence;
- board and place APIs are implemented and integrated before the family board is declared live.

## Pending user decisions

- Exact domain name, e.g. `komarova.su`, `komarov-family.su`, or another name selected by the user.
- Whether the registrant has a confirmed Gosuslugi/ESIA account or requires a legitimate trustee route.
- Approval of a recurring VPS budget and provider.
- Whether the Neon database must be moved to Frankfurt before real family data is used.
