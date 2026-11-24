from backend.app.database import build_engine, normalize_database_url


def test_sqlite_url_is_unchanged():
    url = "sqlite:///./komarova_core.db"
    assert normalize_database_url(url) == url


def test_standard_postgresql_url_uses_psycopg3():
    url = "postgresql://family_user:secret@ep-example.neon.tech/family?sslmode=require"
    normalized = normalize_database_url(url)
    assert normalized.startswith("postgresql+psycopg://")
    assert "sslmode=require" in normalized
    assert "family_user:secret@" in normalized


def test_legacy_postgres_scheme_uses_psycopg3():
    url = "postgres://family_user:secret@localhost/family"
    assert normalize_database_url(url).startswith("postgresql+psycopg://")


def test_engine_can_be_constructed_for_neon_without_connecting():
    engine = build_engine(
        "postgresql://family_user:secret@ep-example.neon.tech/family?sslmode=require"
    )
    try:
        assert engine.url.drivername == "postgresql+psycopg"
        assert engine.url.query["sslmode"] == "require"
    finally:
        engine.dispose()
