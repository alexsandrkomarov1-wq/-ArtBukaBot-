import pytest

from backend.app.backup import backup_database, restore_database
from backend.app.database import build_engine, run_migrations
from backend.app.models import Person


def test_sqlite_backup_restore_round_trip_on_separate_database(tmp_path):
    source_path = tmp_path / "source.sqlite3"
    backup_path = tmp_path / "backups" / "snapshot.sqlite3"
    restored_path = tmp_path / "restore" / "restored.sqlite3"
    source_engine = build_engine(f"sqlite:///{source_path}")
    try:
        run_migrations(source_engine)
        with source_engine.begin() as connection:
            connection.execute(
                Person.__table__.insert().values(
                    person_id="P-ABCDEF123456", display_name="Backup fixture",
                    status="active",
                )
            )
        backup_database(source_engine, backup_path)
    finally:
        source_engine.dispose()

    restore_database(backup_path, restored_path)
    restored_engine = build_engine(f"sqlite:///{restored_path}")
    try:
        with restored_engine.connect() as connection:
            from sqlalchemy import text
            assert connection.execute(text("PRAGMA integrity_check")).scalar_one() == "ok"
            assert connection.execute(text(
                "SELECT display_name FROM people WHERE person_id='P-ABCDEF123456'"
            )).scalar_one() == "Backup fixture"
            assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == "0003_security_controls"
    finally:
        restored_engine.dispose()



def test_restore_rejects_non_archive_sqlite_file_without_creating_destination(tmp_path):
    invalid_backup = tmp_path / "not-a-core-backup.sqlite3"
    restored_path = tmp_path / "restore" / "should-not-exist.sqlite3"
    invalid_backup.write_bytes(b"not a KOMAROVA_CORE database")
    with pytest.raises(RuntimeError, match="not a complete KOMAROVA_CORE database"):
        restore_database(invalid_backup, restored_path)
    assert not restored_path.exists()
