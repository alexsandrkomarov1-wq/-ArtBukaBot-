from __future__ import annotations

import os
from .models import CloudReplica, GoogleDriveOutbox, GoogleDriveReplica, utc_now


def enqueue_google_drive_replica(db, blob) -> None:
    """Write a durable replication request in the archive's current transaction."""
    if os.getenv("GOOGLE_DRIVE_SYNC_ENABLED", "false").strip().lower() != "true":
        return
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "").strip()
    if folder_id:
        db.add(GoogleDriveOutbox(blob_id=blob.blob_id, state="pending", available_at=utc_now()))
        db.add(GoogleDriveReplica(
            blob_id=blob.blob_id, folder_id=folder_id, expected_sha256=blob.sha256,
            size_bytes=blob.size_bytes, state="pending",
        ))

    # Other providers use the provider-neutral durable queue. Credentials stay
    # outside the repository and a provider is queued only when explicitly enabled.
    targets = []
    if os.getenv("ONEDRIVE_SYNC_ENABLED", "false").strip().lower() == "true":
        if os.getenv("ONEDRIVE_FOLDER_ID", "").strip() and (
            os.getenv("ONEDRIVE_ACCESS_TOKEN", "").strip()
            or (os.getenv("ONEDRIVE_REFRESH_TOKEN", "").strip()
                and os.getenv("ONEDRIVE_CLIENT_ID", "").strip())
        ):
            targets.append("onedrive")
    if os.getenv("YANDEX_DISK_SYNC_ENABLED", "false").strip().lower() == "true":
        if os.getenv("YANDEX_DISK_ACCESS_TOKEN", "").strip():
            targets.append("yandex-disk")
    for provider in targets:
        db.add(CloudReplica(
            blob_id=blob.blob_id, provider=provider,
            expected_sha256=blob.sha256, size_bytes=blob.size_bytes,
            state="pending", next_attempt_at=utc_now(),
        ))
