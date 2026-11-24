from __future__ import annotations

import base64
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.app.database import build_engine, run_migrations
from backend.app.main import create_app
from backend.app.models import GoogleDriveAccount, GoogleOAuthState
from backend.app.google_drive_oauth import decrypt_refresh_token, encrypt_refresh_token


def make_client(tmp_path, monkeypatch):
    key = base64.urlsafe_b64encode(b"0123456789abcdef0123456789abcdef").decode("ascii").rstrip("=")
    monkeypatch.setenv("CORE_OAUTH_ENCRYPTION_KEY", key)
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_ID", "test-client.apps.googleusercontent.com")
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_SECRET", "test-client-secret")
    monkeypatch.setenv("GOOGLE_DRIVE_REDIRECT_URI", "https://api.example.test/api/v1/integrations/google-drive/callback")
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
    ciphertext = encrypt_refresh_token("refresh-secret", "U-123", "GD-ONE")
    assert ciphertext != "refresh-secret"
    assert decrypt_refresh_token(ciphertext, "U-123", "GD-ONE") == "refresh-secret"
    try:
        decrypt_refresh_token(ciphertext, "U-456", "GD-ONE")
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
    assert query["redirect_uri"] == ["https://api.example.test/api/v1/integrations/google-drive/callback"]
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
    assert response.json() == {"status": "not_connected", "provider": "google-drive", "accounts": []}


def test_google_drive_callback_stores_encrypted_refresh_token_and_quota(tmp_path, monkeypatch):
    client, token = make_client(tmp_path, monkeypatch)
    connect = client.get("/api/v1/integrations/google-drive/connect", headers=auth(token))
    state = parse_qs(urlparse(connect.json()["authorization_url"]).query)["state"][0]

    class FakeResponse:
        def __init__(self, status_code, payload):
            self.status_code = status_code
            self._payload = payload

        def json(self):
            return self._payload

    def fake_post(url, **kwargs):
        assert url == "https://oauth2.googleapis.com/token"
        assert kwargs["data"]["grant_type"] == "authorization_code"
        assert kwargs["data"]["redirect_uri"] == "https://api.example.test/api/v1/integrations/google-drive/callback"
        return FakeResponse(200, {
            "access_token": "temporary-access-token",
            "refresh_token": "long-lived-refresh-token",
            "scope": "https://www.googleapis.com/auth/drive.metadata.readonly",
        })

    def fake_get(url, **kwargs):
        assert url == "https://www.googleapis.com/drive/v3/about"
        assert kwargs["headers"]["Authorization"] == "Bearer temporary-access-token"
        return FakeResponse(200, {
            "user": {
                "permissionId": "google-permission-123",
                "emailAddress": "owner@example.test",
                "displayName": "Owner Test",
            },
            "storageQuota": {
                "limit": "15000000000",
                "usage": "1000",
                "usageInDrive": "800",
                "usageInDriveTrash": "200",
            },
        })

    monkeypatch.setattr("backend.app.google_drive_oauth.httpx.post", fake_post)
    monkeypatch.setattr("backend.app.google_drive_oauth.httpx.get", fake_get)

    callback = client.get(
        "/api/v1/integrations/google-drive/callback",
        params={"code": "one-time-code", "state": state},
    )
    assert callback.status_code == 200
    payload = callback.json()
    assert payload["status"] == "connected"
    assert payload["email_address"] == "owner@example.test"
    assert payload["quota_limit_bytes"] == 15000000000
    assert "refresh_token" not in callback.text
    assert "access_token" not in callback.text

    status = client.get("/api/v1/integrations/google-drive/status", headers=auth(token))
    assert status.status_code == 200
    assert status.json()["accounts"][0]["email_address"] == "owner@example.test"
    assert status.json()["accounts"][0]["access"] == "metadata_read_only"

    from backend.app.database import build_engine
    from backend.app.models import GoogleDriveAccount
    from sqlalchemy import select
    engine = build_engine(f"sqlite:///{tmp_path / 'oauth.sqlite3'}")
    with engine.connect() as connection:
        stored = connection.execute(select(GoogleDriveAccount.__table__)).mappings().one()
        assert stored["refresh_token_ciphertext"] != "long-lived-refresh-token"
        assert stored["refresh_token_ciphertext"]
    engine.dispose()


