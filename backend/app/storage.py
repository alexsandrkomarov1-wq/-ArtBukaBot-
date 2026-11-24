from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Iterator
from urllib.parse import urlparse

import boto3
from botocore.config import Config


class PrivateMediaStorage:
    """Private object storage adapter. Never creates public URLs."""

    def __init__(self, local_root: str | Path):
        self.provider = os.getenv("CORE_STORAGE_BACKEND", "local-private").strip().lower()
        self.local_root = Path(local_root).expanduser().resolve()
        self.local_root.mkdir(parents=True, exist_ok=True)
        self.client = None
        self.bucket = ""
        if self.provider in {"s3", "neon"}:
            endpoint = os.getenv("CORE_S3_ENDPOINT_URL", "").strip()
            region = os.getenv("CORE_S3_REGION", "").strip()
            self.bucket = os.getenv("CORE_S3_BUCKET", "uploads").strip()
            access_key = os.getenv("CORE_S3_ACCESS_KEY_ID", "").strip()
            secret_key = os.getenv("CORE_S3_SECRET_ACCESS_KEY", "").strip()
            missing = [
                name for name, value in (
                    ("CORE_S3_ENDPOINT_URL", endpoint),
                    ("CORE_S3_REGION", region),
                    ("CORE_S3_BUCKET", self.bucket),
                    ("CORE_S3_ACCESS_KEY_ID", access_key),
                    ("CORE_S3_SECRET_ACCESS_KEY", secret_key),
                ) if not value
            ]
            if missing:
                raise RuntimeError("S3 storage is enabled but required settings are missing: " + ", ".join(missing))
            parsed = urlparse(endpoint)
            if parsed.scheme != "https" or not parsed.netloc:
                raise RuntimeError("CORE_S3_ENDPOINT_URL must be a valid HTTPS endpoint")
            self.provider = "neon-object-storage"
            self.client = boto3.client(
                "s3",
                endpoint_url=endpoint,
                region_name=region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                config=Config(
                    signature_version="s3v4",
                    s3={"addressing_style": "path"},
                    retries={"max_attempts": 3, "mode": "standard"},
                ),
            )
        elif self.provider not in {"local", "local-private"}:
            raise RuntimeError("CORE_STORAGE_BACKEND must be 's3' or 'local-private'")

    def put_file(self, object_key: str, source: str | Path, content_type: str) -> None:
        if self.client is not None:
            with Path(source).open("rb") as stream:
                self.client.put_object(
                    Bucket=self.bucket, Key=object_key, Body=stream,
                    ContentType=content_type,
                )
            return
        destination = self._local_path(object_key)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with Path(source).open("rb") as src, destination.open("xb") as dst:
            shutil.copyfileobj(src, dst, length=1024 * 1024)

    def verify(self, object_key: str, expected_size: int) -> None:
        if self.client is not None:
            response = self.client.head_object(Bucket=self.bucket, Key=object_key)
            if int(response.get("ContentLength", -1)) != expected_size:
                raise IOError("Uploaded object size does not match the source file")
            return
        if self._local_path(object_key).stat().st_size != expected_size:
            raise IOError("Stored object size does not match the source file")

    def check(self) -> bool:
        if self.client is not None:
            self.client.list_objects_v2(Bucket=self.bucket, MaxKeys=1)
            return True
        return self.local_root.exists()

    def open_stream(self, object_key: str) -> tuple[Iterator[bytes], int, str | None]:
        if self.client is not None:
            response = self.client.get_object(Bucket=self.bucket, Key=object_key)
            body = response["Body"]
            def chunks():
                try:
                    while True:
                        chunk = body.read(1024 * 1024)
                        if not chunk:
                            break
                        yield chunk
                finally:
                    body.close()
            return chunks(), int(response.get("ContentLength", 0)), response.get("ContentType")
        path = self._local_path(object_key)
        size = path.stat().st_size
        def chunks():
            with path.open("rb") as stream:
                while True:
                    chunk = stream.read(1024 * 1024)
                    if not chunk:
                        break
                    yield chunk
        return chunks(), size, None

    def delete(self, object_key: str) -> None:
        if self.client is not None:
            self.client.delete_object(Bucket=self.bucket, Key=object_key)
            return
        path = self._local_path(object_key)
        if path.exists():
            path.unlink()

    def _local_path(self, object_key: str) -> Path:
        candidate = (self.local_root / object_key).resolve()
        if candidate != self.local_root and self.local_root not in candidate.parents:
            raise ValueError("Invalid storage object key")
        return candidate
