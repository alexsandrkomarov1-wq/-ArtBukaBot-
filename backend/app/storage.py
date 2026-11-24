from __future__ import annotations

import os
from pathlib import Path
from typing import BinaryIO, Protocol

from botocore.config import Config
from botocore.exceptions import ClientError


class PrivateObjectStorage(Protocol):
    provider: str

    def put_file(self, source: Path, object_key: str, content_type: str) -> None: ...
    def delete(self, object_key: str) -> None: ...


def _validate_key(object_key: str) -> str:
    key = object_key.replace("\\", "/").strip("/")
    parts = Path(key).parts
    if not key or key.startswith("/") or any(part in {"", ".", ".."} for part in parts):
        raise ValueError("Invalid private object key")
    return key


class LocalPrivateStorage:
    provider = "local-private"

    def __init__(self, root: Path):
        self.root = Path(root).expanduser().resolve()

    def put_file(self, source: Path, object_key: str, content_type: str) -> None:
        del content_type
        key = _validate_key(object_key)
        destination = (self.root / key).resolve()
        if self.root not in destination.parents:
            raise ValueError("Object key escapes private storage root")
        destination.parent.mkdir(parents=True, exist_ok=True)
        # Atomic create-if-absent. Never replace an existing content-addressed object.
        os.link(source, destination)

    def delete(self, object_key: str) -> None:
        key = _validate_key(object_key)
        destination = (self.root / key).resolve()
        if self.root not in destination.parents:
            raise ValueError("Object key escapes private storage root")
        try:
            destination.unlink()
        except FileNotFoundError:
            pass


class S3PrivateStorage:
    provider = "neon-object-storage"

    def __init__(
        self,
        *,
        endpoint_url: str,
        region: str,
        bucket: str,
        access_key_id: str,
        secret_access_key: str,
        client=None,
    ):
        if not all((endpoint_url, region, bucket, access_key_id, secret_access_key)):
            raise ValueError("S3 storage configuration is incomplete")
        self.bucket = bucket
        self.client = client or __import__("boto3").client(
            "s3",
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
                retries={"max_attempts": 3, "mode": "standard"},
            ),
        )

    def put_file(self, source: Path, object_key: str, content_type: str) -> None:
        key = _validate_key(object_key)
        try:
            with Path(source).open("rb") as body:
                self.client.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    Body=body,
                    ContentType=content_type,
                    IfNoneMatch="*",
                )
        except ClientError as exc:
            code = str(exc.response.get("Error", {}).get("Code", ""))
            status = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
            if code in {"PreconditionFailed", "ConditionalRequestConflict"} or status in {409, 412}:
                raise FileExistsError(key) from exc
            raise

    def delete(self, object_key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=_validate_key(object_key))


def create_private_storage(root: Path, environ: dict[str, str] | None = None) -> PrivateObjectStorage:
    env = os.environ if environ is None else environ
    backend = env.get("CORE_STORAGE_BACKEND", "local").strip().lower()
    if backend == "local":
        return LocalPrivateStorage(root)
    if backend != "s3":
        raise ValueError("CORE_STORAGE_BACKEND must be 'local' or 's3'")
    return S3PrivateStorage(
        endpoint_url=env.get("CORE_S3_ENDPOINT_URL", ""),
        region=env.get("CORE_S3_REGION", ""),
        bucket=env.get("CORE_S3_BUCKET", ""),
        access_key_id=env.get("CORE_S3_ACCESS_KEY_ID", ""),
        secret_access_key=env.get("CORE_S3_SECRET_ACCESS_KEY", ""),
    )
