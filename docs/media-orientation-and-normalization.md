# Media orientation and format normalization

## Preservation rule
Original bytes are immutable. Orientation correction, HEIC conversion, resizing and video transcoding create separate derivatives with their own IDs, checksums and transformation provenance. Never rewrite the original to make it look upright.

## Processing pipeline
1. Receive into private quarantine and calculate SHA-256.
2. Run malware scanning in an isolated worker. No image/video decoder is invoked before a clean scan result.
3. Inspect actual media signature and metadata.
4. Photos: read EXIF Orientation and apply all eight EXIF orientation cases. Generate a size-limited WebP derivative; preserve source dimensions/orientation. HEIC/HEIF support requires pillow-heif.
5. Videos: use FFprobe to read video streams and display-matrix/rotate metadata. FFmpeg default autorotation creates a browser-compatible H.264/AAC MP4 derivative, scaled to a maximum 1920-pixel long edge. Verify output with FFprobe and require zero remaining rotation metadata.
6. Store derivative as a separate immutable blob with checksum, dimensions, source blob ID, tool versions and parameters.
7. Make a preview available only after the worker marks the derivative verified and authorization is checked.

## Development implementation boundary
backend/app/media_processing.py provides image and video normalization functions. Both require scanner_state="clean". The utility is not connected to the upload route or a background worker. Uploads still remain quarantined. Do not treat the utility as an operational pipeline.

The browser-local viewer relies on native browser decoders. Browsers normally honor EXIF orientation for supported images, but HEIC/HEIF and video display-matrix handling vary. The private worker derivative is the intended compatibility path after scanner and derivative registry are connected.

## Dependencies and acceptance
- Pillow handles EXIF-aware image decode and ImageOps.exif_transpose.
- pillow-heif registers HEIC/HEIF decoding when installed.
- FFmpeg and FFprobe must be installed on the private worker, not GitHub Pages.
- Processing must have CPU/time/memory/size limits and execute outside the web request process.
- Malformed media must fail closed. EXIF GPS and timestamps remain private.
- Tests must cover all eight EXIF orientations, original-byte preservation, HEIC/HEIF, video 90/180/270 degree rotation, missing binaries, corrupt media, timeouts and output verification.
- No preview/download route may serve quarantined content.
