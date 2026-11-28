"""Read-only photo provenance extraction: EXIF date, GPS and location timezone.

No network geocoding or online clock is used. GPS coordinates are retained as
coordinates; a human-readable place name requires a separately approved source.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from PIL import Image

DEFAULT_TIMEZONE = "Europe/Amsterdam"


def _rational(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError, ZeroDivisionError):
        numerator, denominator = value
        return float(numerator) / float(denominator)


def _dms_to_decimal(values: Any, reference: str) -> float:
    degrees, minutes, seconds = (_rational(part) for part in values)
    result = degrees + minutes / 60.0 + seconds / 3600.0
    if reference.upper() in {"S", "W"}:
        result = -result
    return result


def _parse_exif_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, bytes):
        value = value.decode("ascii", errors="ignore")
    try:
        return datetime.strptime(str(value).strip(), "%Y:%m:%d %H:%M:%S")
    except ValueError:
        return None


def _parse_offset(value: Any) -> timezone | None:
    if not value:
        return None
    if isinstance(value, bytes):
        value = value.decode("ascii", errors="ignore")
    raw = str(value).strip()
    if len(raw) != 6 or raw[0] not in "+-" or raw[3] != ":":
        return None
    try:
        hours, minutes = int(raw[1:3]), int(raw[4:6])
        if hours > 14 or minutes > 59:
            return None
        delta = timedelta(hours=hours, minutes=minutes)
        if raw[0] == "-":
            delta = -delta
        return timezone(delta)
    except ValueError:
        return None


def _gps_utc(gps: dict) -> datetime | None:
    date_value, time_value = gps.get(29), gps.get(7)
    if not date_value or not time_value or len(time_value) != 3:
        return None
    if isinstance(date_value, bytes):
        date_value = date_value.decode("ascii", errors="ignore")
    try:
        day = datetime.strptime(str(date_value), "%Y:%m:%d").date()
        hour, minute, second = (_rational(part) for part in time_value)
        return datetime(day.year, day.month, day.day, tzinfo=timezone.utc) + timedelta(
            hours=hour, minutes=minute, seconds=second
        )
    except (TypeError, ValueError, OverflowError):
        return None


def _timezone_for_coordinates(latitude: float, longitude: float) -> tuple[str | None, str]:
    try:
        from timezonefinder import TimezoneFinder
    except ImportError:
        return None, "timezonefinder_not_installed"
    try:
        name = TimezoneFinder().timezone_at(lat=latitude, lng=longitude)
        return (name, "coordinates_resolved") if name else (None, "timezone_not_found")
    except Exception:
        return None, "timezone_lookup_failed"


def analyze_photo_metadata(path: str | Path, *, default_timezone: str = DEFAULT_TIMEZONE) -> dict:
    """Extract source metadata without changing the photo or contacting a service."""
    source = Path(path)
    with Image.open(source) as image:
        exif = image.getexif()
        gps = exif.get_ifd(0x8825) if exif and 0x8825 in exif else {}
        original_dt = _parse_exif_datetime(exif.get(0x9003) or exif.get(0x0132)) if exif else None
        offset = _parse_offset(exif.get(0x9011)) if exif else None

    latitude = longitude = None
    gps_status = "gps_missing"
    if gps and gps.get(1) and gps.get(2) and gps.get(3) and gps.get(4):
        try:
            latitude = _dms_to_decimal(gps[2], str(gps[1]))
            longitude = _dms_to_decimal(gps[4], str(gps[3]))
            if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
                raise ValueError("GPS coordinates out of range")
            gps_status = "gps_present"
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            latitude = longitude = None
            gps_status = "gps_invalid"

    gps_timestamp = _gps_utc(gps) if gps else None
    timezone_name = None
    timezone_status = "no_coordinates"
    if latitude is not None and longitude is not None:
        timezone_name, timezone_status = _timezone_for_coordinates(latitude, longitude)

    # Priority: explicit GPS UTC timestamp, explicit EXIF UTC offset, then
    # location timezone. Device default is used only when location is unknown.
    capture_utc = gps_timestamp
    timestamp_source = "exif_gps_utc" if gps_timestamp else None
    local_capture = None
    if original_dt and offset:
        local_capture = original_dt.replace(tzinfo=offset)
        if capture_utc is None:
            capture_utc = local_capture.astimezone(timezone.utc)
            timestamp_source = "exif_offset"
    elif original_dt and timezone_name:
        try:
            local_capture = original_dt.replace(tzinfo=ZoneInfo(timezone_name))
            if capture_utc is None:
                capture_utc = local_capture.astimezone(timezone.utc)
                timestamp_source = "location_timezone"
        except ZoneInfoNotFoundError:
            timezone_status = "timezone_database_missing"
    elif original_dt and latitude is None:
        try:
            local_capture = original_dt.replace(tzinfo=ZoneInfo(default_timezone))
            if capture_utc is None:
                capture_utc = local_capture.astimezone(timezone.utc)
                timestamp_source = "project_default_assumption"
        except ZoneInfoNotFoundError:
            timezone_status = "default_timezone_database_missing"

    if gps_timestamp and timezone_name:
        try:
            local_capture = gps_timestamp.astimezone(ZoneInfo(timezone_name))
        except ZoneInfoNotFoundError:
            timezone_status = "timezone_database_missing"

    return {
        "original_datetime_exif": original_dt.isoformat() if original_dt else None,
        "exif_utc_offset": offset.tzname(None) if offset else None,
        "gps_latitude": latitude,
        "gps_longitude": longitude,
        "gps_status": gps_status,
        "place_resolution": "coordinates_only" if latitude is not None else "unresolved",
        "place_name": None,
        "timezone_default": default_timezone,
        "timezone_at_location": timezone_name,
        "timezone_status": timezone_status,
        "capture_datetime_local": local_capture.isoformat() if local_capture else None,
        "capture_datetime_utc": capture_utc.isoformat() if capture_utc else None,
        "timestamp_source": timestamp_source,
        "time_confidence": (
            "gps_utc" if gps_timestamp else
            "explicit_exif_offset" if offset and original_dt else
            "location_timezone" if timezone_name and original_dt else
            "default_timezone_assumption" if original_dt else
            "missing_capture_time"
        ),
        "original_file_unchanged": True,
    }
