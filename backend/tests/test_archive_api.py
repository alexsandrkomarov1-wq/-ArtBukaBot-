from pathlib import Path

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
        media_root=tmp_path / "private-media",
    )
    return TestClient(app)


def owner_token(client):
    created = client.post(
        "/api/v1/auth/bootstrap",
        headers={"X-Core-Bootstrap-Token": "test-bootstrap-secret"},
        json={"username": "owner", "password": "correct-horse-battery-123"},
    )
    assert created.status_code == 201, created.text
    logged = client.post(
        "/api/v1/auth/login",
        json={"username": "owner", "password": "correct-horse-battery-123"},
    )
    assert logged.status_code == 200, logged.text
    return logged.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def jpeg_fixture():
    return bytes.fromhex("ffd8ff") + b"family-photo-test-payload" * 4


def test_private_upload_registers_original_hash_and_quarantine_state(tmp_path):
    with make_client(tmp_path) as client:
        token = owner_token(client)
        original = jpeg_fixture()
        response = client.post(
            "/api/v1/archive/items",
            headers=auth(token),
            files={"file": ("family.jpg", original, "application/octet-stream")},
            data={"title": "Семейная фотография"},
        )
        assert response.status_code == 201, response.text
        item = response.json()
        assert item["archive_item_id"].startswith("AR-")
        assert len(item["archive_item_id"]) == 35
        assert item["item_type"] == "photo"
        assert item["record_status"] == "quarantined"
        assert item["storage_state"] == "quarantined"
        assert item["detected_mime_type"] == "image/jpeg"
        assert item["sha256"] == __import__("hashlib").sha256(original).hexdigest()
        assert item["size_bytes"] == len(original)
        assert "storage_object_key" not in item
        assert "private-media" not in response.text

        stored = list((tmp_path / "private-media" / "quarantine").rglob("*"))
        stored_files = [path for path in stored if path.is_file()]
        assert len(stored_files) == 1
        assert stored_files[0].read_bytes() == original

        listed = client.get("/api/v1/archive/items", headers=auth(token))
        assert listed.status_code == 200
        assert listed.json()[0]["archive_item_id"] == item["archive_item_id"]


def test_duplicate_content_is_not_registered_twice(tmp_path):
    with make_client(tmp_path) as client:
        token = owner_token(client)
        payload = jpeg_fixture()
        first = client.post(
            "/api/v1/archive/items", headers=auth(token),
            files={"file": ("one.jpg", payload, "image/jpeg")},
        )
        duplicate = client.post(
            "/api/v1/archive/items", headers=auth(token),
            files={"file": ("renamed.jpg", payload, "image/jpeg")},
        )
        assert first.status_code == 201
        assert duplicate.status_code == 409
        assert duplicate.json()["detail"]["code"] == "duplicate_content"
        assert duplicate.json()["detail"]["archive_item_id"] == first.json()["archive_item_id"]
        assert len([p for p in (tmp_path / "private-media" / "quarantine").rglob("*") if p.is_file()]) == 1


def test_archive_upload_requires_authentication_and_guest_cannot_upload(tmp_path):
    with make_client(tmp_path) as client:
        anonymous = client.post(
            "/api/v1/archive/items",
            files={"file": ("photo.jpg", jpeg_fixture(), "image/jpeg")},
        )
        assert anonymous.status_code == 401

        token = owner_token(client)
        created = client.post(
            "/api/v1/users", headers=auth(token),
            json={"username": "guest", "password": "a-long-test-password-123", "role": "guest"},
        )
        assert created.status_code == 201
        guest_login = client.post(
            "/api/v1/auth/login",
            json={"username": "guest", "password": "a-long-test-password-123"},
        )
        guest_token = guest_login.json()["access_token"]
        forbidden = client.post(
            "/api/v1/archive/items", headers=auth(guest_token),
            files={"file": ("photo.jpg", jpeg_fixture(), "image/jpeg")},
        )
        assert forbidden.status_code == 403
        assert client.get("/api/v1/archive/items", headers=auth(guest_token)).status_code == 403


def test_guest_cannot_read_private_archive_metadata_or_content(tmp_path):
    with make_client(tmp_path) as client:
        owner = owner_token(client)
        uploaded = client.post(
            "/api/v1/archive/items", headers=auth(owner),
            files={"file": ("family.jpg", jpeg_fixture(), "image/jpeg")},
        )
        assert uploaded.status_code == 201
        item_id = uploaded.json()["archive_item_id"]

        created = client.post(
            "/api/v1/users", headers=auth(owner),
            json={"username": "guest", "password": "a-long-test-password-123", "role": "guest"},
        )
        assert created.status_code == 201
        login = client.post(
            "/api/v1/auth/login",
            json={"username": "guest", "password": "a-long-test-password-123"},
        )
        guest = login.json()["access_token"]

        assert client.get("/api/v1/archive/items", headers=auth(guest)).status_code == 403
        assert client.get(
            f"/api/v1/archive/items/{item_id}", headers=auth(guest)
        ).status_code == 403
        assert client.get(
            f"/api/v1/archive/items/{item_id}/content", headers=auth(guest)
        ).status_code == 403
        assert client.get(
            f"/api/v1/archive/items/{item_id}/links", headers=auth(guest)
        ).status_code == 403


