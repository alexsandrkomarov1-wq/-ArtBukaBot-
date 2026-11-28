# KOMAROVA_CORE

**Privacy-first, open-source family archive software.**  
KOMAROVA_CORE is being built to preserve family photographs, documents, stories, people, events and places without surrendering private family materials to a public platform.

- Public showcase: https://alexsandrkomarov1-wq.github.io/-ArtBukaBot-/
- Source code: https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-
- Project brief, architecture, support needs and honest delivery status: [docs/project-brief-and-support-case.md](docs/project-brief-and-support-case.md)
- Backend setup and API: [backend/README.md](backend/README.md)
- Cloud replication operations and current limitations: [docs/cloud-replication-operations.md](docs/cloud-replication-operations.md)

## Core preservation rules

1. Originals are immutable. Every enhanced/restored file is a separate derivative with its own MATERIAL-ID and a link to the original.
2. Files are identified and verified with SHA-256 and byte size.
3. Private family material is not part of this public repository or the public showcase.
4. Cloud copies are not considered successful until read back and hash-verified.
5. Backups must be restorable to a new destination without overwriting existing data.
6. Planned or coded functionality is not described as production-ready until tested in the target deployment.

## Technology

- Python / FastAPI backend and SQLAlchemy data model
- Alembic database migrations
- Jekyll / GitHub Pages public showcase
- Open-source media processing components, including Pillow, OpenCV/scikit-image, FFmpeg and a Real-ESRGAN NCNN Vulkan worker path
- Provider adapters for private cloud replication

## Current status

The repository contains a backend foundation, registry and security code, archive/backup primitives, cloud-provider replication code, frontend modules and automated tests. The private backend and cloud workers are **not yet confirmed as deployed production services**. AI processing requires the external binaries/models and must pass sample-media tests on the target hardware before it can be called operational.

GitHub Pages is a public showcase only. It is not the private archive server and cannot run the Python backend or background workers.

## Development branch

Active implementation is maintained on `core-backend-foundation`. The `main` branch is not the working branch for backend development.

## Contributing and support

The software and generic technical documentation are public. Family photographs, documents, account data, OAuth tokens and private metadata are not public project assets. The project seeks donated infrastructure/compute to operate and test the private service; it does not claim registered nonprofit status or promise unlimited lifetime hosting.

See the [project brief](docs/project-brief-and-support-case.md) for milestones, acceptance evidence, privacy commitments and the exact infrastructure request.
