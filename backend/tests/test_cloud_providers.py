from __future__ import annotations

import pytest

from backend.app.cloud_providers import (
    CloudProviderError,
    OneDriveProvider,
    YandexDiskProvider,
    _remote_object_name,
    build_provider,
)


def test_onedrive_chunk_size_obeys_graph_alignment():
    assert OneDriveProvider.CHUNK_BYTES % (320 * 1024) == 0
    assert OneDriveProvider.CHUNK_BYTES < 60 * 1024 * 1024


def test_onedrive_requires_folder_and_credentials(monkeypatch):
    for key in (
        "ONEDRIVE_FOLDER_ID", "ONEDRIVE_ACCESS_TOKEN",
        "ONEDRIVE_REFRESH_TOKEN", "ONEDRIVE_CLIENT_ID",
    ):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(CloudProviderError, match="onedrive_folder_id_missing"):
        OneDriveProvider()


def test_yandex_disk_requires_server_token(monkeypatch):
    monkeypatch.delenv("YANDEX_DISK_ACCESS_TOKEN", raising=False)
    with pytest.raises(CloudProviderError, match="yandex_disk_token_missing"):
        YandexDiskProvider()


def test_provider_factory_rejects_unknown_provider():
    with pytest.raises(CloudProviderError, match="unsupported_provider"):
        build_provider("not-a-provider")



def test_repair_object_name_is_unique_and_preserves_original_name():
    stable = _remote_object_name("BL-123", "family-photo.jpg")
    repaired_a = _remote_object_name("BL-123", "family-photo.jpg", force_new=True)
    repaired_b = _remote_object_name("BL-123", "family-photo.jpg", force_new=True)

    assert stable == "BL-123_family-photo.jpg"
    assert repaired_a.startswith("BL-123_repair_")
    assert repaired_a.endswith("_family-photo.jpg")
    assert repaired_b.startswith("BL-123_repair_")
    assert repaired_a != repaired_b
