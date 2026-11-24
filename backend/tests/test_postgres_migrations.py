import os

import pytest
from sqlalchemy import inspect, text

from backend.app.database import build_engine, run_migrations, verify_migrations_current
from backend.app.models import Base


@pytest.mark.skipif(not os.getenv("POSTGRES_TEST_URL"), reason="PostgreSQL CI service is not configured")
def test_full_alembic_chain_runs_on_postgresql_and_matches_models():
    engine = build_engine(os.environ["POSTGRES_TEST_URL"])
    try:
        run_migrations(engine)
        verify_migrations_current(engine)
        inspector = inspect(engine)
        expected = set(Base.metadata.tables)
        actual = set(inspector.get_table_names()) - {"alembic_version"}
        assert actual == expected
        with engine.connect() as connection:
            revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        assert revision == "0005_private_media_intake"
    finally:
        engine.dispose()