def test_quarantined_original_cannot_be_viewed_even_by_owner(tmp_path):
    with make_client(tmp_path) as client:
        token = owner_token(client)
        uploaded = client.post(
            "/api/v1/archive/items", headers=auth(token),
            files={"file": ("family.jpg", jpeg_fixture(), "image/jpeg")},
        )
        assert uploaded.status_code == 201
        item_id = uploaded.json()["archive_item_id"]

        response = client.get(
            f"/api/v1/archive/items/{item_id}/content", headers=auth(token)
        )
        assert response.status_code == 423
        assert "quarantined" in response.json()["detail"].lower()


def test_storage_health_reports_actual_local_backend_and_requires_login(tmp_path):
    with make_client(tmp_path) as client:
        anonymous = client.get("/api/v1/archive/storage/health")
        assert anonymous.status_code == 401

        token = owner_token(client)
        response = client.get(
            "/api/v1/archive/storage/health", headers=auth(token)
        )
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "backend": "local-private"}


def test_invalid_signature_and_extension_mismatch_are_rejected(tmp_path):
    with make_client(tmp_path) as client:
        token = owner_token(client)
        invalid = client.post(
            "/api/v1/archive/items", headers=auth(token),
            files={"file": ("fake.jpg", b"not really an image", "image/jpeg")},
        )
        assert invalid.status_code == 415
        mismatch = client.post(
            "/api/v1/archive/items", headers=auth(token),
            files={"file": ("fake.mp4", jpeg_fixture(), "video/mp4")},
        )
        assert mismatch.status_code == 415
        assert client.get("/api/v1/archive/items", headers=auth(token)).json() == []


def test_photo_can_be_linked_to_existing_person_and_duplicate_link_is_blocked(tmp_path):
    with make_client(tmp_path) as client:
        token = owner_token(client)
        headers = auth(token)
        photo = client.post(
            "/api/v1/archive/items", headers=headers,
            files={"file": ("family.jpg", jpeg_fixture(), "image/jpeg")},
        ).json()
        person = client.post(
            "/api/v1/people", headers=headers, json={"display_name": "Иван Иванов"}
        ).json()
        link_payload = {
            "target_entity_type": "person",
            "target_entity_id": person["person_id"],
            "link_role": "depicted",
            "source_note": "Подтверждено владельцем",
        }
        linked = client.post(
            f"/api/v1/archive/items/{photo['archive_item_id']}/links",
            headers=headers, json=link_payload,
        )
        assert linked.status_code == 201, linked.text
        assert linked.json()["target_entity_id"] == person["person_id"]
        duplicate = client.post(
            f"/api/v1/archive/items/{photo['archive_item_id']}/links",
            headers=headers, json=link_payload,
        )
        assert duplicate.status_code == 409
        links = client.get(
            f"/api/v1/archive/items/{photo['archive_item_id']}/links", headers=headers
        )
        assert len(links.json()) == 1


def test_link_rejects_unknown_person_and_unknown_entity_types(tmp_path):
    with make_client(tmp_path) as client:
        token = owner_token(client)
        headers = auth(token)
        photo = client.post(
            "/api/v1/archive/items", headers=headers,
            files={"file": ("family.jpg", jpeg_fixture(), "image/jpeg")},
        ).json()
        missing = client.post(
            f"/api/v1/archive/items/{photo['archive_item_id']}/links",
            headers=headers,
            json={"target_entity_type": "person", "target_entity_id": "P-NOT-FOUND"},
        )
        assert missing.status_code == 404
        unsupported = client.post(
            f"/api/v1/archive/items/{photo['archive_item_id']}/links",
            headers=headers,
            json={"target_entity_type": "event", "target_entity_id": "EV-123"},
        )
        assert unsupported.status_code == 422


def test_upload_limit_is_enforced_before_archive_registration(tmp_path, monkeypatch):
    import backend.app.archive_api as archive_api

    monkeypatch.setattr(archive_api, "MAX_UPLOAD_BYTES", 8)
    with make_client(tmp_path) as client:
        token = owner_token(client)
        response = client.post(
            "/api/v1/archive/items", headers=auth(token),
            files={"file": ("large.jpg", jpeg_fixture(), "image/jpeg")},
        )
        assert response.status_code == 413
        assert client.get("/api/v1/archive/items", headers=auth(token)).json() == []
        assert not list((tmp_path / "private-media").rglob("*.part"))



def test_upload_does_not_overwrite_an_existing_content_addressed_object(tmp_path, monkeypatch):
    import backend.app.archive_api as archive_api

    def simulate_storage_key_collision(source, destination):
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"pre-existing-object")
        raise FileExistsError(destination)

    monkeypatch.setattr(archive_api.os, "link", simulate_storage_key_collision)
    with make_client(tmp_path) as client:
        token = owner_token(client)
        response = client.post(
            "/api/v1/archive/items",
            headers=auth(token),
            files={"file": ("family.jpg", jpeg_fixture(), "image/jpeg")},
        )
        assert response.status_code == 409
        assert "already occupies the storage key" in response.json()["detail"]

        stored_files = [
            path for path in (tmp_path / "private-media").rglob("*")
            if path.is_file() and path.name != ".keep"
        ]
        assert len(stored_files) == 1
        assert stored_files[0].read_bytes() == b"pre-existing-object"
        assert client.get("/api/v1/archive/items", headers=auth(token)).json() == []
        assert not list((tmp_path / "private-media").rglob("*.part"))
