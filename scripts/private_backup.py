#!/usr/bin/env python3
"""Create, verify and restore a complete local KOMAROVA_CORE backup.

The bundle contains a consistent SQLite online backup plus every regular file in
CORE_MEDIA_ROOT (including quarantined originals and derivatives). It never
modifies the source database or media tree and never overwrites a destination.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from sqlalchemy.engine import make_url

from sqlalchemy import create_engine

from backend.app.backup import backup_database, restore_database

CHUNK = 1024 * 1024
FORMAT = "komarova-core-full-backup"
VERSION = 1


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def files_manifest(root: Path, prefix: str) -> list[dict]:
    rows = []
    if not root.exists():
        return rows
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(f"Backup refuses symbolic links: {path}")
        if path.is_file():
            rows.append({
                "path": (f"{prefix}/" if prefix else "") + path.relative_to(root).as_posix(),
                "size": path.stat().st_size,
                "sha256": sha256(path),
            })
    return rows


def create_bundle(destination: Path, database_url: str, media_root: Path) -> Path:
    destination = destination.expanduser().resolve()
    media_root = media_root.expanduser().resolve()
    if destination.exists():
        raise FileExistsError(destination)
    if media_root == destination or media_root in destination.parents:
        raise ValueError("Backup destination must not be inside the private media root")
    destination.parent.mkdir(parents=True, exist_ok=True)
    parsed = make_url(database_url)
    if parsed.get_backend_name() != "sqlite":
        raise RuntimeError("Full backup currently supports SQLite only; PostgreSQL needs pg_dump integration")
    db_name = parsed.database
    if not db_name or db_name == ":memory:":
        raise RuntimeError("A file-backed SQLite DATABASE_URL is required for backups")
    db_path = Path(db_name).expanduser().resolve()
    if db_path == destination or db_path in destination.parents:
        raise ValueError("Backup destination must not be inside the database directory")

    with tempfile.TemporaryDirectory(prefix="komarova-backup-") as temp_name:
        work = Path(temp_name)
        engine = create_engine(database_url)
        try:
            db_copy = backup_database(engine, work / "database.sqlite3")
        finally:
            engine.dispose()
        media_copy = work / "media"
        media_copy.mkdir()
        if media_root.exists():
            for source in media_root.rglob("*"):
                if source.is_symlink():
                    raise RuntimeError(f"Backup refuses symbolic links: {source}")
                if source.is_file():
                    relative = source.relative_to(media_root)
                    target = media_copy / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target)

        manifest = {
            "format": FORMAT,
            "version": VERSION,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "database_engine": "sqlite",
            "media_root_contents_included": True,
            "files": files_manifest(work, ""),
        }
        (work / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        temporary_bundle = destination.with_name(destination.name + ".partial")
        if temporary_bundle.exists():
            raise FileExistsError(temporary_bundle)
        try:
            with tarfile.open(temporary_bundle, "w:gz") as archive:
                archive.add(db_copy, arcname="database.sqlite3", recursive=False)
                archive.add(media_copy, arcname="media", recursive=True)
                archive.add(work / "manifest.json", arcname="manifest.json", recursive=False)
            os.replace(temporary_bundle, destination)
        except Exception:
            temporary_bundle.unlink(missing_ok=True)
            raise
    return destination


def read_and_verify(bundle: Path) -> tuple[dict, list[tarfile.TarInfo]]:
    with tarfile.open(bundle, "r:gz") as archive:
        members = archive.getmembers()
        for member in members:
            name = PurePosixPath(member.name)
            if name.is_absolute() or ".." in name.parts or member.issym() or member.islnk() or not (member.isfile() or member.isdir()):
                raise RuntimeError(f"Unsafe backup member: {member.name}")
        manifest_member = archive.getmember("manifest.json")
        manifest = json.load(archive.extractfile(manifest_member))
        if manifest.get("format") != FORMAT or manifest.get("version") != VERSION:
            raise RuntimeError("Unsupported KOMAROVA_CORE backup format")
        expected = {row["path"]: row for row in manifest.get("files", [])}
        actual = {m.name: m for m in members if m.isfile() and m.name != "manifest.json"}
        if set(expected) != set(actual):
            raise RuntimeError("Backup manifest file list does not match archive contents")
        for name, row in expected.items():
            member = actual[name]
            if member.size != row["size"]:
                raise RuntimeError(f"Backup size mismatch: {name}")
            digest = hashlib.sha256()
            stream = archive.extractfile(member)
            for chunk in iter(lambda: stream.read(CHUNK), b""):
                digest.update(chunk)
            if digest.hexdigest() != row["sha256"]:
                raise RuntimeError(f"Backup checksum mismatch: {name}")
        db_member = archive.extractfile(actual["database.sqlite3"])
        with tempfile.NamedTemporaryFile(suffix=".sqlite3") as temp_db:
            shutil.copyfileobj(db_member, temp_db)
            temp_db.flush()
            with sqlite3.connect(temp_db.name) as connection:
                result = connection.execute("PRAGMA integrity_check").fetchone()
                if not result or result[0] != "ok":
                    raise RuntimeError("Backup database failed SQLite integrity_check")
                violations = connection.execute("PRAGMA foreign_key_check").fetchall()
                if violations:
                    raise RuntimeError("Backup database has foreign-key violations")
                tables = {r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                required = {"alembic_version", "people", "relationships", "audit_events", "users", "auth_sessions", "system_state", "login_attempts", "stored_blobs", "archive_items", "materials"}
                if not required.issubset(tables):
                    raise RuntimeError("Backup database is missing required KOMAROVA_CORE tables")
        return manifest, members


def restore_bundle(bundle: Path, destination: Path) -> Path:
    destination = destination.expanduser().resolve()
    if destination.exists():
        raise FileExistsError(f"Restore destination must not exist: {destination}")
    manifest, _ = read_and_verify(bundle)
    destination.mkdir(parents=True)
    try:
        with tempfile.TemporaryDirectory(prefix="komarova-restore-") as temp_name:
            temp_root = Path(temp_name)
            with tarfile.open(bundle, "r:gz") as archive:
                archive.extractall(temp_root, filter="data")
            restore_database(temp_root / "database.sqlite3", destination / "database.sqlite3")
            restored_media = destination / "media"
            if (temp_root / "media").exists():
                shutil.copytree(temp_root / "media", restored_media)
            # Re-check the restored media against the manifest after copying.
            expected = {row["path"]: row for row in manifest["files"] if row["path"].startswith("media/")}
            for rel, row in expected.items():
                path = destination / rel
                if not path.is_file() or path.stat().st_size != row["size"] or sha256(path) != row["sha256"]:
                    raise RuntimeError(f"Restored media verification failed: {rel}")
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description="KOMAROVA_CORE complete private backup")
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create")
    create.add_argument("destination", type=Path)
    verify = sub.add_parser("verify")
    verify.add_argument("bundle", type=Path)
    restore = sub.add_parser("restore")
    restore.add_argument("bundle", type=Path)
    restore.add_argument("destination", type=Path)
    args = parser.parse_args()
    if args.command == "create":
        url = os.getenv("DATABASE_URL", "")
        media = Path(os.getenv("CORE_MEDIA_ROOT", "./private_media"))
        if not url:
            parser.error("DATABASE_URL is required")
        print(create_bundle(args.destination, url, media))
    elif args.command == "verify":
        manifest, _ = read_and_verify(args.bundle)
        print(json.dumps({"status": "verified", "created_at": manifest["created_at"], "files": len(manifest["files"])}, ensure_ascii=False))
    else:
        print(restore_bundle(args.bundle, args.destination))


if __name__ == "__main__":
    main()
