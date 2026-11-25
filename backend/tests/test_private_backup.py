from __future__ import annotations

import tarfile

import pytest
from sqlalchemy import text

from backend.app.database import build_engine, run_migrations
from scripts.private_backup import create_bundle, read_and_verify, restore_bundle


def test_full_backup_contains_database_originals_and_derivatives(tmp_path):
    database = tmp_path / "source.sqlite3"
    media = tmp_path / "private-media"
    original = media / "quarantine" / "aa" / "original.bin"
    derivative = media / "derivatives" / "MATERIAL-001.webp"
    original.parent.mkdir(parents=True)
    derivative.parent.mkdir(parents=True)
    original.write_bytes(b"immutable-original")
    derivative.write_bytes(b"processed-copy")

    engine = build_engine(f"sqlite:///{database}")
    try:
        run_migrations(engine)
        with engine.begin() as connection:
            connection.execute(text(
                "INSERT INTO people (person_id, display_name, status, created_at, updated_at) "
                "VALUES ('P-BACKUP', 'Backup test', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ))
    finally:
        engine.dispose()

    bundle = create_bundle(tmp_path / "offsite" / "daily.kcb", f"sqlite:///{database}", media)
    manifest, _ = read_and_verify(bundle)
    assert manifest["media_root_contents_included"] is True
    assert len(manifest["files"]) == 3
    restored = restore_bundle(bundle, tmp_path / "restored")
    assert (restored / "media" / "quarantine" / "aa" / "original.bin").read_bytes() == b"immutable-original"
    assert (restored / "media" / "derivatives" / "MATERIAL-001.webp").read_bytes() == b"processed-copy"

    restored_engine = build_engine(f"sqlite:///{restored / 'database.sqlite3'}")
    try:
        with restored_engine.connect() as connection:
            assert connection.execute(text(
                "SELECT display_name FROM people WHERE person_id='P-BACKUP'"
            )).scalar_one() == "Backup test"
    finally:
        restored_engine.dispose()


def test_full_backup_refuses_overwrite_and_symbolic_links(tmp_path):
    database = tmp_path / "source.sqlite3"
    media = tmp_path / "private-media"
    media.mkdir()
    engine = build_engine(f"sqlite:///{database}")
    try:
        run_migrations(engine)
    finally:
        engine.dispose()

    bundle = tmp_path / "backup.kcb"
    create_bundle(bundle, f"sqlite:///{database}", media)
    with pytest.raises(FileExistsError):
        create_bundle(bundle, f"sqlite:///{database}", media)

    target = tmp_path / "outside.txt"
    target.write_text("outside", encoding="utf-8")
    try:
        (media / "link.txt").symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("Symlinks are unavailable on this platform")
    with pytest.raises(RuntimeError, match="symbolic links"):
        create_bundle(tmp_path / "link-backup.kcb", f"sqlite:///{database}", media)


def test_full_backup_restore_refuses_existing_destination(tmp_path):
    database = tmp_path / "source.sqlite3"
    engine = build_engine(f"sqlite:///{database}")
    try:
        run_migrations(engine)
    finally:
        engine.dispose()
    media = tmp_path / "private-media"
    media.mkdir()
    bundle = create_bundle(tmp_path / "backup.kcb", f"sqlite:///{database}", media)
    destination = tmp_path / "existing"
    destination.mkdir()
    with pytest.raises(FileExistsError):
        restore_bundle(bundle, destination)
