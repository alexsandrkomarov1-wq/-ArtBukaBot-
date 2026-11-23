from alembic.autogenerate import compare_metadata
from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from pathlib import Path

from sqlalchemy import inspect, select, text

from backend.app.database import Base, build_engine, run_migrations
from backend.app.models import AuditEvent, Person, RelationshipRecord


def test_fresh_database_upgrades_to_head(tmp_path, monkeypatch):
    database = tmp_path / "migration-test.sqlite3"
    engine = build_engine(f"sqlite:///{database}")
    monkeypatch.chdir(tmp_path)

    try:
        run_migrations(engine)

        inspector = inspect(engine)
        assert set(inspector.get_table_names()) == {
            "alembic_version",
            "people",
            "relationships",
            "audit_events",
            "users",
            "auth_sessions", "system_state", "login_attempts",
            "stored_blobs", "archive_items", "archive_entity_links",
        }
        assert {column["name"] for column in inspector.get_columns("people")} == {
            "person_id", "display_name", "status", "created_at", "updated_at"
        }
        assert len(inspector.get_foreign_keys("relationships")) == 2
        assert len(inspector.get_foreign_keys("auth_sessions")) == 1
        assert {index["name"] for index in inspector.get_indexes("relationships")} == {
            "ix_relationships_from_person_id", "ix_relationships_to_person_id"
        }
    finally:
        engine.dispose()


def test_migrated_schema_matches_sqlalchemy_metadata(tmp_path):
    database = tmp_path / "metadata.sqlite3"
    engine = build_engine(f"sqlite:///{database}")
    try:
        run_migrations(engine)
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            differences = compare_metadata(context, Base.metadata)
        assert differences == []
    finally:
        engine.dispose()


def test_existing_create_all_database_is_adopted_without_data_loss(tmp_path):
    database = tmp_path / "legacy.sqlite3"
    engine = build_engine(f"sqlite:///{database}")
    legacy_tables = [Person.__table__, RelationshipRecord.__table__, AuditEvent.__table__]
    try:
        # Recreate the previous release's schema, before users and sessions existed.
        Base.metadata.create_all(engine, tables=legacy_tables)
        with engine.begin() as connection:
            connection.execute(
                Person.__table__.insert().values(
                    person_id="P-1234567890AB",
                    display_name="Existing record",
                    status="active",
                )
            )

        run_migrations(engine)

        with engine.connect() as connection:
            row = connection.execute(
                select(Person.person_id, Person.display_name).where(
                    Person.person_id == "P-1234567890AB"
                )
            ).one()
            version = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        assert row.person_id == "P-1234567890AB"
        assert row.display_name == "Existing record"
        assert version == "0005_private_media_intake"
        assert inspect(engine).has_table("auth_sessions")
    finally:
        engine.dispose()


def test_partial_legacy_schema_is_rejected_without_changing_core_tables(tmp_path):
    database = tmp_path / "partial.sqlite3"
    engine = build_engine(f"sqlite:///{database}")
    try:
        with engine.begin() as connection:
            connection.exec_driver_sql(
                "CREATE TABLE people (person_id VARCHAR(14) PRIMARY KEY)"
            )
        try:
            run_migrations(engine)
        except RuntimeError as exc:
            assert "partial legacy schema" in str(exc)
        else:
            raise AssertionError("Partial legacy schema must be rejected")

        inspector = inspect(engine)
        assert "people" in inspector.get_table_names()
        assert not {"relationships", "audit_events"}.intersection(inspector.get_table_names())
        with engine.connect() as connection:
            version_rows = connection.execute(text("SELECT version_num FROM alembic_version")).all()
        assert version_rows == []
    finally:
        engine.dispose()



