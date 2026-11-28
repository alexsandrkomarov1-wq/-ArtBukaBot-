from datetime import datetime, timezone

from PIL import Image

from backend.app.photo_metadata import (
    _dms_to_decimal,
    _gps_utc,
    _parse_offset,
    analyze_photo_metadata,
)


def test_dms_coordinates_convert_south_and_west_to_negative():
    assert _dms_to_decimal((52, 22, 12), "N") > 52
    assert _dms_to_decimal((4, 53, 0), "W") < 0


def test_exif_offset_is_parsed_without_fixed_project_offset():
    offset = _parse_offset("+02:00")
    assert offset is not None
    assert offset.utcoffset(None).total_seconds() == 7200
    assert _parse_offset("not-an-offset") is None


def test_gps_date_and_time_are_interpreted_as_utc():
    result = _gps_utc({29: "2024:07:01", 7: (12, 30, 0)})
    assert result == datetime(2024, 7, 1, 12, 30, tzinfo=timezone.utc)


def test_photo_without_gps_uses_amsterdam_only_as_labelled_assumption(tmp_path):
    source = tmp_path / "without-gps.jpg"
    image = Image.new("RGB", (16, 12), "navy")
    exif = image.getexif()
    exif[36867] = "2024:01:15 10:30:00"
    image.save(source, exif=exif)
    before = source.read_bytes()

    metadata = analyze_photo_metadata(source)

    assert metadata["timezone_default"] == "Europe/Amsterdam"
    assert metadata["timezone_status"] == "no_coordinates"
    assert metadata["time_confidence"] == "default_timezone_assumption"
    assert metadata["timestamp_source"] == "project_default_assumption"
    assert metadata["capture_datetime_local"].startswith("2024-01-15T10:30:00")
    assert metadata["capture_datetime_utc"].startswith("2024-01-15T09:30:00")
    assert metadata["original_file_unchanged"] is True
    assert source.read_bytes() == before


def test_photo_with_gps_but_unresolved_timezone_is_not_assigned_amsterdam(tmp_path, monkeypatch):
    import backend.app.photo_metadata as metadata_module

    source = tmp_path / "gps-photo.jpg"
    image = Image.new("RGB", (16, 12), "navy")
    exif = image.getexif()
    gps = {
        1: "N", 2: (52, 22, 12),
        3: "E", 4: (4, 53, 0),
    }
    exif[34853] = gps
    exif[36867] = "2024:01:15 10:30:00"
    image.save(source, exif=exif)
    monkeypatch.setattr(metadata_module, "_timezone_for_coordinates", lambda lat, lon: (None, "timezone_not_found"))

    metadata = metadata_module.analyze_photo_metadata(source)

    assert metadata["gps_status"] == "gps_present"
    assert metadata["timezone_at_location"] is None
    assert metadata["timezone_status"] == "timezone_not_found"
    assert metadata["capture_datetime_local"] is None
    assert metadata["capture_datetime_utc"] is None
    assert metadata["time_confidence"] == "missing_capture_time"
