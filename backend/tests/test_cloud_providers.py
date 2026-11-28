from __future__ import annotations

import pytest

from backend.app.cloud_providers import (
    CloudProviderError,
    OneDriveProvider,
    YandexDiskProvider,
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
