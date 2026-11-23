import zipfile

import pytest

from backend.app.archive import export_archive, restore_archive, verify_archive
from backend.app.database import build_engine, run_migrations


def test_portable_archive_export_verify_and_restore(tmp_path):
    from sqlalchemy import text

    source_path = tmp_path / "source.sqlite3"
    archive_path = tmp_path / "exports" / "family-core.kca"
    restored_path = tmp_path / "restored.sqlite3"
    engine = build_engine(f"sqlite:///{source_path}")
    try:
        run_migrations(engine)
        with engine.begin() as connection:
            connection.execute(text(
                "INSERT INTO people "
                "(person_id, display_name, status, created_at, updated_at) "
                "VALUES ('P-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', 'Archive person', "
                "'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ))
        export_archive(engine, archive_path)
    finally:
        engine.dispose()

    manifest = verify_archive(archive_path)
    assert manifest["format"] == "KOMAROVA_CORE_ARCHIVE"
    assert manifest["format_version"] == 1
    assert manifest["schema_revision"] == "0004_wide_identifiers"
    assert manifest["contents"] == ["relational_database"]
    assert manifest["database_sha256"]
    assert manifest["database_size_bytes"] > 0

    restore_archive(archive_path, restored_path)
    restored = build_engine(f"sqlite:///{restored_path}")
    try:
        with restored.connect() as connection:
            assert connection.exec_driver_sql("PRAGMA integrity_check").scalar_one() == "ok"
            assert connection.exec_driver_sql("PRAGMA foreign_key_check").all() == []
            assert connection.execute(text(
                "SELECT display_name FROM people "
                "WHERE person_id='P-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'"
            )).scalar_one() == "Archive person"
    finally:
        restored.dispose()


def test_archive_rejects_tampered_database_bytes(tmp_path):
    from sqlalchemy import text

    source_path = tmp_path / "source.sqlite3"
    archive_path = tmp_path / "valid.kca"
    tampered_path = tmp_path / "tampered.kca"
    engine = build_engine(f"sqlite:///{source_path}")
    try:
        run_migrations(engine)
        with engine.begin() as connection:
            connection.execute(text(
                "INSERT INTO people "
                "(person_id, display_name, status, created_at, updated_at) "
                "VALUES ('P-BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB', 'Checksum fixture', "
                "'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ))
        export_archive(engine, archive_path)
    finally:
        engine.dispose()

    with zipfile.ZipFile(archive_path, "r") as source:
        manifest = source.read("manifest.json")
        database = bytearray(source.read("database.sqlite3"))
    database[-1] ^= 0x01
    with zipfile.ZipFile(tampered_path, "w", compression=zipfile.ZIP_DEFLATED) as target:
        target.writestr("manifest.json", manifest)
        target.writestr("database.sqlite3", database)

    with pytest.raises(ValueError, match="checksum or size verification failed"):
        verify_archive(tampered_path)


def test_archive_refuses_overwrite_and_rejects_extra_members(tmp_path):
    from sqlalchemy import text

    source_path = tmp_path / "source.sqlite3"
    archive_path = tmp_path / "archive.kca"
    engine = build_engine(f"sqlite:///{source_path}")
    try:
        run_migrations(engine)
        export_archive(engine, archive_path)
        with pytest.raises(FileExistsError):
            export_archive(engine, archive_path)
    finally:
        engine.dispose()

    expanded_path = tmp_path / "expanded.kca"
    with zipfile.ZipFile(archive_path, "r") as source, zipfile.ZipFile(expanded_path, "w") as target:
        for name in source.namelist():
            target.writestr(name, source.read(name))
        target.writestr("../unexpected.txt", "must be rejected")

    with pytest.raises(ValueError, match="exactly manifest.json and database.sqlite3"):
        verify_archive(expanded_path)


def test_restore_database_never_overwrites_existing_destination(tmp_path):
    from backend.app.backup import backup_database, restore_database

    source = tmp_path / "source.sqlite3"
    backup = tmp_path / "backup.sqlite3"
    destination = tmp_path / "existing.sqlite3"
    engine = build_engine(f"sqlite:///{source}")
    try:
        run_migrations(engine)
        backup_database(engine, backup)
    finally:
        engine.dispose()

    destination.write_bytes(b"preserve this existing file")
    with pytest.raises(FileExistsError):
        restore_archive(backup, destination)
    assert destination.read_bytes() == b"preserve this existing file"
