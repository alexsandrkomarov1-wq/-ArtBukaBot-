# Photo geography and capture-time analysis

**Project default timezone:** `Europe/Amsterdam` (IANA timezone identifier).

The project default is for records with no usable location/timezone evidence and for the interface default. It must never override a timezone inferred from a photo's own GPS coordinates.

## Required analysis order

1. Preserve the uploaded original and its checksum. Metadata extraction is read-only.
2. Read EXIF DateTimeOriginal, OffsetTimeOriginal, GPSLatitude/GPSLatitudeRef, GPSLongitude/GPSLongitudeRef, GPSDateStamp and GPSTimeStamp.
3. Convert GPS coordinates to a location timezone using an offline IANA timezone boundary database (`timezonefinder` plus the system IANA timezone database).
4. Prefer GPS UTC capture timestamp when present. Otherwise prefer the explicit EXIF UTC offset. Otherwise interpret DateTimeOriginal in the timezone resolved from the GPS coordinates.
5. If GPS is absent, use `Europe/Amsterdam` only as a clearly labelled assumption, never as a verified fact. Preserve the raw EXIF date and mark confidence.
6. Keep coordinates, resolved timezone, raw EXIF date, derived local time, derived UTC time and provenance as separate metadata fields.
7. Do not send private GPS coordinates to public reverse-geocoding services. Coordinates can be stored as location evidence; a human-readable place name must come from an approved offline gazetteer or explicit user confirmation.
8. If location/timezone cannot be resolved, retain the original values and report the missing field. Never invent a city, country or timestamp.

## Important distinction

A timezone can be resolved from coordinates without resolving an exact street address or named place. Named-place resolution is a separate step and must preserve source and confidence. EXIF timestamps can be wrong or have been edited; metadata is evidence, not proof.

## Implementation status

`backend/app/photo_metadata.py` provides read-only EXIF extraction, GPS coordinate parsing, GPS UTC timestamp parsing, timezone lookup through the optional `timezonefinder` package and explicit confidence/source labels. If `timezonefinder` is not installed, it reports that the timezone could not be resolved instead of guessing. It does not call an online clock or geocoding API, and it does not modify the source image.

The upload and enhancement routes are not yet wired to persist this metadata. Do not claim automatic archive-wide photo analysis is active until database fields/migration, upload integration and tests are completed.
