"""Durable OneDrive and Yandex Disk replication worker.

Each provider is processed independently. A failed provider never blocks another.
A replica becomes available only after a full read-back SHA-256 and size check.
"""
from __future__ import annotations

import hashlib
import os
import tempfile
import time
from datetime import timedelta
from pathlib import Path

from sqlalchemy import or_, select

from .cloud_providers import CloudProviderError, build_provider
from .database import build_engine, build_session_factory
from .models import CloudReplica, StoredBlob, utc_now
from .storage import PrivateMediaStorage


class QuotaExceeded(CloudProviderError):
    pass


def _copy_primary(storage, blob: StoredBlob, destination: Path) -> None:
    chunks, expected_size, _ = storage.open_stream(blob.storage_object_key)
    digest = hashlib.sha256()
    written = 0
    with destination.open("wb") as output:
        for chunk in chunks:
            output.write(chunk)
            digest.update(chunk)
            written += len(chunk)
    if written != blob.size_bytes or expected_size != blob.size_bytes or digest.hexdigest() != blob.sha256:
        raise CloudProviderError("primary_blob_integrity_mismatch")


def process_one(session_factory, storage, provider_name: str) -> bool:
    now = utc_now()
    with session_factory() as db:
        replica = db.scalar(
            select(CloudReplica)
            .where(
                CloudReplica.provider == provider_name,
                or_(
                    (CloudReplica.state.in_(("pending", "retryable_error"))
                     & (CloudReplica.next_attempt_at <= now)),
                    ((CloudReplica.state == "uploading") & (CloudReplica.lease_until < now)),
                ),
            )
            .order_by(CloudReplica.next_attempt_at, CloudReplica.created_at)
            .with_for_update(skip_locked=True).limit(1)
        )
        if replica is None:
            return False
        replica.state = "uploading"
        replica.lease_until = now + timedelta(minutes=30)
        replica.attempt_count += 1
        replica.last_error_code = None
        blob = db.get(StoredBlob, replica.blob_id)
        if blob is None:
            replica.state = "failed"
            replica.last_error_code = "source_blob_missing"
            replica.lease_until = None
            db.commit()
            return True
        snapshot = {
            "blob_id": blob.blob_id, "sha256": blob.sha256,
            "size_bytes": blob.size_bytes, "storage_object_key": blob.storage_object_key,
            "original_filename": blob.original_filename,
            "detected_mime_type": blob.detected_mime_type,
            "attempt_count": replica.attempt_count,
            "replica_id": replica.replica_id,
        }
        db.commit()

    try:
        provider = build_provider(provider_name)
        max_file_bytes = getattr(provider, "MAX_FILE_BYTES", None)
        if isinstance(max_file_bytes, int) and snapshot["size_bytes"] > max_file_bytes:
            raise QuotaExceeded("provider_file_size_limit")
        quota = provider.quota()
        remaining = quota.get("remaining_bytes")
        if isinstance(remaining, int) and remaining < snapshot["size_bytes"]:
            raise QuotaExceeded("provider_quota_insufficient")
        class BlobView:
            pass
        blob_view = BlobView()
        for key, value in snapshot.items():
            setattr(blob_view, key, value)
        with tempfile.TemporaryDirectory(prefix=f"komarova-{provider_name}-") as temp_dir:
            source = Path(temp_dir) / "original.bin"
            readback = Path(temp_dir) / "readback.bin"
            _copy_primary(storage, blob_view, source)
            remote_id = provider.upload(
                source, blob_id=snapshot["blob_id"],
                filename=snapshot["original_filename"], size_bytes=snapshot["size_bytes"],
            )
            read_size, read_sha256 = provider.download(remote_id, readback)
            if read_size != snapshot["size_bytes"] or read_sha256 != snapshot["sha256"]:
                raise CloudProviderError("replica_readback_integrity_mismatch")
        with session_factory() as db:
            replica = db.get(CloudReplica, snapshot["replica_id"])
            replica.remote_id = remote_id
            replica.state = "available"
            replica.verified_at = utc_now()
            replica.lease_until = None
            replica.last_error_code = None
            db.commit()
    except QuotaExceeded as exc:
        with session_factory() as db:
            replica = db.get(CloudReplica, snapshot["replica_id"])
            replica.state = "quota_blocked"
            replica.lease_until = None
            replica.last_error_code = str(exc).split(":", 1)[0][:100]
            db.commit()
    except Exception as exc:
        code = str(exc).split(":", 1)[0][:100] or "replication_error"
        with session_factory() as db:
            replica = db.get(CloudReplica, snapshot["replica_id"])
            delay = min(86400, 60 * (2 ** min(replica.attempt_count, 10)))
            replica.state = "retryable_error"
            replica.next_attempt_at = utc_now() + timedelta(seconds=delay)
            replica.lease_until = None
            replica.last_error_code = code
            db.commit()
    return True


def main() -> None:
    enabled = []
    if os.getenv("ONEDRIVE_SYNC_ENABLED", "false").strip().lower() == "true":
        enabled.append("onedrive")
    if os.getenv("YANDEX_DISK_SYNC_ENABLED", "false").strip().lower() == "true":
        enabled.append("yandex-disk")
    if not enabled:
        raise SystemExit("No cloud replication providers are enabled; no files were changed.")
    engine = build_engine()
    sessions = build_session_factory(engine)
    storage = PrivateMediaStorage(Path(os.getenv("CORE_MEDIA_ROOT", "./private_media")))
    try:
        while True:
            worked = False
            for provider_name in enabled:
                try:
                    worked = process_one(sessions, storage, provider_name) or worked
                except Exception:
                    # Provider-level configuration or outage is isolated.
                    continue
            if not worked:
                time.sleep(10)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
