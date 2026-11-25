from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterator

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from .google_drive_oauth import google_drive_access_token

DRIVE_FILES_URL = "https://www.googleapis.com/drive/v3/files"
DRIVE_UPLOAD_URL = "https://www.googleapis.com/upload/drive/v3/files"


def _folder_id() -> str:
    value = os.getenv("GOOGLE_DRIVE_ARCHIVE_FOLDER_ID", "").strip()
    if not value:
        raise HTTPException(status_code=503, detail="GOOGLE_DRIVE_ARCHIVE_FOLDER_ID is not configured")
    return value


def health_check(db: Session, user_id: str) -> dict[str, str]:
    access_token, _ = google_drive_access_token(db, user_id)
    folder_id = _folder_id()
    try:
        response = httpx.get(
            f"{DRIVE_FILES_URL}/{folder_id}",
            params={"fields": "id,name,mimeType,trashed", "supportsAllDrives": "true"},
            headers={"Authorization": f"Bearer {access_token}"}, timeout=20.0,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Google Drive archive folder check failed") from exc
    if response.status_code != 200:
        raise HTTPException(status_code=503, detail="Configured Google Drive archive folder is unavailable")
    try:
        folder = response.json()
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=502, detail="Google Drive returned invalid folder metadata") from exc
    if not isinstance(folder, dict) or folder.get("id") != folder_id or folder.get("mimeType") != "application/vnd.google-apps.folder" or folder.get("trashed"):
        raise HTTPException(status_code=503, detail="Configured Google Drive target is not an available folder")
    return {"status": "ok", "backend": "google-drive", "folder_id": folder_id}


def upload_file(db: Session, user_id: str, source: Path, filename: str, content_type: str, size_bytes: int) -> str:
    access_token, _ = google_drive_access_token(db, user_id)
    folder_id = _folder_id()
    metadata = {"name": filename, "mimeType": content_type, "parents": [folder_id],
                "description": "KOMAROVA_CORE original media; managed by archive registry"}
    try:
        session = httpx.post(
            DRIVE_UPLOAD_URL,
            params={"uploadType": "resumable", "fields": "id,name,mimeType,size,parents"},
            json=metadata,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json; charset=UTF-8",
                "X-Upload-Content-Type": content_type,
                "X-Upload-Content-Length": str(size_bytes),
            }, timeout=30.0,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Google Drive upload session could not be created") from exc
    if session.status_code not in (200, 201):
        raise HTTPException(status_code=502, detail="Google Drive rejected the archive upload request")
    upload_url = session.headers.get("Location")
    if not upload_url or not upload_url.startswith("https://"):
        raise HTTPException(status_code=502, detail="Google Drive returned an invalid upload session")

    def chunks() -> Iterator[bytes]:
        with source.open("rb") as stream:
            while True:
                chunk = stream.read(1024 * 1024)
                if not chunk:
                    break
                yield chunk

    try:
        uploaded = httpx.put(
            upload_url, content=chunks(),
            headers={"Content-Type": content_type, "Content-Length": str(size_bytes)},
            timeout=120.0,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Google Drive did not complete the archive upload") from exc
    if uploaded.status_code not in (200, 201):
        raise HTTPException(status_code=502, detail="Google Drive did not confirm the uploaded file")
    try:
        result = uploaded.json()
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=502, detail="Google Drive returned invalid upload metadata") from exc
    file_id = result.get("id") if isinstance(result, dict) else None
    parents = result.get("parents", []) if isinstance(result, dict) else []
    uploaded_size = result.get("size") if isinstance(result, dict) else None
    uploaded_type = result.get("mimeType") if isinstance(result, dict) else None
    if not file_id or folder_id not in parents or str(uploaded_size) != str(size_bytes) or uploaded_type != content_type:
        raise HTTPException(status_code=502, detail="Google Drive upload metadata did not match the original file")
    return file_id


def delete_file(db: Session, user_id: str, file_id: str) -> None:
    access_token, _ = google_drive_access_token(db, user_id)
    try:
        response = httpx.delete(
            f"{DRIVE_FILES_URL}/{file_id}",
            headers={"Authorization": f"Bearer {access_token}"}, timeout=20.0,
        )
    except httpx.HTTPError as exc:
        raise RuntimeError("Google Drive deletion request failed") from exc
    if response.status_code not in (200, 204, 404):
        raise RuntimeError("Google Drive did not confirm file deletion")


def download_file(db: Session, user_id: str, file_id: str) -> tuple[Iterator[bytes], int, str | None]:
    access_token, _ = google_drive_access_token(db, user_id)
    try:
        response = httpx.get(
            f"{DRIVE_FILES_URL}/{file_id}", params={"alt": "media"},
            headers={"Authorization": f"Bearer {access_token}"}, timeout=60.0,
        )
    except httpx.HTTPError as exc:
        raise RuntimeError("Google Drive download failed") from exc
    if response.status_code != 200:
        raise RuntimeError("Google Drive file is unavailable to this family account")
    payload = response.content
    return iter((payload,)), len(payload), response.headers.get("Content-Type")
