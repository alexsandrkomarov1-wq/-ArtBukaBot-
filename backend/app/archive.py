"""Portable, checksummed KOMAROVA_CORE database archive format v1.

Version 1 packages the SQLite database. Media-object packaging will be added
when the project's independent file-storage layer is implemented.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.engine import Engine

from .backup import (
    _check_archive_schema,
    _check_integrity,
    backup_database,
    restore_database,
)

ARCHIVE_FORMAT = "KOMAROVA_CORE_ARCHIVE"
ARCHIVE_VERSION = 1
DATABASE_MEMBER = "database.sqlite3"
MANIFEST_MEMBER = "manifest.json"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _database_revision(path: Path) -> str:
    try:
        with sqlite3.connect(path) as connection:
            _check_integrity(connection)
            _check_archive_schema(connection)
            violations = connection.execute("PRAGMA foreign_key_check").fetchall()
            if violations:
                raise ValueError(
                    f"Archive database contains foreign-key violations: {violations[:10]}"
                )
            rows = connection.execute("SELECT version_num FROM alembic_version").fetchall()
    except sqlite3.DatabaseError as exc:
        raise ValueError("Archive database is not a readable SQLite database") from exc
    if len(rows) != 1 or not isinstance(rows[0][0], str) or not rows[0][0]:
        raise ValueError("Archive database must contain exactly one Alembic revision")
    return rows[0][0]


def export_archive(engine: Engine, destination: str | Path) -> Path:
    """Create a new ZIP archive; never replace an existing export."""
    target = Path(destination).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise FileExistsError(f"Archive destination already exists: {target}")

    with tempfile.TemporaryDirectory(prefix="komarova-archive-") as work_dir:
        database_path = Path(work_dir) / DATABASE_MEMBER
        backup_database(engine, database_path)
        manifest: dict[str, Any] = {
            "format": ARCHIVE_FORMAT,
            "format_version": ARCHIVE_VERSION,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "database_file": DATABASE_MEMBER,
            "database_size_bytes": database_path.stat().st_size,
            "database_sha256": _sha256_file(database_path),
            "schema_revision": _database_revision(database_path),
            "contents": ["relational_database"],
        }
        manifest_bytes = (
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        ).encode("utf-8")

        fd, temporary_name = tempfile.mkstemp(
            prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
        )
        os.close(fd)
        temporary_archive = Path(temporary_name)
        try:
            with zipfile.ZipFile(
                temporary_archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
            ) as archive:
                archive.write(database_path, arcname=DATABASE_MEMBER)
                archive.writestr(MANIFEST_MEMBER, manifest_bytes)
            if target.exists():
                raise FileExistsError(f"Archive destination already exists: {target}")
            os.replace(temporary_archive, target)
        except Exception:
            temporary_archive.unlink(missing_ok=True)
            raise

    return target


def _extract_verified_database(archive_path: str | Path, work_dir: Path) -> tuple[dict[str, Any], Path]:
    source = Path(archive_path).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)

    try:
        with zipfile.ZipFile(source, "r") as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) != 2 or set(names) != {MANIFEST_MEMBER, DATABASE_MEMBER}:
                raise ValueError("Archive must contain exactly manifest.json and database.sqlite3")
            if any(info.is_dir() for info in infos):
                raise ValueError("Archive must not contain directory entries")

            manifest = json.loads(archive.read(MANIFEST_MEMBER).decode("utf-8"))
            if not isinstance(manifest, dict):
                raise ValueError("Archive manifest must be a JSON object")
            if manifest.get("format") != ARCHIVE_FORMAT:
                raise ValueError("Unrecognized KOMAROVA_CORE archive format")
            if manifest.get("format_version") != ARCHIVE_VERSION:
                raise ValueError("Unsupported KOMAROVA_CORE archive version")
            if manifest.get("database_file") != DATABASE_MEMBER:
                raise ValueError("Archive manifest references an unsupported database member")

            database_info = archive.getinfo(DATABASE_MEMBER)
            expected_size = manifest.get("database_size_bytes")
            expected_hash = manifest.get("database_sha256")
            if not isinstance(expected_size, int) or expected_size < 1:
                raise ValueError("Archive manifest has an invalid database size")
            if database_info.file_size != expected_size:
                raise ValueError("Archive database size does not match its manifest")
            if not isinstance(expected_hash, str) or len(expected_hash) != 64:
                raise ValueError("Archive manifest has an invalid SHA-256 checksum")

            database_path = work_dir / DATABASE_MEMBER
            digest = hashlib.sha256()
            written = 0
            with archive.open(DATABASE_MEMBER, "r") as compressed, database_path.open("wb") as output:
                for chunk in iter(lambda: compressed.read(1024 * 1024), b""):
                    output.write(chunk)
                    digest.update(chunk)
                    written += len(chunk)

            if written != expected_size or digest.hexdigest() != expected_hash:
                raise ValueError("Archive database checksum or size verification failed")

    except zipfile.BadZipFile as exc:
        raise ValueError("Archive is not a valid ZIP file") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Archive manifest is not valid UTF-8 JSON") from exc

    actual_revision = _database_revision(database_path)
    if manifest.get("schema_revision") != actual_revision:
        raise ValueError("Archive schema revision does not match its manifest")
    return manifest, database_path


def verify_archive(archive_path: str | Path) -> dict[str, Any]:
    """Verify archive structure, checksum, SQLite integrity and schema."""
    with tempfile.TemporaryDirectory(prefix="komarova-verify-") as work_dir:
        manifest, _ = _extract_verified_database(archive_path, Path(work_dir))
        return manifest


def restore_archive(archive_path: str | Path, destination: str | Path) -> Path:
    """Restore a verified archive into a new database file; never overwrite."""
    target = Path(destination).resolve()
    if target.exists():
        raise FileExistsError(f"Restore destination already exists: {target}")
    with tempfile.TemporaryDirectory(prefix="komarova-restore-") as work_dir:
        _, database_path = _extract_verified_database(archive_path, Path(work_dir))
        return restore_database(database_path, target)
