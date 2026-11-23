from fastapi.testclient import TestClient

from backend.app.main import create_app


def make_client(tmp_path):
    database = tmp_path / "test.sqlite3"
    app = create_app(database_url=f"sqlite:///{database}", api_token="test-secret")
    return TestClient(app)


def headers():
    return {"X-Core-Token": "test-secret", "X-Actor-ID": "test-user"}


def test_health_is_public_and_contains_no_personal_data(tmp_path):
    with make_client(tmp_path) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "service": "komarova-core-api",
            "version": "0.1.0",
        }


def test_api_requires_token(tmp_path):
    with make_client(tmp_path) as client:
        response = client.get("/api/v1/people")
        assert response.status_code == 401


def test_person_id_is_stable_and_archive_is_soft_delete(tmp_path):
    with make_client(tmp_path) as client:
        created = client.post("/api/v1/people", headers=headers(), json={"display_name": "  Иван   Иванов "})
        assert created.status_code == 201
        person = created.json()
        person_id = person["person_id"]
        assert person_id.startswith("P-")
        assert len(person_id) == 14
        assert person["display_name"] == "Иван Иванов"

        fetched = client.get(f"/api/v1/people/{person_id}", headers=headers())
        assert fetched.status_code == 200
        assert fetched.json()["person_id"] == person_id

        archived = client.delete(f"/api/v1/people/{person_id}", headers=headers())
        assert archived.status_code == 200
        assert archived.json()["status"] == "archived"

        active_list = client.get("/api/v1/people", headers=headers())
        assert active_list.json() == []
        full_list = client.get("/api/v1/people?include_archived=true", headers=headers())
        assert full_list.json()[0]["person_id"] == person_id


def test_relationships_require_two_existing_people_and_are_audited(tmp_path):
    with make_client(tmp_path) as client:
        first = client.post("/api/v1/people", headers=headers(), json={"display_name": "Анна"})
        second = client.post("/api/v1/people", headers=headers(), json={"display_name": "Борис"})
        first_id, second_id = first.json()["person_id"], second.json()["person_id"]

        relation = client.post(
            "/api/v1/relationships",
            headers=headers(),
            json={
                "from_person_id": first_id,
                "to_person_id": second_id,
                "relationship_type": "sibling",
            },
        )
        assert relation.status_code == 201
        assert relation.json()["from_person_id"] == first_id
        assert relation.json()["to_person_id"] == second_id

        listed = client.get(f"/api/v1/people/{first_id}/relationships", headers=headers())
        assert listed.status_code == 200
        assert len(listed.json()) == 1

        self_relation = client.post(
            "/api/v1/relationships",
            headers=headers(),
            json={
                "from_person_id": first_id,
                "to_person_id": first_id,
                "relationship_type": "self",
            },
        )
        assert self_relation.status_code == 422


def test_blank_name_is_rejected(tmp_path):
    with make_client(tmp_path) as client:
        response = client.post("/api/v1/people", headers=headers(), json={"display_name": "   "})
        assert response.status_code == 422
