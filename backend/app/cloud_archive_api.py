from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import archive_api as legacy_archive_api
from .models import ArchiveEntityLink, ArchiveItem, AuditEvent, Person, StoredBlob, User, new_id
from .schemas import ArchiveItemRead, ArchiveLinkCreate, ArchiveLinkRead
from .storage import PrivateMediaStorage
from . import google_drive_storage

MAX_UPLOAD_BYTES = 100 * 1024 * 1024
CHUNK_SIZE = 1024 * 1024
PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".tif", ".tiff", ".heic", ".heif"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm", ".3gp"}


def _safe_filename(value: str | None) -> str:
    name = (value or "upload.bin").replace(chr(92), "/").split("/")[-1]
    name = "".join(ch for ch in name if ch.isprintable() and ch not in "/\r\n")
    return name.strip(" .")[:255] or "upload.bin"


def _detect_media(header: bytes, extension: str) -> tuple[str, str]:
    if extension not in PHOTO_EXTENSIONS | VIDEO_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Unsupported media extension")
    if header.startswith(bytes.fromhex("ffd8ff")):
        detected = ("photo", "image/jpeg")
    elif header.startswith(bytes.fromhex("89504e470d0a1a0a")):
        detected = ("photo", "image/png")
    elif header.startswith((b"GIF87a", b"GIF89a")):
        detected = ("photo", "image/gif")
    elif len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        detected = ("photo", "image/webp")
    elif header.startswith((bytes.fromhex("49492a00"), bytes.fromhex("4d4d002a"))):
        detected = ("photo", "image/tiff")
    elif len(header) >= 12 and header[4:8] == b"ftyp":
        brand = header[8:12]
        if brand in {b"heic", b"heix", b"hevc", b"hevx", b"mif1", b"msf1"}:
            detected = ("photo", "image/heic")
        elif extension in VIDEO_EXTENSIONS:
            detected = ("video", "video/quicktime" if extension == ".mov" else "video/mp4")
        else:
            raise HTTPException(status_code=415, detail="File signature does not match a supported photo")
    elif header.startswith(bytes.fromhex("1a45dfa3")):
        detected = ("video", "video/webm" if extension == ".webm" else "video/x-matroska")
    elif len(header) >= 12 and header[:4] == "RIFF".encode() and header[8:12] == b"AVI ":
        detected = ("video", "video/x-msvideo")
    else:
        raise HTTPException(status_code=415, detail="File content is not a supported photo or video")
    if detected[0] != ("photo" if extension in PHOTO_EXTENSIONS else "video"):
        raise HTTPException(status_code=415, detail="File extension and detected content type do not match")
    return detected


def _item_payload(item: ArchiveItem, blob: StoredBlob) -> dict:
    return {
        "archive_item_id": item.archive_item_id,
        "item_type": item.item_type,
        "title": item.title,
        "record_status": "quarantined",
        "original_filename": blob.original_filename,
        "detected_mime_type": blob.detected_mime_type,
        "size_bytes": blob.size_bytes,
        "sha256": blob.sha256,
        "storage_state": "quarantined",
        "created_at": item.created_at,
    }


