from __future__ import annotations

import io
from pathlib import Path

from backend.app.storage import PrivateMediaStorage


class FakeS3Client:
    def __init__(self):
        self.objects: dict[tuple[str, str], bytes] = {}
        self.calls: list[tuple[str, dict]] = []

    def put_object(self, **kwargs):
        self.calls.append(("put_object", kwargs))
        body = kwargs["Body"]
        payload = body.read() if hasattr(body, "read") else body
        self.objects[(kwargs["Bucket"], kwargs["Key"])] = payload

    def get_object(self, **kwargs):
        self.calls.append(("get_object", kwargs))
        payload = self.objects[(kwargs["Bucket"], kwargs["Key"])]
        return {"Body": io.BytesIO(payload), "ContentLength": len(payload)}

    def delete_object(self, **kwargs):
        self.calls.append(("delete_object", kwargs))
        self.objects.pop((kwargs["Bucket"], kwargs["Key"]), None)


def test_local_storage_health_check_writes_reads_and_cleans_up(tmp_path, monkeypatch):
    monkeypatch.delenv("CORE_STORAGE_BACKEND", raising=False)
    storage = PrivateMediaStorage(tmp_path / "private")

    result = storage.health_check()

    assert result == {"status": "ok", "backend": "local-private"}
    assert list((tmp_path / "private").iterdir()) == []


def test_s3_storage_health_check_uses_supported_put_get_delete_operations(tmp_path, monkeypatch):
    monkeypatch.setenv("CORE_STORAGE_BACKEND", "local-private")
    storage = PrivateMediaStorage(tmp_path / "private")
    fake = FakeS3Client()
    storage.client = fake
    storage.bucket = "uploads"

    result = storage.health_check()

    assert result == {"status": "ok", "backend": "s3-compatible"}
    assert [name for name, _ in fake.calls] == [
        "put_object", "get_object", "delete_object"
    ]
    assert fake.objects == {}
    for name, kwargs in fake.calls:
        assert kwargs["Bucket"] == "uploads"
        assert "ServerSideEncryption" not in kwargs


def test_s3_upload_does_not_send_unsupported_encryption_header(tmp_path, monkeypatch):
    monkeypatch.setenv("CORE_STORAGE_BACKEND", "local-private")
    storage = PrivateMediaStorage(tmp_path / "private")
    fake = FakeS3Client()
    storage.client = fake
    storage.bucket = "uploads"
    source = tmp_path / "source.jpg"
    source.write_bytes(b"photo-original")

    storage.put_file("quarantine/ab/object", source, "image/jpeg")

    assert fake.objects[("uploads", "quarantine/ab/object")] == b"photo-original"
    name, kwargs = fake.calls[0]
    assert name == "put_object"
    assert kwargs["ContentType"] == "image/jpeg"
    assert "ServerSideEncryption" not in kwargs



def test_cloudflare_r2_configuration_uses_auto_region_and_path_style(tmp_path, monkeypatch):
    monkeypatch.setenv("CORE_STORAGE_BACKEND", "cloudflare-r2")
    monkeypatch.setenv("CORE_S3_ENDPOINT_URL", "https://account-id.r2.cloudflarestorage.com")
    monkeypatch.setenv("CORE_S3_REGION", "auto")
    monkeypatch.setenv("CORE_S3_BUCKET", "komarova-core-private")
    monkeypatch.setenv("CORE_S3_ACCESS_KEY_ID", "test-access-key")
    monkeypatch.setenv("CORE_S3_SECRET_ACCESS_KEY", "test-secret-key")
    captured = {}

    def fake_client(service, **kwargs):
        captured["service"] = service
        captured.update(kwargs)
        return FakeS3Client()

    monkeypatch.setattr("backend.app.storage.boto3.client", fake_client)

    storage = PrivateMediaStorage(tmp_path / "private")

    assert storage.provider == "cloudflare-r2"
    assert storage.health_check() == {"status": "ok", "backend": "cloudflare-r2"}
    assert captured["service"] == "s3"
    assert captured["endpoint_url"] == "https://account-id.r2.cloudflarestorage.com"
    assert captured["region_name"] == "auto"
    assert captured["config"].s3["addressing_style"] == "path"


def test_cloudflare_r2_rejects_non_r2_endpoint(tmp_path, monkeypatch):
    monkeypatch.setenv("CORE_STORAGE_BACKEND", "cloudflare-r2")
    monkeypatch.setenv("CORE_S3_ENDPOINT_URL", "https://s3.example.com")
    monkeypatch.setenv("CORE_S3_REGION", "auto")
    monkeypatch.setenv("CORE_S3_BUCKET", "komarova-core-private")
    monkeypatch.setenv("CORE_S3_ACCESS_KEY_ID", "test-access-key")
    monkeypatch.setenv("CORE_S3_SECRET_ACCESS_KEY", "test-secret-key")

    import pytest
    with pytest.raises(RuntimeError, match="Cloudflare R2 endpoint"):
        PrivateMediaStorage(tmp_path / "private")


def test_cloudflare_r2_requires_auto_region(tmp_path, monkeypatch):
    monkeypatch.setenv("CORE_STORAGE_BACKEND", "cloudflare-r2")
    monkeypatch.setenv("CORE_S3_ENDPOINT_URL", "https://account-id.r2.cloudflarestorage.com")
    monkeypatch.setenv("CORE_S3_REGION", "us-east-1")
    monkeypatch.setenv("CORE_S3_BUCKET", "komarova-core-private")
    monkeypatch.setenv("CORE_S3_ACCESS_KEY_ID", "test-access-key")
    monkeypatch.setenv("CORE_S3_SECRET_ACCESS_KEY", "test-secret-key")

    import pytest
    with pytest.raises(RuntimeError, match="CORE_S3_REGION=auto"):
        PrivateMediaStorage(tmp_path / "private")
