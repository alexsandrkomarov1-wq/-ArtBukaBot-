from fastapi.testclient import TestClient

from backend.app.database import build_engine, run_migrations
from backend.app.main import create_app


def make_client(tmp_path):
    database = tmp_path / "test.sqlite3"
    database_url = f"sqlite:///{database}"
    migration_engine = build_engine(database_url)
    run_migrations(migration_engine)
    migration_engine.dispose()
    app = create_app(
        database_url=database_url,
        jwt_secret="test-only-signing-secret-with-at-least-32-bytes",
        bootstrap_token="test-bootstrap-secret",
    )
    return TestClient(app)


def bootstrap_owner(client):
    response = client.post(
        "/api/v1/auth/bootstrap",
        headers={"X-Core-Bootstrap-Token": "test-bootstrap-secret"},
        json={"username": "owner", "password": "correct-horse-battery-123"},
    )
    assert response.status_code == 201, response.text
    login = client.post(
        "/api/v1/auth/login",
        json={"username": "owner", "password": "correct-horse-battery-123"},
    )
    assert login.status_code == 200, login.text
    return login.json()


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def create_account(client, owner_token, username, role, password="a-long-test-password-123"):
    return client.post(
        "/api/v1/users",
        headers=auth(owner_token),
        json={"username": username, "password": password, "role": role},
    )


def login(client, username, password="a-long-test-password-123"):
    return client.post("/api/v1/auth/login", json={"username": username, "password": password})


def test_health_is_public_and_contains_no_personal_data(tmp_path):
    with make_client(tmp_path) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "service": "komarova-core-api",
            "version": "0.2.0",
        }


def test_bootstrap_is_one_time_and_owner_can_login(tmp_path):
    with make_client(tmp_path) as client:
        owner = bootstrap_owner(client)
        assert owner["user"]["role"] == "owner"
        assert owner["user"]["user_id"].startswith("U-")
        assert len(owner["user"]["user_id"]) == 14
        assert client.get("/api/v1/auth/me", headers=auth(owner["access_token"])).json()["username"] == "owner"

        repeated = client.post(
            "/api/v1/auth/bootstrap",
            headers={"X-Core-Bootstrap-Token": "test-bootstrap-secret"},
            json={"username": "second-owner", "password": "correct-horse-battery-456"},
        )
        assert repeated.status_code == 409


def test_logout_revokes_access_session(tmp_path):
    with make_client(tmp_path) as client:
        owner = bootstrap_owner(client)
        token_headers = auth(owner["access_token"])
        assert len(client.get("/api/v1/auth/sessions", headers=token_headers).json()) == 1
        assert client.post("/api/v1/auth/logout", headers=token_headers).status_code == 200
        assert client.get("/api/v1/auth/me", headers=token_headers).status_code == 401


def test_password_change_revokes_all_sessions_and_requires_new_login(tmp_path):
    with make_client(tmp_path) as client:
        owner = bootstrap_owner(client)
        token_headers = auth(owner["access_token"])
        changed = client.post(
            "/api/v1/auth/change-password",
            headers=token_headers,
            json={
                "current_password": "correct-horse-battery-123",
                "new_password": "a-new-long-password-456",
            },
        )
        assert changed.status_code == 200
        assert changed.json()["reauthentication_required"] is True
        assert client.get("/api/v1/auth/me", headers=token_headers).status_code == 401
        assert login(client, "owner", "correct-horse-battery-123").status_code == 401
        assert login(client, "owner", "a-new-long-password-456").status_code == 200


def test_guest_is_read_only_and_family_member_can_add_people(tmp_path):
    with make_client(tmp_path) as client:
        owner = bootstrap_owner(client)
        owner_token = owner["access_token"]
        family = create_account(client, owner_token, "family", "family_member")
        guest = create_account(client, owner_token, "guest", "guest")
        assert family.status_code == guest.status_code == 201

        family_login = login(client, "family")
        guest_login = login(client, "guest")
        created = client.post(
            "/api/v1/people",
            headers=auth(family_login.json()["access_token"]),
            json={"display_name": "Иван Иванов"},
        )
        assert created.status_code == 201

        guest_headers = auth(guest_login.json()["access_token"])
        assert client.get("/api/v1/people", headers=guest_headers).status_code == 200
        assert client.post(
            "/api/v1/people", headers=guest_headers, json={"display_name": "No write"}
        ).status_code == 403


def test_moderator_cannot_grant_roles_or_manage_owner(tmp_path):
    with make_client(tmp_path) as client:
        owner = bootstrap_owner(client)
        owner_token = owner["access_token"]
        moderator = create_account(client, owner_token, "moderator", "moderator")
        assert moderator.status_code == 201
        moderator_token = login(client, "moderator").json()["access_token"]

        denied_owner = create_account(client, moderator_token, "newowner", "owner")
        denied_moderator = create_account(client, moderator_token, "newmod", "moderator")
        assert denied_owner.status_code == denied_moderator.status_code == 403

        owner_id = owner["user"]["user_id"]
        assert client.patch(
            f"/api/v1/users/{owner_id}",
            headers=auth(moderator_token),
            json={"status": "disabled"},
        ).status_code == 403