def build_archive_router(get_db, require_roles, storage_root: Path) -> APIRouter:
    router = APIRouter(prefix="/api/v1/archive", tags=["private-archive"])
    storage_backend = os.getenv("CORE_STORAGE_BACKEND", "local-private").strip().lower()
    use_google_drive = storage_backend == "google-drive"
    storage = None if use_google_drive else PrivateMediaStorage(storage_root)
    storage_provider = "google-drive" if use_google_drive else storage.provider
    intake_root = Path(os.getenv("CORE_MEDIA_ROOT", str(storage_root))).expanduser().resolve()
    intake_root.mkdir(parents=True, exist_ok=True)

    @router.get("/storage/health")
    def storage_health(
        db: Session = Depends(get_db),
        actor: User = Depends(require_roles("owner", "moderator", "family_member")),
    ): 
        """Report the configured storage backend; never expose bucket names or secrets."""
        result = google_drive_storage.health_check(db, actor.user_id) if use_google_drive else storage.health_check()
        if result["status"] != "ok":
            raise HTTPException(status_code=503, detail="Configured media storage is unavailable")
        return result

    @router.post("/items", response_model=ArchiveItemRead, status_code=201)
    async def upload_media(
        file: UploadFile = File(...),
        title: str | None = Form(default=None, max_length=300),
        person_id: str | None = Form(default=None, max_length=40),
        db: Session = Depends(get_db),
        actor: User = Depends(require_roles("owner", "moderator", "family_member")),
    ):
        filename = _safe_filename(file.filename)
        extension = Path(filename).suffix.lower()
        linked_person = None
        if person_id:
            linked_person = db.get(Person, person_id.strip())
            if linked_person is None or linked_person.status != "active":
                raise HTTPException(status_code=404, detail="Active PERSON-ID not found")

        descriptor, temp_name = tempfile.mkstemp(prefix="upload-", suffix=".part", dir=intake_root)
        temp_path = Path(temp_name)
        digest = hashlib.sha256()
        size = 0
        header = bytearray()
        object_key = None
        stored = False
        committed = False
        try:
            with os.fdopen(descriptor, "wb") as destination:
                while True:
                    chunk = await file.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > legacy_archive_api.MAX_UPLOAD_BYTES:
                        raise HTTPException(status_code=413, detail="File exceeds the 100 MiB upload limit")
                    if len(header) < 64:
                        header.extend(chunk[:64 - len(header)])
                    digest.update(chunk)
                    destination.write(chunk)
                destination.flush()
                os.fsync(destination.fileno())
            if size == 0:
                raise HTTPException(status_code=422, detail="Empty files cannot be archived")
            item_type, mime_type = _detect_media(bytes(header), extension)
            sha256 = digest.hexdigest()
            existing = db.scalar(select(StoredBlob).where(StoredBlob.sha256 == sha256))
            if existing is not None:
                existing_item = db.scalar(select(ArchiveItem).where(
                    ArchiveItem.original_blob_id == existing.blob_id
                ))
                raise HTTPException(status_code=409, detail={
                    "code": "duplicate_content",
                    "message": "An identical file is already registered; no second archive item was created.",
                    "archive_item_id": existing_item.archive_item_id if existing_item else None,
                })
            object_key = f"quarantine/{sha256[:2]}/{sha256}"
            if use_google_drive:
                object_key = google_drive_storage.upload_file(db, actor.user_id, temp_path, filename, mime_type, size)
            else:
                storage.put_file(object_key, temp_path, mime_type)
            stored = True

            blob = StoredBlob(
                blob_id=new_id("BL"), sha256=sha256, size_bytes=size,
                detected_mime_type=mime_type, original_filename=filename,
                storage_provider=storage_provider, storage_object_key=object_key,
                storage_state="quarantined",
            )
            db.add(blob)
            db.flush()
            item = ArchiveItem(
                archive_item_id=new_id("AR"), item_type=item_type,
                title=(" ".join(title.split()) if title and title.strip() else None),
                record_status="quarantined", original_blob_id=blob.blob_id,
                created_by_user_id=actor.user_id,
            )
            db.add(item)
            if linked_person is not None:
                link = ArchiveEntityLink(
                    archive_item_id=item.archive_item_id, target_entity_type="person",
                    target_entity_id=linked_person.person_id, link_role="depicted",
                    confirmation_status="confirmed", created_by_user_id=actor.user_id,
                )
                db.add(link)
            db.add(AuditEvent(
                event_type="archive.media_received", entity_type="archive_item",
                entity_id=item.archive_item_id, actor_id=actor.user_id,
                details=json.dumps({
                    "blob_id": blob.blob_id, "sha256": sha256,
                    "size_bytes": size, "item_type": item_type,
                    "storage_provider": storage_provider,
                    "person_id": linked_person.person_id if linked_person else None,
                }, ensure_ascii=False),
            ))
            db.commit()
            committed = True
            db.refresh(item)
            db.refresh(blob)
            return _item_payload(item, blob)
        except HTTPException:
            db.rollback()
            raise
        except FileExistsError:
            db.rollback()
            raise HTTPException(status_code=409, detail="An object with this content hash already occupies the storage key")
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="The file was registered concurrently; retry to resolve the duplicate")
        except Exception:
            db.rollback()
            raise
        finally:
            if temp_path.exists():
                temp_path.unlink()
            if stored and not committed and object_key:
                try:
                    google_drive_storage.delete_file(db, actor.user_id, object_key) if use_google_drive else storage.delete(object_key)
                except Exception:
                    pass
            await file.close()

    @router.get("/items", response_model=list[ArchiveItemRead])
    def list_archive_items(
        limit: int = 50, offset: int = 0,
        db: Session = Depends(get_db),
        _: User = Depends(require_roles("owner", "moderator", "family_member")),
    ):
        if limit < 1 or limit > 100 or offset < 0:
            raise HTTPException(status_code=422, detail="Invalid pagination")
        rows = db.execute(
            select(ArchiveItem, StoredBlob)
            .join(StoredBlob, ArchiveItem.original_blob_id == StoredBlob.blob_id)
            .where(ArchiveItem.record_status == "quarantined")
            .order_by(ArchiveItem.created_at.desc(), ArchiveItem.archive_item_id)
            .limit(limit).offset(offset)
        ).all()
        return [_item_payload(item, blob) for item, blob in rows]

    @router.get("/items/{archive_item_id}", response_model=ArchiveItemRead)
    def get_archive_item(
        archive_item_id: str, db: Session = Depends(get_db),
        _: User = Depends(require_roles("owner", "moderator", "family_member")),
    ):
        row = db.execute(
            select(ArchiveItem, StoredBlob)
            .join(StoredBlob, ArchiveItem.original_blob_id == StoredBlob.blob_id)
            .where(ArchiveItem.archive_item_id == archive_item_id,
                   ArchiveItem.record_status == "quarantined")
        ).first()
        if row is None:
            raise HTTPException(status_code=404, detail="Archive item not found")
        return _item_payload(row[0], row[1])

    @router.get("/items/{archive_item_id}/content")
    def view_archive_item(
        archive_item_id: str, db: Session = Depends(get_db),
        actor: User = Depends(require_roles("owner", "moderator", "family_member")),
    ):
        row = db.execute(
            select(ArchiveItem, StoredBlob)
            .join(StoredBlob, ArchiveItem.original_blob_id == StoredBlob.blob_id)
            .where(ArchiveItem.archive_item_id == archive_item_id)
        ).first()
        if row is None:
            raise HTTPException(status_code=404, detail="Archive item not found")
        item, blob = row
        # Fail closed: no original may leave quarantine until a scanner and
        # verification workflow explicitly marks both records as released.
        if item.record_status != "available" or blob.storage_state != "verified":
            raise HTTPException(
                status_code=423,
                detail="Media is quarantined and cannot be viewed before malware scanning and verification",
            )
        try:
            chunks, length, stored_type = (google_drive_storage.download_file(db, actor.user_id, blob.storage_object_key)
                                           if blob.storage_provider == "google-drive"
                                           else storage.open_stream(blob.storage_object_key))
        except Exception:
            raise HTTPException(status_code=404, detail="Stored media object is unavailable")
        filename = quote(blob.original_filename, safe="")
        return StreamingResponse(
            chunks, media_type=stored_type or blob.detected_mime_type,
            headers={
                "Content-Length": str(length),
                "Content-Disposition": f"inline; filename*=UTF-8''{filename}",
                "Cache-Control": "private, no-store",
                "X-Content-Type-Options": "nosniff",
            },
        )

    @router.post("/items/{archive_item_id}/links", response_model=ArchiveLinkRead, status_code=201)
    def link_person(
        archive_item_id: str, payload: ArchiveLinkCreate,
        db: Session = Depends(get_db),
        actor: User = Depends(require_roles("owner", "moderator", "family_member")),
    ):
        item = db.get(ArchiveItem, archive_item_id)
        if item is None or item.record_status != "quarantined":
            raise HTTPException(status_code=404, detail="Archive item not found")
        person = db.get(Person, payload.target_entity_id)
        if person is None or person.status != "active":
            raise HTTPException(status_code=404, detail="Active PERSON-ID not found")
        link = ArchiveEntityLink(
            archive_item_id=item.archive_item_id, target_entity_type="person",
            target_entity_id=person.person_id, link_role=payload.link_role,
            confirmation_status="confirmed", source_note=payload.source_note,
            created_by_user_id=actor.user_id,
        )
        try:
            db.add(link)
            db.flush()
            db.add(AuditEvent(
                event_type="archive.person_linked", entity_type="archive_item",
                entity_id=item.archive_item_id, actor_id=actor.user_id,
                details=json.dumps({"person_id": person.person_id, "link_role": payload.link_role}),
            ))
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="This person link already exists")
        db.refresh(link)
        return link

    @router.get("/items/{archive_item_id}/links", response_model=list[ArchiveLinkRead])
    def list_item_links(
        archive_item_id: str, db: Session = Depends(get_db),
        _: User = Depends(require_roles("owner", "moderator", "family_member")),
    ):
        if db.get(ArchiveItem, archive_item_id) is None:
            raise HTTPException(status_code=404, detail="Archive item not found")
        return list(db.scalars(
            select(ArchiveEntityLink).where(ArchiveEntityLink.archive_item_id == archive_item_id)
            .order_by(ArchiveEntityLink.created_at, ArchiveEntityLink.link_id)
        ).all())

    @router.delete("/items/{archive_item_id}")
    def delete_archive_item(
        archive_item_id: str, db: Session = Depends(get_db),
        actor: User = Depends(require_roles("owner", "moderator")),
    ):
        row = db.execute(
            select(ArchiveItem, StoredBlob)
            .join(StoredBlob, ArchiveItem.original_blob_id == StoredBlob.blob_id)
            .where(ArchiveItem.archive_item_id == archive_item_id,
                   ArchiveItem.record_status == "quarantined")
        ).first()
        if row is None:
            raise HTTPException(status_code=404, detail="Archive item not found")
        item, blob = row
        item.record_status = "deleting"
        blob.storage_state = "deleting"
        db.add(AuditEvent(
            event_type="archive.media_delete_started", entity_type="archive_item",
            entity_id=item.archive_item_id, actor_id=actor.user_id,
            details=json.dumps({"blob_id": blob.blob_id, "provider": blob.storage_provider}),
        ))
        db.commit()
        try:
            google_drive_storage.delete_file(db, actor.user_id, blob.storage_object_key) if blob.storage_provider == "google-drive" else storage.delete(blob.storage_object_key)
        except Exception:
            item.record_status = "delete_failed"
            blob.storage_state = "delete_failed"
            db.add(AuditEvent(
                event_type="archive.media_delete_failed", entity_type="archive_item",
                entity_id=item.archive_item_id, actor_id=actor.user_id,
                details=json.dumps({"blob_id": blob.blob_id}),
            ))
            db.commit()
            raise HTTPException(status_code=502, detail="Storage deletion failed; item retained for recovery")
        item.record_status = "deleted"
        blob.storage_state = "deleted"
        db.add(AuditEvent(
            event_type="archive.media_deleted", entity_type="archive_item",
            entity_id=item.archive_item_id, actor_id=actor.user_id,
            details=json.dumps({"blob_id": blob.blob_id}),
        ))
        db.commit()
        return {"status": "deleted", "archive_item_id": item.archive_item_id}

    return router
