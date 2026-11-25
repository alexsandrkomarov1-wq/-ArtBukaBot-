from fastapi.testclient import TestClient

from backend.app.database import build_engine, run_migrations
from backend.app.main import create_app


def make_client(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'registry.sqlite3'}"
    engine = build_engine(database_url)
    run_migrations(engine)
    engine.dispose()
    app = create_app(
        database_url=database_url,
        jwt_secret="test-only-signing-secret-with-at-least-32-bytes",
        bootstrap_token="test-bootstrap-secret",
    )
    return TestClient(app)


def owner_headers(client):
    boot = client.post(
        "/api/v1/auth/bootstrap",
        headers={"X-Core-Bootstrap-Token": "test-bootstrap-secret"},
        json={"username": "owner", "password": "correct-horse-battery-123"},
    )
    assert boot.status_code == 201
    login = client.post(
        "/api/v1/auth/login",
        json={"username": "owner", "password": "correct-horse-battery-123"},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_event_place_visit_and_entity_links_share_stable_ids(tmp_path):
    with make_client(tmp_path) as client:
        headers = owner_headers(client)
        person = client.post("/api/v1/people", headers=headers, json={"display_name": "Анна"}).json()
        event = client.post("/api/v1/events", headers=headers, json={
            "title": "Семейная встреча", "description": "Проверка реестра",
            "occurred_at": "2026-11-25T12:00:00Z",
        })
        assert event.status_code == 201, event.text
        event_data = event.json()
        assert event_data["event_id"].startswith("E-")
        assert len(event_data["event_id"]) == 34

        place = client.post("/api/v1/places", headers=headers, json={
            "name": "Санкт-Петербург", "latitude": 59.9386, "longitude": 30.3141,
        })
        assert place.status_code == 201, place.text
        place_data = place.json()
        assert place_data["place_id"].startswith("PL-")
        assert len(place_data["place_id"]) == 35

        visit = client.post("/api/v1/places/visits", headers=headers, json={
            "place_id": place_data["place_id"], "visited_at": "2026-11-25T12:00:00Z",
            "notes": "Тестовая запись",
        })
        assert visit.status_code == 201, visit.text
        assert visit.json()["visit_id"].startswith("V-")
        assert client.get(f"/api/v1/places/{place_data['place_id']}/visits", headers=headers).json()[0]["visit_id"] == visit.json()["visit_id"]

        link = client.post("/api/v1/entities/links", headers=headers, json={
            "source_type": "event", "source_id": event_data["event_id"],
            "target_type": "person", "target_id": person["person_id"],
            "relationship_type": "participant",
        })
        assert link.status_code == 201, link.text
        assert link.json()["link_id"].startswith("EL-")
        listed = client.get("/api/v1/entities/links", headers=headers, params={
            "entity_type": "person", "entity_id": person["person_id"],
        })
        assert listed.status_code == 200
        assert listed.json()[0]["target_id"] == person["person_id"]


def test_place_rejects_invalid_coordinate_pair_and_entity_links_reject_missing_target(tmp_path):
    with make_client(tmp_path) as client:
        headers = owner_headers(client)
        invalid = client.post("/api/v1/places", headers=headers, json={
            "name": "Invalid", "latitude": 59.9,
        })
        assert invalid.status_code == 422
        missing = client.post("/api/v1/entities/links", headers=headers, json={
            "source_type": "event", "source_id": "E-00000000000000000000000000000000",
            "target_type": "place", "target_id": "PL-00000000000000000000000000000000",
            "relationship_type": "held_at",
        })
        assert missing.status_code == 404


def test_entity_registry_requires_authentication(tmp_path):
    with make_client(tmp_path) as client:
        assert client.get("/api/v1/events").status_code == 401
        assert client.get("/api/v1/places").status_code == 401
