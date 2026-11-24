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
            assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == "0006_google_drive_oauth"
            people_columns = connection.execute(text("PRAGMA table_info(people)")).all()
            person_id_column = next(column for column in people_columns if column[1] == "person_id")
            assert person_id_column[2] == "VARCHAR(34)"
    finally:
        restored_engine.dispose()



def test_restore_rejects_non_archive_sqlite_file_without_creating_destination(tmp_path):
    invalid_backup = tmp_path / "not-a-core-backup.sqlite3"
    restored_path = tmp_path / "restore" / "should-not-exist.sqlite3"
    invalid_backup.write_bytes(b"not a KOMAROVA_CORE database")
    with pytest.raises(RuntimeError, match="not a complete KOMAROVA_CORE database"):
        restore_database(invalid_backup, restored_path)
    assert not restored_path.exists()


def test_sqlite_backup_restore_preserves_complete_identity_graph(tmp_path):
    """A restorable archive must retain people, edges, accounts, sessions and audit."""
    from sqlalchemy import text

    source_path = tmp_path / "complete-source.sqlite3"
    backup_path = tmp_path / "complete-backup" / "snapshot.sqlite3"
    restored_path = tmp_path / "complete-restore" / "restored.sqlite3"
    source_engine = build_engine(f"sqlite:///{source_path}")

    person_a = "P-" + "A" * 32
    person_b = "P-" + "B" * 32
    relationship_id = "R-" + "C" * 32
    user_id = "U-" + "D" * 32
    session_id = "S-" + "E" * 32
    event_id = "A-" + "F" * 32
    token_jti = "J" * 36

    try:
        run_migrations(source_engine)
        with source_engine.begin() as connection:
            connection.execute(text(
                "INSERT INTO people (person_id, display_name, status, created_at, updated_at) "
                "VALUES (:a, 'Archive person A', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), "
                "(:b, 'Archive person B', 'archived', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ), {"a": person_a, "b": person_b})
            connection.execute(text(
                "INSERT INTO relationships "
                "(relationship_id, from_person_id, to_person_id, relationship_type, created_at) "
                "VALUES (:rid, :a, :b, 'parent', CURRENT_TIMESTAMP)"
            ), {"rid": relationship_id, "a": person_a, "b": person_b})
            connection.execute(text(
                "INSERT INTO users "
                "(user_id, username, password_hash, role, status, created_at, updated_at) "
                "VALUES (:uid, 'archive-owner', 'argon2-test-hash', 'owner', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ), {"uid": user_id})
            connection.execute(text(
                "INSERT INTO auth_sessions "
                "(session_id, user_id, token_jti, created_at, expires_at, revoked_at) "
                "VALUES (:sid, :uid, :jti, CURRENT_TIMESTAMP, '2099-01-01 00:00:00', NULL)"
            ), {"sid": session_id, "uid": user_id, "jti": token_jti})
            connection.execute(text(
                "INSERT INTO audit_events "
                "(event_id, event_type, entity_type, entity_id, actor_id, details, occurred_at) "
                "VALUES (:eid, 'archive.test', 'person', :pid, :uid, '{\"source\":\"test\"}', CURRENT_TIMESTAMP)"
            ), {"eid": event_id, "pid": person_a, "uid": user_id})
            connection.execute(text(
                "INSERT INTO login_attempts "
                "(attempt_key, failed_attempts, window_started_at, locked_until) "
                "VALUES ('archive-test-key', 2, CURRENT_TIMESTAMP, NULL)"
            ))

        backup_database(source_engine, backup_path)
    finally:
        source_engine.dispose()

    restore_database(backup_path, restored_path)
    restored_engine = build_engine(f"sqlite:///{restored_path}")
    try:
        with restored_engine.connect() as connection:
            assert connection.exec_driver_sql("PRAGMA integrity_check").scalar_one() == "ok"
            assert connection.exec_driver_sql("PRAGMA foreign_key_check").all() == []
            assert connection.execute(text(
                "SELECT display_name, status FROM people WHERE person_id=:id"
            ), {"id": person_a}).one() == ("Archive person A", "active")
            assert connection.execute(text(
                "SELECT display_name, status FROM people WHERE person_id=:id"
            ), {"id": person_b}).one() == ("Archive person B", "archived")
            assert connection.execute(text(
                "SELECT from_person_id, to_person_id, relationship_type "
                "FROM relationships WHERE relationship_id=:id"
            ), {"id": relationship_id}).one() == (person_a, person_b, "parent")
            assert connection.execute(text(
                "SELECT username, role FROM users WHERE user_id=:id"
            ), {"id": user_id}).one() == ("archive-owner", "owner")
            assert connection.execute(text(
                "SELECT user_id, token_jti FROM auth_sessions WHERE session_id=:id"
            ), {"id": session_id}).one() == (user_id, token_jti)
            assert connection.execute(text(
                "SELECT entity_id, actor_id, details FROM audit_events WHERE event_id=:id"
            ), {"id": event_id}).one() == (person_a, user_id, '{"source":"test"}')
            assert connection.execute(text(
                "SELECT failed_attempts FROM login_attempts WHERE attempt_key='archive-test-key'"
            )).scalar_one() == 2
            assert connection.execute(text(
                "SELECT version_num FROM alembic_version"
            )).scalar_one() == "0006_google_drive_oauth"
    finally:
        restored_engine.dispose()



def test_backup_rejects_broken_foreign_key_references(tmp_path):
    from sqlalchemy import text

    source = tmp_path / "broken-source.sqlite3"
    backup = tmp_path / "backups" / "must-not-be-created.sqlite3"
    engine = build_engine(f"sqlite:///{source}")
    try:
        run_migrations(engine)
        # SQLite FK enforcement is off by default unless a connection enables it;
        # the integrity scan must still detect pre-existing orphan references.
        with engine.begin() as connection:
            connection.execute(text(
                "INSERT INTO relationships "
                "(relationship_id, from_person_id, to_person_id, relationship_type, created_at) "
                "VALUES ('R-' || printf('%032d', 1), 'P-missing-from', 'P-missing-to', "
                "'invalid-fixture', CURRENT_TIMESTAMP)"
            ))
        with pytest.raises(RuntimeError, match="foreign-key violations"):
            backup_database(engine, backup)
        assert not backup.exists()
    finally:
        engine.dispose()