def test_one_owner_can_connect_two_independent_google_accounts(tmp_path, monkeypatch):
    client, token = make_client(tmp_path, monkeypatch)

    class FakeResponse:
        def __init__(self, status_code, payload):
            self.status_code, self.payload = status_code, payload
        def json(self):
            return self.payload

    def fake_post(url, **kwargs):
        if url == "https://oauth2.googleapis.com/revoke":
            return FakeResponse(200, {})
        assert url == "https://oauth2.googleapis.com/token"
        data = kwargs["data"]
        if data["grant_type"] == "refresh_token":
            code = data["refresh_token"].removeprefix("refresh-")
            return FakeResponse(200, {"access_token": f"access-{code}"})
        code = data["code"]
        return FakeResponse(200, {
            "access_token": f"access-{code}", "refresh_token": f"refresh-{code}",
            "scope": "https://www.googleapis.com/auth/drive.metadata.readonly",
        })

    def fake_get(url, **kwargs):
        code = kwargs["headers"]["Authorization"].split("access-")[1]
        return FakeResponse(200, {"user": {
            "permissionId": f"google-id-{code}", "emailAddress": f"{code}@example.test",
            "displayName": f"Drive {code}",
        }, "storageQuota": {"limit": "10000", "usage": "100", "usageInDrive": "90", "usageInDriveTrash": "10"}})

    monkeypatch.setattr("backend.app.google_drive_oauth.httpx.post", fake_post)
    monkeypatch.setattr("backend.app.google_drive_oauth.httpx.get", fake_get)

    account_ids = []
    for code in ("first", "second"):
        connect = client.get("/api/v1/integrations/google-drive/connect", headers=auth(token))
        state = parse_qs(urlparse(connect.json()["authorization_url"]).query)["state"][0]
        callback = client.get("/api/v1/integrations/google-drive/callback",
                              params={"code": code, "state": state})
        assert callback.status_code == 200
        account_ids.append(callback.json()["drive_account_id"])

    assert account_ids[0] != account_ids[1]
    status = client.get("/api/v1/integrations/google-drive/status", headers=auth(token)).json()
    assert len(status["accounts"]) == 2
    assert {item["email_address"] for item in status["accounts"]} == {
        "first@example.test", "second@example.test"
    }

    refreshed = client.post(
        f"/api/v1/integrations/google-drive/accounts/{account_ids[0]}/refresh-quota",
        headers=auth(token),
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["drive_account_id"] == account_ids[0]
    disconnected = client.delete(
        f"/api/v1/integrations/google-drive/accounts/{account_ids[0]}",
        headers=auth(token),
    )
    assert disconnected.status_code == 200
    remaining = client.get(
        "/api/v1/integrations/google-drive/status", headers=auth(token)
    ).json()["accounts"]
    assert [item["drive_account_id"] for item in remaining] == [account_ids[1]]

    from backend.app.database import build_engine
    engine = build_engine(f"sqlite:///{tmp_path / 'oauth.sqlite3'}")
    with engine.connect() as connection:
        stored = connection.execute(select(GoogleDriveAccount.__table__)).mappings().all()
        assert len(stored) == 1
        assert stored[0]["drive_account_id"] == account_ids[1]
    engine.dispose()


def test_google_identity_cannot_be_linked_to_another_core_user(tmp_path, monkeypatch):
    client, owner_token = make_client(tmp_path, monkeypatch)

    class FakeResponse:
        def __init__(self, status_code, payload):
            self.status_code, self.payload = status_code, payload
        def json(self):
            return self.payload

    def fake_post(url, **kwargs):
        code = kwargs["data"]["code"]
        return FakeResponse(200, {
            "access_token": f"access-{code}", "refresh_token": f"refresh-{code}",
            "scope": "https://www.googleapis.com/auth/drive.metadata.readonly",
        })

    def fake_get(url, **kwargs):
        return FakeResponse(200, {"user": {
            "permissionId": "one-google-identity",
            "emailAddress": "same-google@example.test",
            "displayName": "Same Google account",
        }, "storageQuota": {"limit": "10000", "usage": "100"}})

    monkeypatch.setattr("backend.app.google_drive_oauth.httpx.post", fake_post)
    monkeypatch.setattr("backend.app.google_drive_oauth.httpx.get", fake_get)

    connect = client.get("/api/v1/integrations/google-drive/connect", headers=auth(owner_token))
    state = parse_qs(urlparse(connect.json()["authorization_url"]).query)["state"][0]
    first = client.get("/api/v1/integrations/google-drive/callback",
                       params={"code": "owner", "state": state})
    assert first.status_code == 200

    created = client.post("/api/v1/users", headers=auth(owner_token), json={
        "username": "family", "password": "family-member-password-123",
        "role": "family_member",
    })
    assert created.status_code == 201
    login = client.post("/api/v1/auth/login", json={
        "username": "family", "password": "family-member-password-123",
    })
    family_token = login.json()["access_token"]
    connect = client.get("/api/v1/integrations/google-drive/connect", headers=auth(family_token))
    state = parse_qs(urlparse(connect.json()["authorization_url"]).query)["state"][0]
    second = client.get("/api/v1/integrations/google-drive/callback",
                        params={"code": "family", "state": state})
    assert second.status_code == 409
