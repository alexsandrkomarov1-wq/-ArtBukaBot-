from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, select

from backend.app.database import Base, build_engine, run_migrations
from backend.app.models import Person


def test_fresh_database_upgrades_to_head(tmp_path, monkeypatch):
    database = tmp_path / "migration-test.sqlite3"
    engine = build_engine(f"sqlite:///{database}")
    # The migration config must not depend on the process working directory.
    monkeypatch.chdir(tmp_path)

    try:
        run_migrations(engine)

        inspector = inspect(engine)
        assert set(inspector.get_table_names()) == {
            "alembic_version",
            "people",
            "relationships",
            "audit_events",
        }
        assert {column["name"] for column in inspector.get_columns("people")} == {
            "person_id", "display_name", "status", "created_at", "updated_at"
        }
        assert len(inspector.get_foreign_keys("relationships")) == 2
        assert {index["name"] for index in inspector.get_indexes("relationships")} == {
            "ix_relationships_from_person_id", "ix_relationships_to_person_id"
        }
    finally:
        engine.dispose()


def test_existing_create_all_database_is_adopted_without_data_loss(tmp_path):
    database = tmp_path / "legacy.sqlite3"
    engine = build_engine(f"sqlite:///{database}")
    try:
        Base.metadata.create_all(engine)
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
        assert row.person_id == "P-1234567890AB"
        assert row.display_name == "Existing record"
        assert inspect(engine).has_table("alembic_version")
    finally:
        engine.dispose()


def test_partial_legacy_schema_is_rejected_without_creating_other_tables(tmp_path):
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

        assert set(inspect(engine).get_table_names()) == {"people"}
    finally:
        engine.dispose()