def test_legacy_48_bit_person_id_survives_identifier_width_migration(tmp_path):
    database = tmp_path / "identifier-upgrade.sqlite3"
    engine = build_engine(f"sqlite:///{database}")
    project_root = Path(__file__).resolve().parents[2]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "backend" / "migrations"))
    config.set_main_option("prepend_sys_path", str(project_root))

    try:
        with engine.begin() as connection:
            config.attributes["connection"] = connection
            command.upgrade(config, "0003_security_controls")

        with engine.begin() as connection:
            connection.execute(text(
                "INSERT INTO people (person_id, display_name, status, created_at, updated_at) "
                "VALUES (:id, :name, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ), {"id": "P-1234567890AB", "name": "Legacy person"})

        run_migrations(engine)

        inspector = inspect(engine)
        assert inspector.get_columns("people")[0]["type"].length == 34
        with engine.connect() as connection:
            row = connection.execute(
                select(Person.person_id, Person.display_name).where(
                    Person.person_id == "P-1234567890AB"
                )
            ).one()
            version = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        assert row.person_id == "P-1234567890AB"
        assert row.display_name == "Legacy person"
        assert version == "0005_private_media_intake"
    finally:
        engine.dispose()

def test_full_legacy_identity_graph_survives_identifier_width_migration(tmp_path):
    """Widening IDs must preserve every row and every FK edge, not just people."""
    database = tmp_path / "full-identity-graph.sqlite3"
    engine = build_engine(f"sqlite:///{database}")
    project_root = Path(__file__).resolve().parents[2]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "backend" / "migrations"))
    config.set_main_option("prepend_sys_path", str(project_root))

    person_a = "P-1234567890AB"
    person_b = "P-ABCDEF123456"
    relationship_id = "R-1234567890AB"
    user_id = "U-1234567890AB"
    session_id = "S-1234567890AB"
    event_id = "A-1234567890AB"
    token_jti = "legacy-session-token-jti-0000000001"

    try:
        # Build a real pre-0004 database, then populate every table whose
        # identifier width is changed by revision 0004.
        with engine.begin() as connection:
            config.attributes["connection"] = connection
            command.upgrade(config, "0003_security_controls")

        with engine.begin() as connection:
            connection.execute(text(
                "INSERT INTO people (person_id, display_name, status, created_at, updated_at) "
                "VALUES (:id, 'Legacy A', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), "
                "(:id2, 'Legacy B', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ), {"id": person_a, "id2": person_b})
            connection.execute(text(
                "INSERT INTO relationships "
                "(relationship_id, from_person_id, to_person_id, relationship_type, created_at) "
                "VALUES (:rid, :from_id, :to_id, 'sibling', CURRENT_TIMESTAMP)"
            ), {"rid": relationship_id, "from_id": person_a, "to_id": person_b})
            connection.execute(text(
                "INSERT INTO users "
                "(user_id, username, password_hash, role, status, created_at, updated_at) "
                "VALUES (:uid, 'legacy-owner', 'test-hash', 'owner', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ), {"uid": user_id})
            connection.execute(text(
                "INSERT INTO auth_sessions "
                "(session_id, user_id, token_jti, created_at, expires_at, revoked_at) "
                "VALUES (:sid, :uid, :jti, CURRENT_TIMESTAMP, '2099-01-01 00:00:00', NULL)"
            ), {"sid": session_id, "uid": user_id, "jti": token_jti})
            connection.execute(text(
                "INSERT INTO audit_events "
                "(event_id, event_type, entity_type, entity_id, actor_id, details, occurred_at) "
                "VALUES (:eid, 'legacy.created', 'person', :person_id, :actor_id, '{}', CURRENT_TIMESTAMP)"
            ), {"eid": event_id, "person_id": person_a, "actor_id": user_id})

        run_migrations(engine)

        with engine.connect() as connection:
            people = connection.execute(text(
                "SELECT person_id, display_name FROM people ORDER BY person_id"
            )).all()
            relationship = connection.execute(text(
                "SELECT relationship_id, from_person_id, to_person_id, relationship_type "
                "FROM relationships WHERE relationship_id = :id"
            ), {"id": relationship_id}).one()
            user = connection.execute(text(
                "SELECT user_id, username, role FROM users WHERE user_id = :id"
            ), {"id": user_id}).one()
            session = connection.execute(text(
                "SELECT session_id, user_id, token_jti FROM auth_sessions WHERE session_id = :id"
            ), {"id": session_id}).one()
            audit = connection.execute(text(
                "SELECT event_id, entity_id, actor_id, details FROM audit_events WHERE event_id = :id"
            ), {"id": event_id}).one()

            assert people == [(person_a, "Legacy A"), (person_b, "Legacy B")]
            assert tuple(relationship) == (relationship_id, person_a, person_b, "sibling")
            assert tuple(user) == (user_id, "legacy-owner", "owner")
            assert tuple(session) == (session_id, user_id, token_jti)
            assert tuple(audit) == (event_id, person_a, user_id, "{}")

            expected_widths = {
                "people": {"person_id"},
                "relationships": {"relationship_id", "from_person_id", "to_person_id"},
                "users": {"user_id"},
                "auth_sessions": {"session_id", "user_id"},
                "audit_events": {"event_id"},
                "stored_blobs": {"blob_id"},
                "archive_items": {"archive_item_id"},
                "archive_entity_links": {"link_id"},
            }
            inspector = inspect(connection)
            for table_name, column_names in expected_widths.items():
                columns = {column["name"]: column for column in inspector.get_columns(table_name)}
                for column_name in column_names:
                    expected_length = 35 if table_name in {"stored_blobs", "archive_items", "archive_entity_links"} else 34
                    assert columns[column_name]["type"].length == expected_length, (table_name, column_name)

            # SQLite reports broken references even when FK enforcement was
            # not enabled on the connection that originally inserted rows.
            violations = connection.exec_driver_sql("PRAGMA foreign_key_check").all()
            assert violations == []

            version = connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one()
            assert version == "0005_private_media_intake"
    finally:
        engine.dispose()
