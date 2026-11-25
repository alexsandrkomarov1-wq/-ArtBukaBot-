# Neon AI Gateway integration

## Current architecture

KOMAROVA_CORE uses the existing Neon AI Gateway on the Neon project production branch. The gateway is branch-scoped and receives its bearer token from Neon Function runtime environment variables:

- `NEON_AI_GATEWAY_BASE_URL`
- `NEON_AI_GATEWAY_TOKEN`

The website does not contain either credential.

## Public status endpoint

A read-only Neon Function with slug `aistatus` exposes:

- `GET /status` — checks `GET /v1/models` using the injected branch credential and returns only gateway reachability, enabled model count, total model count, and the availability reason.
- `OPTIONS /status` — CORS preflight for the exact GitHub Pages origin.

The endpoint does not accept files, invoke a model, expose model credentials, or modify archive records. CORS allows only `https://alexsandrkomarov1-wq.github.io`.

## Current limitation

On 2026-11-25, the production branch gateway was enabled and an existing credential with `ai_gateway:invoke` scope was present. A diagnostic Function successfully called `/v1/models` and received HTTP 200. Every listed model returned `enabled: false` and `unavailable_reason: paid_plan_required`.

On the Neon Free plan, model inference requires a payment card and prepaid AI Gateway credits. Do not make a model call or incur paid usage until the owner explicitly authorizes credit purchase.

## Media processing is still a separate stage

Gateway status is not photo/video restoration. Before enabling file processing, implement and verify:

1. Authenticated media upload with strict size/type validation.
2. Original storage and SHA-256 verification before processing.
3. A real model/worker request, with no browser-side fake filters.
4. A separate derivative file and MATERIAL-ID linked to the original.
5. Output validation, malware scanning, and quarantine release.
6. Export only after a successful result and registry confirmation.

The current status function performs none of these steps. It is only a live connection/model-availability check.
