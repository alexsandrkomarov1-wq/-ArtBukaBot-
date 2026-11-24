# KOMAROVA_CORE — hosting compatibility assessment

**Date:** 24 November 2026  
**Branch:** `core-backend-foundation`  
**Assessment status:** completed from published provider terms and repository source  
**Deployment status:** not deployed; no provider account or server credentials are connected.

## Executive result

The strongest zero-cost candidate is **Fondation Simafri's Free VPS for Open Source Projects**. It is a real, separately published sponsorship program, not the ordinary paid Managed VPS product. The advertised configuration is 2 vCPU, 4 GB RAM and 50 GB storage, with monitoring, system updates and nightly backups. The program is conditional on an active project using a recognized open-source licence, a named maintainer, a genuine server requirement and public acknowledgement of the sponsor.

KOMAROVA_CORE is technically close to the advertised resource envelope, but **is not currently application-ready for this program**: no `LICENSE` file was found in `core-backend-foundation`. No licence has been added or selected. Selecting a licence is a rights decision reserved to the project owner.

## Provider compatibility

| Candidate | Published offer | Technical fit | Eligibility / risks | Decision |
|---|---|---|---|---|
| Fondation Simafri — Free VPS for Open Source | 2 vCPU, 4 GB RAM, 50 GB storage; monitoring, updates, nightly backups; sponsorship while the project remains active | Good candidate for existing Python 3.11+ FastAPI API, PostgreSQL client, Docker/Linux deployment, subject to provider confirmation of Docker and persistent-volume support | Recognized open-source licence, active project, named maintainer, real server need, public acknowledgement. Repository currently has no LICENSE. | **Conditional first choice. Do not submit until licence is explicitly chosen and provider confirms stack.** |
| BlueServers Social Support | Approved projects generally receive VPS from 1 vCPU / 1 GB; annual review and possible renewal | Could run a small API if the actual VPS offer meets Python/PostgreSQL/Docker needs | Open-source projects with public code are listed as eligible, but individual/personal projects are excluded. Application asks for organization-domain email, audience statistics and evidence, plus sponsor acknowledgement. Do not invent an organization, audience or email. | **Conditional / weak fit. Not ready to apply on current evidence.** |
| Moz.su free hosting | 10 GB disk, 256 MB RAM, 50% CPU, one MySQL database; PHP 7.4/8.0, SFTP, SSL | Not compatible with the existing FastAPI backend as a server runtime; 256 MB and PHP-only documented stack are inadequate for this API. Could only host a separate simple PHP/static test page. | No support for our Python/FastAPI runtime is documented; no technical support is included. Not suitable for private family originals or core API. | **Reject as backend host. Do not put family data there.** |
| Simafri ordinary Managed VPS | Paid plans start at US$19.99/month excl. tax; Pro 2 is US$33.99/month excl. tax | Technically suitable | This is not the free sponsorship programme. | **Not a zero-cost option.** |

## Repository compatibility

The inspected branch is `core-backend-foundation`, 142 commits ahead of `main`. `main` was not modified.

Confirmed source characteristics:
- FastAPI application in `backend/app/main.py`.
- Backend README specifies Python 3.11+.
- Existing dependencies include FastAPI, Uvicorn, SQLAlchemy, Alembic, psycopg and boto3.
- Existing API includes `/health`, bootstrap/login/session controls, user roles, people registry, relationships and private-media intake quarantine.
- Existing migrations are through `0005_private_media_intake`.
- The API README explicitly states it is development software, not deployed or production-certified.
- Media upload currently quarantines originals; malware scanning, media processing worker, private preview/download routes, cloud storage adapter and browser private UI are not production-ready.
- The family board remains a browser-side prototype and is not connected to backend persistence.
- No production secrets or family data are to be committed or uploaded to a sponsor server.

## Required compatibility questions for Simafri

Before any deployment or transfer, obtain written confirmation of:
1. Python 3.11+ and FastAPI/Uvicorn support.
2. Docker/Compose support or permission to install and manage system packages.
3. Persistent disk/volume behaviour and whether 50 GB is included without hidden storage fees.
4. Whether PostgreSQL can be hosted locally or the API can securely connect to the existing Neon PostgreSQL.
5. Backup schedule, retention period, off-site location, restore procedure and whether the backups include mounted media volumes.
6. Data-centre country, data-processing terms, access by provider staff and deletion/export procedure on programme termination.
7. Whether the project qualifies as a family-heritage preservation tool and what public acknowledgement is required.

## Required gates before a live launch

A server must not be called launched until:
- eligibility and sponsorship are confirmed in writing;
- provider account and server are actually provisioned;
- the deployment target is Linux and the intended Python runtime is confirmed;
- secrets are configured outside GitHub;
- database region and residency decision is made before any real family data is inserted;
- migrations are run against a disposable test database first;
- public HTTPS `/health`, authentication, bootstrap disablement, role checks, people API, archive quarantine and CORS are tested;
- encrypted off-server backup and a restore test are demonstrated;
- the frontend is connected to the live API;
- board/map API integration is implemented before the board is described as server-backed.

## Actions deliberately not taken

- No open-source licence was selected or added.
- No provider application was submitted.
- No account was created and no server was provisioned.
- No domain was purchased or changed.
- No family data, mail, photographs or documents were uploaded.
- `main` was not changed.
