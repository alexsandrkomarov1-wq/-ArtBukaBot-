from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from backend.app.database import build_engine


def test_fresh_database_upgrades_to_head(tmp_path):
    database = tmp_path / "migration-test.sqlite3"
    engine = build_engine(f"sqlite:///{database}")
    config = Config("alembic.ini")

    try:
        with engine.begin() as connection:
            config.attributes["connection"] = connection
            command.upgrade(config, "head")

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
    finally:
        engine.dispose()
