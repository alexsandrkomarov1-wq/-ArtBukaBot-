# AI media restoration pipeline

## Implemented worker primitives

- backend/app/ai_media_worker.py provides fail-closed ClamAV scanning,
  Pillow-safe EXIF-aware preparation, Real-ESRGAN NCNN Vulkan neural super-resolution
  for photos (default 4×), OpenCV + scikit-image contrast/denoise/detail finishing,
  restrained Pillow brightness/color correction, frame-by-frame Real-ESRGAN
  inference for video (default 2×), FFmpeg muxing, SHA-256 calculation,
  dimension verification, and strict source/output path inequality.
- The authenticated archive enhancement route invokes this AI worker only
  after the original has passed ClamAV and its stored checksum is verified.
- The worker never writes to the original path. The derivative is scanned,
  checksum-verified, stored separately and registered with a new MATERIAL-ID
  linked to the original.
- Missing ClamAV, Real-ESRGAN executable/model weights, FFmpeg, or FFprobe is
  a hard error. There is no browser-filter fallback or pretend AI result.
- The public UI has a dedicated nature atmosphere, original generated ambient
  music and Russian voice commands. The music is synthesized locally; it is
  not a commercial radio stream.

## Deployment requirements still outstanding

The authenticated API route and MATERIAL-ID workflow are implemented, but
the public GitHub Pages site still has no deployed private backend URL or
authenticated session configuration. Therefore public visitors cannot yet
invoke the server-side Real-ESRGAN worker from the page.

Before live processing, provision a private worker host and install:
1. ClamAV / clamdscan;
2. Real-ESRGAN NCNN Vulkan executable and model weights;
3. FFmpeg and FFprobe;
4. private storage and the database;
5. HTTPS API deployment and the site's authenticated API configuration.

Do not substitute the browser's contrast filter for a missing neural model.
If the worker or model is missing, fail closed and preserve the original.

## Worker runtime requirements

Install and configure ClamAV (clamdscan), realesrgan-ncnn-vulkan with model
files, FFmpeg and FFprobe on a private worker host. Optional binary paths and
model name are configured through CORE_CLAMDSCAN_BINARY,
CORE_REALESRGAN_BINARY, CORE_REALESRGAN_MODEL, CORE_FFMPEG_BINARY,
and CORE_FFPROBE_BINARY. No credentials or model weights are committed.
The browser fallback is intentionally disabled: no neural output is shown
unless the private API returns a verified derivative.
