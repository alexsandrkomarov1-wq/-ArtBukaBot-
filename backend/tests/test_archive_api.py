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


def test_quarantined_media_is_released_only_after_clean_clamav_scan(tmp_path, monkeypatch):
    from types import SimpleNamespace
    import backend.app.cloud_archive_api as cloud_api

    monkeypatch.setattr(cloud_api.shutil, "which", lambda _: "/usr/bin/clamdscan")
    monkeypatch.setattr(
        cloud_api.subprocess, "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="OK", stderr=""),
    )

    def fake_realesrgan(source_path, output_path, *, scale):
        from PIL import Image
        Image.new("RGB", (64, 48), (180, 205, 225)).save(output_path, format="PNG")
        return SimpleNamespace(
            output_path=str(output_path), output_mime="image/png",
            source_sha256=cloud_api.sha256_file(source_path),
            output_sha256=cloud_api.sha256_file(output_path),
            source_size=Path(source_path).stat().st_size,
            output_size=Path(output_path).stat().st_size,
            engine=f"Real-ESRGAN NCNN Vulkan x{scale}",
            output_width=64, output_height=48,
        )

    from pathlib import Path
    monkeypatch.setattr(cloud_api, "restore_photo", fake_realesrgan)
    with make_client(tmp_path) as client:
        token = owner_token(client)
        headers = auth(token)
        uploaded = client.post(
            "/api/v1/archive/items", headers=headers,
            files={"file": ("family.jpg", jpeg_fixture(), "image/jpeg")},
        )
        assert uploaded.status_code == 201
        item_id = uploaded.json()["archive_item_id"]
        assert uploaded.json()["record_status"] == "quarantined"
        assert client.get(f"/api/v1/archive/items/{item_id}/content", headers=headers).status_code == 423

        scanned = client.post(f"/api/v1/archive/items/{item_id}/scan", headers=headers)
        assert scanned.status_code == 200, scanned.text
        assert scanned.json()["scan_status"] == "clean"
        assert scanned.json()["record_status"] == "available"
        assert scanned.json()["storage_state"] == "verified"
        content = client.get(f"/api/v1/archive/items/{item_id}/content", headers=headers)
        assert content.status_code == 200
        assert content.content == jpeg_fixture()


def test_clamav_unavailable_keeps_media_in_quarantine(tmp_path, monkeypatch):
    import backend.app.cloud_archive_api as cloud_api

    monkeypatch.setattr(cloud_api.shutil, "which", lambda _: None)
    with make_client(tmp_path) as client:
        token = owner_token(client)
        headers = auth(token)
        uploaded = client.post(
            "/api/v1/archive/items", headers=headers,
            files={"file": ("family.jpg", jpeg_fixture(), "image/jpeg")},
        )
        item_id = uploaded.json()["archive_item_id"]
        response = client.post(f"/api/v1/archive/items/{item_id}/scan", headers=headers)
        assert response.status_code == 503
        assert client.get(f"/api/v1/archive/items/{item_id}/content", headers=headers).status_code == 423


def test_clamav_detected_infected_media_is_never_released(tmp_path, monkeypatch):
    from types import SimpleNamespace
    import backend.app.cloud_archive_api as cloud_api

    monkeypatch.setattr(cloud_api.shutil, "which", lambda _: "/usr/bin/clamdscan")
    monkeypatch.setattr(
        cloud_api.subprocess, "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=1, stdout="FOUND", stderr=""),
    )
    with make_client(tmp_path) as client:
        token = owner_token(client)
        headers = auth(token)
        uploaded = client.post(
            "/api/v1/archive/items", headers=headers,
            files={"file": ("family.jpg", jpeg_fixture(), "image/jpeg")},
        )
        item_id = uploaded.json()["archive_item_id"]
        response = client.post(f"/api/v1/archive/items/{item_id}/scan", headers=headers)
        assert response.status_code == 200
        assert response.json()["scan_status"] == "infected"
        assert response.json()["record_status"] == "infected"
        assert client.get(f"/api/v1/archive/items/{item_id}/content", headers=headers).status_code == 423


def test_automatic_enhancement_creates_new_material_linked_to_immutable_original(tmp_path, monkeypatch):
    from types import SimpleNamespace
    import backend.app.cloud_archive_api as cloud_api

    monkeypatch.setattr(cloud_api.shutil, "which", lambda _: "/usr/bin/clamdscan")
    monkeypatch.setattr(
        cloud_api.subprocess, "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="OK", stderr=""),
    )
    with make_client(tmp_path) as client:
        headers = auth(owner_token(client))
        from io import BytesIO
        from PIL import Image
        image_buffer = BytesIO()
        Image.new("RGB", (32, 24), (92, 120, 145)).save(image_buffer, format="JPEG")
        original_bytes = image_buffer.getvalue()
        uploaded = client.post(
            "/api/v1/archive/items", headers=headers,
            files={"file": ("family.jpg", original_bytes, "image/jpeg")},
        )
        assert uploaded.status_code == 201, uploaded.text
        original = uploaded.json()
        assert original["material_id"].startswith("M-")
        assert original["original_material_id"] is None
        original_id = original["archive_item_id"]
        original_material_id = original["material_id"]

        scanned = client.post(f"/api/v1/archive/items/{original_id}/scan", headers=headers)
        assert scanned.status_code == 200, scanned.text
        enhanced = client.post(f"/api/v1/archive/items/{original_id}/enhance", headers=headers)
        assert enhanced.status_code == 200, enhanced.text
        derivative = enhanced.json()
        assert derivative["material_id"].startswith("M-")
        assert derivative["material_id"] != original_material_id
        assert derivative["original_material_id"] == original_material_id
        assert derivative["record_status"] == "available"
        assert derivative["storage_state"] == "verified"
        assert derivative["engine"] == "Real-ESRGAN NCNN Vulkan x4"

        original_content = client.get(f"/api/v1/archive/items/{original_id}/content", headers=headers)
        derivative_content = client.get(
            f"/api/v1/archive/items/{derivative['archive_item_id']}/content", headers=headers
        )
        assert original_content.status_code == 200
        assert original_content.content == original_bytes
        assert derivative_content.status_code == 200
        assert derivative_content.headers["content-type"].startswith("image/png")
        assert derivative_content.content != original_bytes
        assert derivative["output_width"] == 64 and derivative["output_height"] == 48

        derivative_record = client.get(
            f"/api/v1/archive/items/{derivative['archive_item_id']}", headers=headers
        )
        assert derivative_record.status_code == 200
        assert derivative_record.json()["material_id"] == derivative["material_id"]
        assert derivative_record.json()["original_material_id"] == original_material_id
