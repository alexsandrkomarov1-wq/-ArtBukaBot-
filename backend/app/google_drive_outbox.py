from __future__ import annotations

import os
from .models import GoogleDriveOutbox, GoogleDriveReplica, utc_now


def enqueue_google_drive_replica(db, blob) -> None:
    """Write a durable replication request in the archive's current transaction."""
    if os.getenv("GOOGLE_DRIVE_SYNC_ENABLED", "false").strip().lower() != "true":
        return
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "").strip()
    if not folder_id:
        return
    db.add(GoogleDriveOutbox(blob_id=blob.blob_id, state="pending", available_at=utc_now()))
    db.add(GoogleDriveReplica(
        blob_id=blob.blob_id, folder_id=folder_id, expected_sha256=blob.sha256,
        size_bytes=blob.size_bytes, state="pending",
    ))
