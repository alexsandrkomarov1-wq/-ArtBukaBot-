from pathlib import Path

import pytest
from botocore.exceptions import ClientError

from backend.app.storage import LocalPrivateStorage, S3PrivateStorage, create_private_storage


class FakeS3:
    def __init__(self):
        self.calls = []

    def put_object(self, **kwargs):
        self.calls.append(("put", kwargs))
        if getattr(self, "collision", False):
            raise ClientError(
                {"Error": {"Code": "PreconditionFailed"}, "ResponseMetadata": {"HTTPStatusCode": 412}},
                "PutObject",
            )

    def delete_object(self, **kwargs):
        self.calls.append(("delete", kwargs))


def test_local_storage_is_private_and_create_only(tmp_path):
    source = tmp_path / "source.bin"
    source.write_bytes(b"private family data")
    storage = LocalPrivateStorage(tmp_path / "objects")
    storage.put_file(source, "quarantine/aa/file.bin", "application/octet-stream")
    assert (tmp_path / "objects/quarantine/aa/file.bin").read_bytes() == source.read_bytes()
    with pytest.raises(FileExistsError):
        storage.put_file(source, "quarantine/aa/file.bin", "application/octet-stream")


def test_local_storage_rejects_path_traversal(tmp_path):
    storage = LocalPrivateStorage(tmp_path / "objects")
    source = tmp_path / "source.bin"
    source.write_bytes(b"x")
    with pytest.raises(ValueError):
        storage.put_file(source, "../outside.bin", "application/octet-stream")


def test_s3_storage_uses_private_create_only_put_and_delete(tmp_path):
    source = tmp_path / "source.bin"
    source.write_bytes(b"private family data")
    client = FakeS3()
    storage = S3PrivateStorage(
        endpoint_url="https://example.invalid",
        region="us-east-2",
        bucket="uploads",
        access_key_id="test-access",
        secret_access_key="test-secret",
        client=client,
    )
    storage.put_file(source, "quarantine/aa/file.bin", "image/jpeg")
    storage.delete("quarantine/aa/file.bin")
    assert client.calls[0][1]["Bucket"] == "uploads"
    assert client.calls[0][1]["Key"] == "quarantine/aa/file.bin"
    assert client.calls[0][1]["ContentType"] == "image/jpeg"
    assert client.calls[0][1]["IfNoneMatch"] == "*"
    assert client.calls[1] == ("delete", {"Bucket": "uploads", "Key": "quarantine/aa/file.bin"})


def test_s3_storage_maps_conditional_write_collision_to_file_exists(tmp_path):
    source = tmp_path / "source.bin"
    source.write_bytes(b"x")
    client = FakeS3()
    client.collision = True
    storage = S3PrivateStorage(
        endpoint_url="https://example.invalid",
        region="us-east-2",
        bucket="uploads",
        access_key_id="test-access",
        secret_access_key="test-secret",
        client=client,
    )
    with pytest.raises(FileExistsError):
        storage.put_file(source, "quarantine/file.bin", "image/jpeg")


def test_storage_factory_requires_complete_s3_credentials(tmp_path):
    with pytest.raises(ValueError, match="incomplete"):
        create_private_storage(tmp_path, {"CORE_STORAGE_BACKEND": "s3"})
