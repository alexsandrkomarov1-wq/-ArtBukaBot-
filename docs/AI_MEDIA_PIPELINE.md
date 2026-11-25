# AI media restoration pipeline

## Implemented worker primitives

- backend/app/ai_media_worker.py provides fail-closed ClamAV scanning,
  Real-ESRGAN NCNN image inference, frame-by-frame video inference through
  FFmpeg, SHA-256 calculation for source and output, input size/duration limits,
  and strict source/output path inequality.
- The worker never writes to the original path.
- Missing ClamAV, Real-ESRGAN, FFmpeg, or FFprobe is a hard error. There is no
  browser-filter fallback or pretend successful result.
- The public AI Media UI no longer contains Unsplash demo portraits, a fake
  before/after comparison, CSS scanner animation, Canvas filters, or a
  downloadable file labelled as enhanced.

## Not yet connected / release blockers

This module is a worker primitive, not a deployed processing service. It is
not called by an HTTP route yet. No server endpoint, malware-scanner daemon,
Real-ESRGAN executable/model weights, private production storage, or deployed
backend is currently configured.

Before enabling processing, implement the authenticated API workflow that:
1. stores and hashes the original in private quarantine;
2. runs ClamAV and records a verified clean result;
3. invokes this worker only after the clean scan;
4. stores the derivative as a separate object and verifies its hash;
5. creates a distinct MATERIAL-ID and an explicit derivative-of relation;
6. exposes derivative content/export only after all checks pass.

The current ArchiveItem/StoredBlob model uses archive/blob identifiers and
quarantine states; it does not yet provide the required MATERIAL-ID lineage
model. Do not treat ArchiveItem IDs as MATERIAL-IDs or mark files available
until the schema and scanner workflow are implemented.

## Worker runtime requirements

Install and configure ClamAV (clamdscan), realesrgan-ncnn-vulkan with model
files, FFmpeg and FFprobe on a private worker host. Optional binary paths and
model name are configured through CORE_CLAMDSCAN_BINARY,
CORE_REALESRGAN_BINARY, CORE_REALESRGAN_MODEL, CORE_FFMPEG_BINARY,
and CORE_FFPROBE_BINARY. No credentials or model weights are committed.
