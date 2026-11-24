from sqlalchemy.pool import NullPool

from backend.app.database import build_engine, normalize_database_url


def test_normalize_neon_postgresql_url_to_psycopg():
    value = "postgresql://family:secret@ep-example-pooler.eu-central-1.aws.neon.tech/core?sslmode=require"
    assert normalize_database_url(value) == (
        "postgresql+psycopg://family:secret@ep-example-pooler.eu-central-1.aws.neon.tech/core?sslmode=require"
    )


def test_normalize_legacy_postgres_scheme():
    assert normalize_database_url("postgres://u:p@localhost/db") == (
        "postgresql+psycopg://u:p@localhost/db"
    )


def test_sqlite_url_is_unchanged():
    assert normalize_database_url("sqlite:///./test.db") == "sqlite:///./test.db"


def test_serverless_postgres_engine_does_not_keep_connection_pool(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    engine = build_engine("postgresql://u:p@localhost/db")
    try:
        assert isinstance(engine.pool, NullPool)
        assert engine.url.drivername == "postgresql+psycopg"
    finally:
        engine.dispose()
