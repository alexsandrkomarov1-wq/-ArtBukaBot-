from __future__ import annotations

import hashlib
import io
import os
import tempfile
import time
from datetime import timedelta
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from sqlalchemy import or_, select

from .database import build_engine, build_session_factory
from .models import GoogleDriveOutbox, GoogleDriveReplica, StoredBlob, utc_now
from .storage import PrivateMediaStorage

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def _service():
    values = [os.getenv(key, "").strip() for key in (
        "GOOGLE_OAUTH_CLIENT_ID", "GOOGLE_OAUTH_CLIENT_SECRET", "GOOGLE_DRIVE_REFRESH_TOKEN"
    )]
    if not all(values):
        raise RuntimeError("google_drive_credentials_missing")
    credentials = Credentials(
        token=None, refresh_token=values[2], token_uri="https://oauth2.googleapis.com/token",
        client_id=values[0], client_secret=values[1], scopes=SCOPES,
    )
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def _copy_source(storage, blob: StoredBlob, target: Path) -> None:
    chunks, size, _ = storage.open_stream(blob.storage_object_key)
    digest = hashlib.sha256()
    written = 0
    with target.open("wb") as output:
        for chunk in chunks:
            digest.update(chunk)
            output.write(chunk)
            written += len(chunk)
    if written != blob.size_bytes or size != blob.size_bytes or digest.hexdigest() != blob.sha256:
        raise RuntimeError("primary_blob_integrity_mismatch")


def _upload_and_verify(service, blob: StoredBlob, local_path: Path, folder_id: str) -> str:
    found = service.files().list(
        q=f"'{folder_id}' in parents and appProperties has {{ key='komarova_blob_id' and value='{blob.blob_id}' }} and trashed=false",
        pageSize=10, fields="files(id,name,size,appProperties)",
    ).execute().get("files", [])
    if len(found) > 1:
        raise RuntimeError("duplicate_drive_replica_detected")
    if found:
        file_id = found[0]["id"]
    else:
        metadata = {
            "name": blob.original_filename, "mimeType": blob.detected_mime_type,
            "parents": [folder_id],
            "appProperties": {"komarova_blob_id": blob.blob_id, "komarova_sha256": blob.sha256},
        }
        media = MediaFileUpload(str(local_path), mimetype=blob.detected_mime_type, resumable=True)
        file_id = service.files().create(body=metadata, media_body=media, fields="id,size").execute()["id"]
    sink = io.BytesIO()
    downloader = MediaIoBaseDownload(sink, service.files().get_media(fileId=file_id), chunksize=1024 * 1024)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    actual = sink.getvalue()
    if len(actual) != blob.size_bytes or hashlib.sha256(actual).hexdigest() != blob.sha256:
        raise RuntimeError("drive_readback_integrity_mismatch")
    return file_id


def process_one(session_factory, storage, service, folder_id: str) -> bool:
    now = utc_now()
    with session_factory() as db:
        job = db.scalar(
            select(GoogleDriveOutbox)
            .where(or_(\n                (GoogleDriveOutbox.state.in_(("pending", "retryable_error")) & (GoogleDriveOutbox.available_at <= now)),\n                (GoogleDriveOutbox.state == "uploading") & (GoogleDriveOutbox.lease_until < now),\n            ))
            .order_by(GoogleDriveOutbox.available_at, GoogleDriveOutbox.created_at)
            .with_for_update(skip_locked=True).limit(1)
        )
        if job is None:
            return False
        job_id = job.job_id
        job.state = "uploading"
        job.lease_until = now + timedelta(minutes=15)
        job.attempts += 1
        blob = db.get(StoredBlob, job.blob_id)
        if blob is None:
            job.state = "failed"
            job.last_error_code = "source_blob_missing"
            db.commit()
            return True
        blob_data = {
            "blob_id": blob.blob_id, "sha256": blob.sha256, "size_bytes": blob.size_bytes,
            "storage_object_key": blob.storage_object_key, "original_filename": blob.original_filename,
            "detected_mime_type": blob.detected_mime_type,
        }
        replica = db.scalar(select(GoogleDriveReplica).where(GoogleDriveReplica.blob_id == blob.blob_id))
        if replica is None:
            replica = GoogleDriveReplica(
                blob_id=blob.blob_id, folder_id=folder_id, expected_sha256=blob.sha256,
                size_bytes=blob.size_bytes, state="uploading", attempt_count=job.attempts,
            )
            db.add(replica)
        else:
            replica.state = "uploading"
            replica.attempt_count = job.attempts
        db.commit()

    try:
        class BlobView:
            pass
        source = BlobView()
        for key, value in blob_data.items():
            setattr(source, key, value)
        with tempfile.TemporaryDirectory(prefix="komarova-drive-") as temp_dir:
            local_path = Path(temp_dir) / "replica.bin"
            _copy_source(storage, source, local_path)
            file_id = _upload_and_verify(service, source, local_path, folder_id)
        with session_factory() as db:
            job = db.get(GoogleDriveOutbox, job_id)
            replica = db.scalar(select(GoogleDriveReplica).where(GoogleDriveReplica.blob_id == blob_data["blob_id"]))
            replica.drive_file_id = file_id
            replica.state = "available"
            replica.verified_at = utc_now()
            replica.last_error_code = None
            job.state = "complete"
            job.lease_until = None
            job.last_error_code = None
            db.commit()
    except Exception as exc:
        code = str(exc).split(":", 1)[0][:80] or "replication_error"
        with session_factory() as db:
            job = db.get(GoogleDriveOutbox, job_id)
            replica = db.scalar(select(GoogleDriveReplica).where(GoogleDriveReplica.blob_id == blob_data["blob_id"]))
            delay = min(3600, 30 * (2 ** min(job.attempts, 7)))
            job.state = "retryable_error"
            job.available_at = utc_now() + timedelta(seconds=delay)
            job.lease_until = None
            job.last_error_code = code
            replica.state = "retryable_error"
            replica.last_error_code = code
            db.commit()
    return True


def main():
    if os.getenv("GOOGLE_DRIVE_SYNC_ENABLED", "false").lower() != "true":
        raise SystemExit("Google Drive sync is disabled; no files were changed.")
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "").strip()
    if not folder_id:
        raise SystemExit("GOOGLE_DRIVE_FOLDER_ID is required; no folder will be created automatically.")
    engine = build_engine()
    session_factory = build_session_factory(engine)
    storage = PrivateMediaStorage(Path(os.getenv("CORE_MEDIA_ROOT", "./private_media")))
    service = _service()
    try:
        while True:
            if not process_one(session_factory, storage, service, folder_id):
                time.sleep(10)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
