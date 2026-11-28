from __future__ import annotations

import hashlib
from types import SimpleNamespace

import pytest

from backend.app.google_drive_outbox import enqueue_google_drive_replica
from backend.app.models import CloudReplica, GoogleDriveOutbox
from backend.app.cloud_replication import _copy_primary
from backend.app.cloud_providers import CloudProviderError


class CollectingSession:
    def __init__(self):
        self.rows = []

    def add(self, row):
        self.rows.append(row)


class FakeStorage:
    def __init__(self, payload: bytes):
        self.payload = payload

    def open_stream(self, object_key):
        return iter((self.payload[:3], self.payload[3:])), len(self.payload), "application/octet-stream"


def test_enqueue_enabled_cloud_providers_independently_of_google(monkeypatch):
    monkeypatch.setenv("GOOGLE_DRIVE_SYNC_ENABLED", "false")
    monkeypatch.setenv("ONEDRIVE_SYNC_ENABLED", "true")
    monkeypatch.setenv("ONEDRIVE_FOLDER_ID", "folder-id")
    monkeypatch.setenv("ONEDRIVE_ACCESS_TOKEN", "test-token")
    monkeypatch.setenv("YANDEX_DISK_SYNC_ENABLED", "true")
    monkeypatch.setenv("YANDEX_DISK_ACCESS_TOKEN", "test-token")
    db = CollectingSession()
    blob = SimpleNamespace(blob_id="BL-1", sha256="a" * 64, size_bytes=9)

    enqueue_google_drive_replica(db, blob)

    assert len(db.rows) == 2
    assert {row.provider for row in db.rows if isinstance(row, CloudReplica)} == {
        "onedrive", "yandex-disk"
    }
    assert not any(isinstance(row, GoogleDriveOutbox) for row in db.rows)


def test_enqueue_does_not_store_credentials_or_queue_unconfigured_providers(monkeypatch):
    for key in (
        "GOOGLE_DRIVE_SYNC_ENABLED", "ONEDRIVE_SYNC_ENABLED",
        "ONEDRIVE_FOLDER_ID", "ONEDRIVE_ACCESS_TOKEN",
        "ONEDRIVE_REFRESH_TOKEN", "ONEDRIVE_CLIENT_ID",
        "YANDEX_DISK_SYNC_ENABLED", "YANDEX_DISK_ACCESS_TOKEN",
    ):
        monkeypatch.delenv(key, raising=False)
    db = CollectingSession()
    blob = SimpleNamespace(blob_id="BL-2", sha256="b" * 64, size_bytes=12)

    enqueue_google_drive_replica(db, blob)

    assert db.rows == []


def test_primary_copy_streams_and_verifies_integrity(tmp_path):
    payload = b"immutable original material"
    blob = SimpleNamespace(
        storage_object_key="originals/blob",
        size_bytes=len(payload),
        sha256=hashlib.sha256(payload).hexdigest(),
    )
    target = tmp_path / "source.bin"

    _copy_primary(FakeStorage(payload), blob, target)

    assert target.read_bytes() == payload


def test_primary_copy_rejects_hash_mismatch(tmp_path):
    payload = b"corrupted"
    blob = SimpleNamespace(
        storage_object_key="originals/blob",
        size_bytes=len(payload),
        sha256="0" * 64,
    )
    with pytest.raises(CloudProviderError, match="primary_blob_integrity_mismatch"):
        _copy_primary(FakeStorage(payload), blob, tmp_path / "source.bin")
