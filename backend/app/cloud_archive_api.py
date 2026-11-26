from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import archive_api as legacy_archive_api
from .models import ArchiveEntityLink, ArchiveItem, AuditEvent, Material, Person, StoredBlob, User, new_id
from .schemas import ArchiveItemRead, ArchiveLinkCreate, ArchiveLinkRead
from .storage import PrivateMediaStorage
from .google_drive_outbox import enqueue_google_drive_replica
from .ai_media_worker import restore_photo, restore_video, sha256_file

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


def _item_payload(item: ArchiveItem, blob: StoredBlob, material: Material) -> dict:
    return {
        "material_id": material.material_id,
        "original_material_id": material.original_material_id,
        "archive_item_id": item.archive_item_id,
        "item_type": item.item_type,
        "title": item.title,
        "record_status": item.record_status,
        "original_filename": blob.original_filename,
        "detected_mime_type": blob.detected_mime_type,
        "size_bytes": blob.size_bytes,
        "sha256": blob.sha256,
        "storage_state": blob.storage_state,
        "created_at": item.created_at,
    }


def build_archive_router(get_db, require_roles, storage_root: Path) -> APIRouter:
    router = APIRouter(prefix="/api/v1/archive", tags=["private-archive"])
    storage = PrivateMediaStorage(storage_root)
    intake_root = Path(os.getenv("CORE_MEDIA_ROOT", str(storage_root))).expanduser().resolve()
    intake_root.mkdir(parents=True, exist_ok=True)

    @router.get("/storage/health")
    def storage_health(
        _: User = Depends(require_roles("owner", "moderator", "family_member")),
    ):
        """Report the configured storage backend; never expose bucket names or secrets."""
        result = storage.health_check()
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
            storage.put_file(object_key, temp_path, mime_type)
            stored = True

            blob = StoredBlob(
                blob_id=new_id("BL"), sha256=sha256, size_bytes=size,
                detected_mime_type=mime_type, original_filename=filename,
                storage_provider=storage.provider, storage_object_key=object_key,
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
            db.flush()
            material = Material(
                material_id=new_id("M"), archive_item_id=item.archive_item_id,
                material_role="original", output_sha256=sha256,
            )
            db.add(material)
            enqueue_google_drive_replica(db, blob)
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
                    "storage_provider": storage.provider,
                    "person_id": linked_person.person_id if linked_person else None,
                }, ensure_ascii=False),
            ))
            db.commit()
            committed = True
            db.refresh(item)
            db.refresh(blob)
            db.refresh(material)
            return _item_payload(item, blob, material)
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
                    storage.delete(object_key)
                except Exception:
                    pass
            await file.close()

    @router.post("/items/{archive_item_id}/scan")
    def scan_quarantined_item(
        archive_item_id: str,
        db: Session = Depends(get_db),
        actor: User = Depends(require_roles("owner", "moderator")),
    ):
        """Scan the quarantined original with ClamAV; fail closed if scanner is unavailable."""
        row = db.execute(
            select(ArchiveItem, StoredBlob)
            .join(StoredBlob, ArchiveItem.original_blob_id == StoredBlob.blob_id)
            .where(ArchiveItem.archive_item_id == archive_item_id)
        ).first()
        if row is None:
            raise HTTPException(status_code=404, detail="Archive item not found")
        item, blob = row
        if item.record_status != "quarantined" or blob.storage_state != "quarantined":
            raise HTTPException(status_code=409, detail="Only quarantined media can be scanned")

        scanner = shutil.which(os.getenv("CORE_CLAMDSCAN_BINARY", "clamdscan"))
        if not scanner:
            raise HTTPException(status_code=503, detail="ClamAV scanner is unavailable; media remains quarantined")

        descriptor, temp_name = tempfile.mkstemp(prefix="core-scan-", suffix=Path(blob.original_filename).suffix, dir=intake_root)
        temp_path = Path(temp_name)
        digest = hashlib.sha256()
        size = 0
        try:
            os.close(descriptor)
            chunks, expected_length, _ = storage.open_stream(blob.storage_object_key)
            with temp_path.open("wb") as output:
                for chunk in chunks:
                    size += len(chunk)
                    digest.update(chunk)
                    output.write(chunk)
                output.flush()
                os.fsync(output.fileno())
            if size != expected_length or size != blob.size_bytes or digest.hexdigest() != blob.sha256:
                raise HTTPException(status_code=502, detail="Stored media integrity check failed; item remains quarantined")
            try:
                result = subprocess.run(
                    [scanner, "--no-summary", str(temp_path)],
                    check=False, capture_output=True, text=True, timeout=180, shell=False,
                )
            except (OSError, subprocess.TimeoutExpired):
                raise HTTPException(status_code=503, detail="ClamAV scan could not complete; item remains quarantined")

            if result.returncode == 0:
                item.record_status = "available"
                blob.storage_state = "verified"
                scan_status = "clean"
            elif result.returncode == 1:
                item.record_status = "infected"
                blob.storage_state = "infected"
                scan_status = "infected"
            else:
                raise HTTPException(status_code=503, detail="ClamAV scan failed; item remains quarantined")

            db.add(AuditEvent(
                event_type="archive.malware_scan_completed",
                entity_type="archive_item",
                entity_id=item.archive_item_id,
                actor_id=actor.user_id,
                details=json.dumps({
                    "blob_id": blob.blob_id,
                    "sha256": blob.sha256,
                    "scanner": "ClamAV",
                    "scan_status": scan_status,
                }, ensure_ascii=False),
            ))
            db.commit()
            return {
                "archive_item_id": item.archive_item_id,
                "material_id": db.scalar(select(Material.material_id).where(Material.archive_item_id == item.archive_item_id)),
                "scan_status": scan_status,
                "record_status": item.record_status,
                "storage_state": blob.storage_state,
            }
        finally:
            temp_path.unlink(missing_ok=True)


    @router.post("/items/{archive_item_id}/enhance")
    def enhance_archived_media(
        archive_item_id: str,
        strength: int = Form(default=65),
        start_seconds: float = Form(default=0.0),
        end_seconds: float | None = Form(default=None),
        crop_x: int | None = Form(default=None),
        crop_y: int | None = Form(default=None),
        crop_width: int | None = Form(default=None),
        crop_height: int | None = Form(default=None),
        enhance_audio: bool = Form(default=True),
        db: Session = Depends(get_db),
        actor: User = Depends(require_roles("owner", "moderator")),
    ):
        """Create a separately registered derivative after original malware verification."""
        row = db.execute(
            select(ArchiveItem, StoredBlob, Material)
            .join(StoredBlob, ArchiveItem.original_blob_id == StoredBlob.blob_id)
            .join(Material, Material.archive_item_id == ArchiveItem.archive_item_id)
            .where(ArchiveItem.archive_item_id == archive_item_id)
        ).first()
        if row is None:
            raise HTTPException(status_code=404, detail="Original archive material not found")
        original_item, original_blob, original_material = row
        if original_item.record_status != "available" or original_blob.storage_state != "verified":
            raise HTTPException(status_code=423, detail="Original must pass malware scan before enhancement")
        scanner = shutil.which(os.getenv("CORE_CLAMDSCAN_BINARY", "clamdscan"))
        if not scanner:
            raise HTTPException(status_code=503, detail="ClamAV is unavailable; no derivative was created")

        object_key = None
        stored = False
        try:
            with tempfile.TemporaryDirectory(prefix="core-enhance-", dir=intake_root) as temp_name:
                work = Path(temp_name)
                source_path = work / "original" / _safe_filename(original_blob.original_filename)
                source_path.parent.mkdir(parents=True, exist_ok=True)
                output_suffix = ".png" if original_item.item_type == "photo" else ".mp4"
                output_path = work / "derivative" / ("enhanced" + output_suffix)
                digest = hashlib.sha256()
                total = 0
                chunks, expected_length, _ = storage.open_stream(original_blob.storage_object_key)
                with source_path.open("wb") as stream:
                    for chunk in chunks:
                        total += len(chunk)
                        digest.update(chunk)
                        stream.write(chunk)
                if total != expected_length or total != original_blob.size_bytes or digest.hexdigest() != original_blob.sha256:
                    raise HTTPException(status_code=502, detail="Original integrity check failed; processing stopped")

                try:
                    if original_item.item_type == "photo":
                        result = restore_photo(source_path, output_path, scale=4, strength=strength)
                    else:
                        result = restore_video(
                            source_path, output_path, scale=2, strength=strength,
                            start_seconds=start_seconds, end_seconds=end_seconds,
                            crop_x=crop_x, crop_y=crop_y,
                            crop_width=crop_width, crop_height=crop_height,
                            enhance_audio=enhance_audio,
                        )
                except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as exc:
                    raise HTTPException(status_code=422, detail=f"Media processing failed: {exc}") from exc
                if result.source_sha256 != original_blob.sha256 or sha256_file(source_path) != original_blob.sha256:
                    raise HTTPException(status_code=502, detail="Original changed during processing; derivative was rejected")

                try:
                    scan = subprocess.run(
                        [scanner, "--no-summary", str(output_path)],
                        check=False, capture_output=True, text=True, timeout=180, shell=False,
                    )
                except (OSError, subprocess.TimeoutExpired) as exc:
                    raise HTTPException(status_code=503, detail="Derivative malware scan could not complete") from exc
                if scan.returncode != 0:
                    raise HTTPException(status_code=422, detail="Derivative failed malware scan; it was not registered or released")
                if not output_path.is_file() or output_path.stat().st_size == 0 or sha256_file(output_path) != result.output_sha256:
                    raise HTTPException(status_code=502, detail="Derivative validation failed")

                duplicate = db.scalar(select(StoredBlob).where(StoredBlob.sha256 == result.output_sha256))
                if duplicate is not None:
                    raise HTTPException(status_code=409, detail="Identical derivative content is already registered")

                object_key = f"derivatives/{result.output_sha256[:2]}/{result.output_sha256}"
                storage.put_file(object_key, output_path, result.output_mime)
                stored = True

                derivative_blob = StoredBlob(
                    blob_id=new_id("BL"), sha256=result.output_sha256,
                    size_bytes=result.output_size, detected_mime_type=result.output_mime,
                    original_filename=Path(original_blob.original_filename).stem + "-enhanced" + output_suffix,
                    storage_provider=storage.provider, storage_object_key=object_key,
                    storage_state="verified",
                )
                db.add(derivative_blob)
                db.flush()
                derivative_item = ArchiveItem(
                    archive_item_id=new_id("AR"), item_type=original_item.item_type,
                    title=((original_item.title or Path(original_blob.original_filename).stem) + " — улучшенная копия")[:300],
                    record_status="available", original_blob_id=derivative_blob.blob_id,
                    created_by_user_id=actor.user_id,
                )
                db.add(derivative_item)
                db.flush()
                derivative_material = Material(
                    material_id=new_id("M"), archive_item_id=derivative_item.archive_item_id,
                    original_material_id=original_material.material_id,
                    material_role="derivative", processing_engine=result.engine,
                    source_sha256=result.source_sha256, output_sha256=result.output_sha256,
                )
                db.add(derivative_material)
                db.add(AuditEvent(
                    event_type="archive.media_derivative_created",
                    entity_type="material", entity_id=derivative_material.material_id,
                    actor_id=actor.user_id,
                    details=json.dumps({
                        "original_material_id": original_material.material_id,
                        "derivative_material_id": derivative_material.material_id,
                        "engine": result.engine,
                        "source_sha256": result.source_sha256,
                        "output_sha256": result.output_sha256,
                        "source_size": result.source_size,
                        "output_size": result.output_size,
                        "output_width": result.output_width,
                        "output_height": result.output_height,
                    }, ensure_ascii=False),
                ))
                db.commit()
                db.refresh(derivative_item)
                db.refresh(derivative_blob)
                db.refresh(derivative_material)
                return {
                    "archive_item_id": derivative_item.archive_item_id,
                    "material_id": derivative_material.material_id,
                    "original_material_id": original_material.material_id,
                    "record_status": derivative_item.record_status,
                    "storage_state": derivative_blob.storage_state,
                    "engine": result.engine,
                    "source_sha256": result.source_sha256,
                    "output_sha256": result.output_sha256,
                    "output_size": result.output_size,
                    "output_width": result.output_width,
                    "output_height": result.output_height,
                }
        except Exception:
            db.rollback()
            if stored and object_key:
                try:
                    storage.delete(object_key)
                except Exception:
                    pass
            raise

    @router.get("/items", response_model=list[ArchiveItemRead])
    def list_archive_items(
        limit: int = 50, offset: int = 0,
        db: Session = Depends(get_db),
        _: User = Depends(require_roles("owner", "moderator", "family_member")),
    ):
        if limit < 1 or limit > 100 or offset < 0:
            raise HTTPException(status_code=422, detail="Invalid pagination")
        rows = db.execute(
            select(ArchiveItem, StoredBlob, Material)
            .join(StoredBlob, ArchiveItem.original_blob_id == StoredBlob.blob_id)
            .join(Material, Material.archive_item_id == ArchiveItem.archive_item_id)
            .where(ArchiveItem.record_status.in_(["quarantined", "available", "infected"]))
            .order_by(ArchiveItem.created_at.desc(), ArchiveItem.archive_item_id)
            .limit(limit).offset(offset)
        ).all()
        return [_item_payload(item, blob, material) for item, blob, material in rows]

    @router.get("/items/{archive_item_id}", response_model=ArchiveItemRead)
    def get_archive_item(
        archive_item_id: str, db: Session = Depends(get_db),
        _: User = Depends(require_roles("owner", "moderator", "family_member")),
    ):
        row = db.execute(
            select(ArchiveItem, StoredBlob, Material)
            .join(StoredBlob, ArchiveItem.original_blob_id == StoredBlob.blob_id)
            .join(Material, Material.archive_item_id == ArchiveItem.archive_item_id)
            .where(ArchiveItem.archive_item_id == archive_item_id,
                   ArchiveItem.record_status.in_(["quarantined", "available", "infected"]))
        ).first()
        if row is None:
            raise HTTPException(status_code=404, detail="Archive item not found")
        return _item_payload(row[0], row[1], row[2])

    @router.get("/items/{archive_item_id}/content")
    def view_archive_item(
        archive_item_id: str, db: Session = Depends(get_db),
        _: User = Depends(require_roles("owner", "moderator", "family_member")),
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
            chunks, length, stored_type = storage.open_stream(blob.storage_object_key)
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
            storage.delete(blob.storage_object_key)
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
