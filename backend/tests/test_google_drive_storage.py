from pathlib import Path

import httpx
import pytest
from fastapi import HTTPException

from backend.app import google_drive_storage


class FakeResponse:
    def __init__(self, status_code=200, payload=None, headers=None):
        self.status_code = status_code
        self._payload = payload or {}
        self.headers = headers or {}

    def json(self):
        return self._payload


def test_folder_health_requires_configured_folder(monkeypatch):
    monkeypatch.delenv("GOOGLE_DRIVE_ARCHIVE_FOLDER_ID", raising=False)
    monkeypatch.setattr(google_drive_storage, "google_drive_access_token", lambda db, user: ("token", None))
    with pytest.raises(HTTPException) as exc:
        google_drive_storage.health_check(object(), "U-TEST")
    assert exc.value.status_code == 503
    assert "GOOGLE_DRIVE_ARCHIVE_FOLDER_ID" in exc.value.detail


def test_folder_health_confirms_exact_folder(monkeypatch):
    folder_id = "folder-test"
    monkeypatch.setenv("GOOGLE_DRIVE_ARCHIVE_FOLDER_ID", folder_id)
    monkeypatch.setattr(google_drive_storage, "google_drive_access_token", lambda db, user: ("token", None))
    monkeypatch.setattr(google_drive_storage.httpx, "get", lambda *a, **k: FakeResponse(payload={
        "id": folder_id, "name": "KOMAROVA_CORE", "mimeType": "application/vnd.google-apps.folder", "trashed": False,
    }))
    result = google_drive_storage.health_check(object(), "U-TEST")
    assert result == {"status": "ok", "backend": "google-drive", "folder_id": folder_id}


def test_upload_uses_configured_folder_and_requires_google_file_id(monkeypatch, tmp_path):
    folder_id = "folder-test"
    monkeypatch.setenv("GOOGLE_DRIVE_ARCHIVE_FOLDER_ID", folder_id)
    monkeypatch.setattr(google_drive_storage, "google_drive_access_token", lambda db, user: ("token", None))
    calls = []

    def fake_post(*args, **kwargs):
        calls.append((args, kwargs))
        return FakeResponse(status_code=200, headers={"Location": "https://upload.example.test/session"})

    def fake_put(*args, **kwargs):
        list(kwargs["content"])
        return FakeResponse(status_code=200, payload={"id": "drive-file-1", "parents": [folder_id]})

    monkeypatch.setattr(google_drive_storage.httpx, "post", fake_post)
    monkeypatch.setattr(google_drive_storage.httpx, "put", fake_put)
    source = tmp_path / "portrait.jpg"
    source.write_bytes(b"\\xff\\xd8\\xfftest")
    file_id = google_drive_storage.upload_file(object(), "U-TEST", source, "portrait.jpg", "image/jpeg", source.stat().st_size)
    assert file_id == "drive-file-1"
    assert calls[0][1]["json"]["parents"] == [folder_id]


def test_upload_rejects_file_not_confirmed_in_archive_folder(monkeypatch, tmp_path):
    folder_id = "folder-test"
    monkeypatch.setenv("GOOGLE_DRIVE_ARCHIVE_FOLDER_ID", folder_id)
    monkeypatch.setattr(google_drive_storage, "google_drive_access_token", lambda db, user: ("token", None))
    monkeypatch.setattr(google_drive_storage.httpx, "post", lambda *a, **k: FakeResponse(
        headers={"Location": "https://upload.example.test/session"}))
    monkeypatch.setattr(google_drive_storage.httpx, "put", lambda *a, **k: FakeResponse(
        payload={"id": "drive-file-2", "parents": ["different-folder"]}))
    source = tmp_path / "portrait.jpg"
    source.write_bytes(b"\\xff\\xd8\\xfftest")
    with pytest.raises(HTTPException) as exc:
        google_drive_storage.upload_file(object(), "U-TEST", source, "portrait.jpg", "image/jpeg", source.stat().st_size)
    assert exc.value.status_code == 502
