from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_configured_origin_can_call_private_api_preflight(tmp_path, monkeypatch):
    database_url = "sqlite:///" + str(tmp_path / "cors.sqlite3")
    monkeypatch.setenv("CORE_CORS_ORIGINS", "https://family.example")
    app = create_app(
        database_url=database_url,
        jwt_secret="test-only-signing-secret-with-at-least-32-bytes",
        bootstrap_token="test-bootstrap-secret",
        media_root=tmp_path / "private-media",
    )
    with TestClient(app) as client:
        response = client.options(
            "/api/v1/auth/login",
            headers={
                "Origin": "https://family.example",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization,content-type",
            },
        )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://family.example"
    assert response.headers["access-control-allow-credentials"] == "true"


def test_unlisted_origin_is_not_granted_cors_access(tmp_path, monkeypatch):
    database_url = "sqlite:///" + str(tmp_path / "cors.sqlite3")
    migration_engine = build_engine(database_url)
    run_migrations(migration_engine)
    migration_engine.dispose()
    monkeypatch.setenv("CORE_CORS_ORIGINS", "https://family.example")
    app = create_app(
        database_url=database_url,
        jwt_secret="test-only-signing-secret-with-at-least-32-bytes",
        bootstrap_token="test-bootstrap-secret",
        media_root=tmp_path / "private-media",
    )
    with TestClient(app) as client:
        response = client.options(
            "/api/v1/auth/login",
            headers={
                "Origin": "https://attacker.example",
                "Access-Control-Request-Method": "POST",
            },
        )
    assert "access-control-allow-origin" not in response.headers
