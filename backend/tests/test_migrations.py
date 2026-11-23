from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
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
            "auth_sessions",
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
        assert version == "0002_users_sessions"
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
