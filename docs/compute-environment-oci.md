# KOMAROVA_CORE compute environment: OCI Always Free

Status: provider selected for evaluation; account authorization and VM provisioning are pending. No cloud instance has been created yet.

## Scope

Use Oracle Cloud Infrastructure (OCI) Always Free as the first candidate for a separate compute host. Keep GitHub Pages as the public frontend and the existing Supabase project `KOMAROVA_CORE` as the existing database project. Do not create another Supabase project.

Target runtime:
- Ubuntu LTS on OCI Ampere A1 (ARM64), within Always Free limits.
- Python 3.11+ and FastAPI/Uvicorn.
- FFmpeg and FFprobe for media operations.
- ClamAV/clamdscan for quarantine scanning.
- KOMAROVA_CORE backend and a separately supervised AI worker.
- Persistent private work directory; never store originals in the public web root.

## Free-tier guardrails

- Start only with resources explicitly labelled Always Free in the OCI console.
- Target no more than 2 OCPUs and 12 GB RAM total for Ampere A1.
- Keep boot/block volumes within the free allocation.
- Do not upgrade to Pay As You Go, enable paid services, reserve paid capacity, or provision resources that are not marked Always Free without the owner's explicit approval.
- OCI requires identity/payment-method verification for account signup in many regions. The owner must complete this directly in the provider's secure signup flow; never send card data or account passwords in chat.
- Always Free capacity is not guaranteed in every home region. If capacity is unavailable, stop and report; do not switch to paid resources.
- OCI may reclaim idle Always Free compute instances under its published idle-instance policy. Maintain monitoring and backups.

## Architecture

`GitHub Pages frontend -> HTTPS -> FastAPI -> authentication/role checks -> quarantine -> ClamAV -> worker -> derivative MATERIAL-ID`

The browser must not receive database passwords, service-role keys, bootstrap secrets, JWT signing secrets, TinyFish API keys, or SSH private keys.

## Required server-side environment variables

Set these only in the host's secret/environment manager or a root-readable environment file:
- `DATABASE_URL` (private database connection string; do not commit)
- `CORE_JWT_SECRET` (random secret, at least 32 characters)
- `CORE_BOOTSTRAP_TOKEN` (one-time owner bootstrap secret)
- `CORE_MEDIA_ROOT` (private persistent path)
- `CORE_CORS_ORIGINS=https://alexsandrkomarov1-wq.github.io`
- Optional provider credentials only when their integrations are explicitly configured.

The temporary Supabase anon key is public client configuration, not a server secret. It is not a substitute for database authentication or row-level security. Do not put a Supabase service-role/secret key in frontend code.

## Media integrity requirements

- Quarantine uploads before processing.
- Verify file type and size; scan with ClamAV before worker access.
- Never overwrite or mutate the original.
- Save each derivative as a separate object with its own MATERIAL-ID and SHA-256, linked to the original MATERIAL-ID.
- If scanner or worker is unavailable, fail closed for processing and preserve the original.
- Do not report Real-ESRGAN as operational until an ARM64-compatible runtime and actual inference test have passed. OCI A1 is ARM-based and has no attached NVIDIA GPU by default; CPU/Vulkan compatibility must be tested separately.

## Deployment gates

1. Owner completes OCI account sign-in/verification in the secure browser profile.
2. Confirm home region and that an Ubuntu Ampere A1 shape is explicitly marked Always Free.
3. Create VM, SSH key, network rules, and private storage without enabling paid resources.
4. Install base runtime and run health checks.
5. Deploy backend and verify database connectivity without exposing credentials.
6. Verify ClamAV with a harmless test file and confirm quarantine behavior.
7. Verify FFmpeg/FFprobe.
8. Verify AI-worker binaries and perform an actual test on a disposable image/video; otherwise keep AI processing unavailable.
9. Configure HTTPS, CORS, rate limits, logs, backups, and restore test.
10. Connect the frontend only after the API health endpoint and auth checks pass.

## Repository constraints

- Work only on `core-backend-foundation`.
- Never modify `main`.
- Do not commit credentials, private keys, access tokens, database URLs, or user data.
- Keep deployment reversible; preserve the current frontend and backend behavior until the new API is verified.