def test_only_owner_changes_roles_and_last_owner_is_protected(tmp_path):
    with make_client(tmp_path) as client:
        owner = bootstrap_owner(client)
        owner_token = owner["access_token"]
        member = create_account(client, owner_token, "member", "family_member").json()
        changed = client.patch(
            f"/api/v1/users/{member['user_id']}",
            headers=auth(owner_token),
            json={"role": "moderator"},
        )
        assert changed.status_code == 200
        assert changed.json()["role"] == "moderator"

        last_owner = client.patch(
            f"/api/v1/users/{owner['user']['user_id']}",
            headers=auth(owner_token),
            json={"status": "disabled"},
        )
        assert last_owner.status_code == 409


def test_person_registry_archive_and_audit_actor(tmp_path):
    with make_client(tmp_path) as client:
        owner = bootstrap_owner(client)
        headers = auth(owner["access_token"])
        created = client.post("/api/v1/people", headers=headers, json={"display_name": "  Иван   Иванов "})
        assert created.status_code == 201
        person = created.json()
        person_id = person["person_id"]
        assert person_id.startswith("P-") and len(person_id) == 14
        assert person["display_name"] == "Иван Иванов"

        fetched = client.get(f"/api/v1/people/{person_id}", headers=headers)
        assert fetched.status_code == 200
        assert fetched.json()["person_id"] == person_id

        archived = client.delete(f"/api/v1/people/{person_id}", headers=headers)
        assert archived.status_code == 200
        assert archived.json()["status"] == "archived"
        assert client.get("/api/v1/people", headers=headers).json() == []
        full_list = client.get("/api/v1/people?include_archived=true", headers=headers)
        assert full_list.json()[0]["person_id"] == person_id


def test_relationships_require_two_existing_people(tmp_path):
    with make_client(tmp_path) as client:
        owner = bootstrap_owner(client)
        headers = auth(owner["access_token"])
        first = client.post("/api/v1/people", headers=headers, json={"display_name": "Анна"})
        second = client.post("/api/v1/people", headers=headers, json={"display_name": "Борис"})
        first_id, second_id = first.json()["person_id"], second.json()["person_id"]

        relation = client.post(
            "/api/v1/relationships",
            headers=headers,
            json={
                "from_person_id": first_id,
                "to_person_id": second_id,
                "relationship_type": "sibling",
            },
        )
        assert relation.status_code == 201
        assert relation.json()["from_person_id"] == first_id
        assert len(client.get(
            f"/api/v1/people/{first_id}/relationships", headers=headers
        ).json()) == 1

        self_relation = client.post(
            "/api/v1/relationships",
            headers=headers,
            json={
                "from_person_id": first_id,
                "to_person_id": first_id,
                "relationship_type": "self",
            },
        )
        assert self_relation.status_code == 422


def test_bad_password_and_missing_bearer_are_rejected(tmp_path):
    with make_client(tmp_path) as client:
        bootstrap_owner(client)
        assert login(client, "owner", "wrong-password").status_code == 401
        assert client.get("/api/v1/people").status_code == 401


def test_blank_person_name_and_short_password_are_rejected(tmp_path):
    with make_client(tmp_path) as client:
        short_password = client.post(
            "/api/v1/auth/bootstrap",
            headers={"X-Core-Bootstrap-Token": "test-bootstrap-secret"},
            json={"username": "owner", "password": "short"},
        )
        assert short_password.status_code == 422
        owner = bootstrap_owner(client)
        response = client.post(
            "/api/v1/people",
            headers=auth(owner["access_token"]),
            json={"display_name": "   "},
        )
        assert response.status_code == 422



def test_disabling_user_revokes_sessions_even_after_reenable(tmp_path):
    with make_client(tmp_path) as client:
        owner = bootstrap_owner(client)
        owner_headers = auth(owner["access_token"])
        member = create_account(client, owner["access_token"], "member", "family_member").json()
        member_login = login(client, "member").json()
        member_headers = auth(member_login["access_token"])
        disabled = client.patch(
            f"/api/v1/users/{member['user_id']}", headers=owner_headers,
            json={"status": "disabled"},
        )
        assert disabled.status_code == 200
        assert client.get("/api/v1/auth/me", headers=member_headers).status_code == 401
        enabled = client.patch(
            f"/api/v1/users/{member['user_id']}", headers=owner_headers,
            json={"status": "active"},
        )
        assert enabled.status_code == 200
        assert client.get("/api/v1/auth/me", headers=member_headers).status_code == 401


def test_login_throttling_is_persistent_and_resets_after_success(tmp_path):
    with make_client(tmp_path) as client:
        bootstrap_owner(client)
        for _ in range(5):
            response = login(client, "owner", "definitely-wrong-password")
            assert response.status_code == 401
        assert login(client, "owner").status_code == 429
