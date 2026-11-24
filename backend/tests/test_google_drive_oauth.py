from __future__ import annotations

import base64
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient

from backend.app.database import build_engine, run_migrations
from backend.app.main import create_app
from backend.app.models import GoogleDriveAccount, GoogleOAuthState
from backend.app.google_drive_oauth import decrypt_refresh_token, encrypt_refresh_token


def make_client(tmp_path, monkeypatch):
    key = base64.urlsafe_b64encode(b"0123456789abcdef0123456789abcdef").decode("ascii").rstrip("=")
    monkeypatch.setenv("CORE_OAUTH_ENCRYPTION_KEY", key)
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_ID", "test-client.apps.googleusercontent.com")
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_SECRET", "test-client-secret")
    monkeypatch.setenv("GOOGLE_DRIVE_REDIRECT_URI", "https://api.example.test/oauth/google-drive/callback")
    database_url = f"sqlite:///{tmp_path / 'oauth.sqlite3'}"
    engine = build_engine(database_url)
    run_migrations(engine)
    engine.dispose()
    app = create_app(
        database_url=database_url,
        jwt_secret="test-only-signing-secret-with-at-least-32-bytes",
        bootstrap_token="test-bootstrap-secret",
    )
    client = TestClient(app)
    bootstrap = client.post(
        "/api/v1/auth/bootstrap",
        headers={"X-Core-Bootstrap-Token": "test-bootstrap-secret"},
        json={"username": "owner", "password": "correct-horse-battery-123"},
    )
    login = client.post("/api/v1/auth/login", json={
        "username": "owner", "password": "correct-horse-battery-123"
    })
    return client, login.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_refresh_token_is_authenticated_encrypted_and_user_bound(monkeypatch):
    monkeypatch.setenv(
        "CORE_OAUTH_ENCRYPTION_KEY",
        base64.urlsafe_b64encode(b"0123456789abcdef0123456789abcdef").decode("ascii").rstrip("="),
    )
    ciphertext = encrypt_refresh_token("refresh-secret", "U-123")
    assert ciphertext != "refresh-secret"
    assert decrypt_refresh_token(ciphertext, "U-123") == "refresh-secret"
    try:
        decrypt_refresh_token(ciphertext, "U-456")
        assert False, "Ciphertext must not decrypt for another user"
    except Exception:
        pass


def test_google_drive_connect_returns_offline_read_only_authorization_url(tmp_path, monkeypatch):
    client, token = make_client(tmp_path, monkeypatch)
    response = client.get("/api/v1/integrations/google-drive/connect", headers=auth(token))
    assert response.status_code == 200
    payload = response.json()
    parsed = urlparse(payload["authorization_url"])
    query = parse_qs(parsed.query)
    assert parsed.netloc == "accounts.google.com"
    assert query["access_type"] == ["offline"]
    assert query["prompt"] == ["consent"]
    assert query["scope"] == ["https://www.googleapis.com/auth/drive.metadata.readonly"]
    assert query["redirect_uri"] == ["https://api.example.test/oauth/google-drive/callback"]
    assert len(query["state"][0]) >= 32


def test_google_drive_connect_requires_app_authentication(tmp_path, monkeypatch):
    client, _ = make_client(tmp_path, monkeypatch)
    response = client.get("/api/v1/integrations/google-drive/connect")
    assert response.status_code == 401


def test_google_drive_callback_rejects_replayed_or_unknown_state(tmp_path, monkeypatch):
    client, token = make_client(tmp_path, monkeypatch)
    response = client.get(
        "/api/v1/integrations/google-drive/callback",
        params={"code": "unused", "state": "invalid-state"},
    )
    assert response.status_code == 400


def test_google_drive_status_is_private_and_starts_disconnected(tmp_path, monkeypatch):
    client, token = make_client(tmp_path, monkeypatch)
    response = client.get("/api/v1/integrations/google-drive/status", headers=auth(token))
    assert response.status_code == 200
    assert response.json() == {"status": "not_connected", "provider": "google-drive"}
