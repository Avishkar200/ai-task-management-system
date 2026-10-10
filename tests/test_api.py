from fastapi.testclient import TestClient

from tests.conftest import token_for


def test_registration_and_login_issue_jwt(client: TestClient):
    registered = client.post(
        "/api/auth/register",
        json={"name": "New User", "email": "new@example.com", "password": "NewPass123!"},
    )
    assert registered.status_code == 201
    assert registered.json()["role"] == "user"
    assert "password" not in registered.json()

    login = client.post("/api/auth/login", json={"email": "new@example.com", "password": "NewPass123!"})
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"
    assert login.json()["access_token"]


def test_invalid_credentials_and_missing_token_are_rejected(client: TestClient):
    assert client.post("/api/auth/login", json={"email": "alice@example.com", "password": "wrong"}).status_code == 401
    assert client.get("/api/tasks").status_code == 401


def test_user_can_manage_own_tasks_but_not_other_users_tasks(client: TestClient):
    alice_token = token_for(client, "alice@example.com", "AlicePass123!")
    bob_token = token_for(client, "bob@example.com", "BobPass123!")
    alice = {"Authorization": f"Bearer {alice_token}"}
    bob = {"Authorization": f"Bearer {bob_token}"}

    created = client.post("/api/tasks", json={"title": "Write tests", "description": "Cover permissions"}, headers=alice)
    assert created.status_code == 201
    task_id = created.json()["id"]
    assert created.json()["status"] == "Pending"

    assert client.get(f"/api/tasks/{task_id}", headers=bob).status_code == 404
    assert client.patch(f"/api/tasks/{task_id}", json={"title": "Tampered"}, headers=bob).status_code == 404
    assert client.get("/api/tasks", headers=bob).json() == []

    updated = client.patch(f"/api/tasks/{task_id}", json={"title": "Write thorough tests"}, headers=alice)
    assert updated.status_code == 200
    assert updated.json()["title"] == "Write thorough tests"
    assert client.patch(f"/api/tasks/{task_id}/status", json={"status": "Completed"}, headers=alice).status_code == 403


def test_admin_can_list_and_update_any_users_tasks(client: TestClient):
    alice_token = token_for(client, "alice@example.com", "AlicePass123!")
    admin_token = token_for(client, "admin@example.com", "AdminPass123!")
    created = client.post(
        "/api/tasks",
        json={"title": "Alice task"},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    task_id = created.json()["id"]
    admin = {"Authorization": f"Bearer {admin_token}"}

    assert len(client.get("/api/admin/tasks", headers=admin).json()) == 1
    status_update = client.patch(
        f"/api/tasks/{task_id}/status",
        json={"status": "In Progress"},
        headers=admin,
    )
    assert status_update.status_code == 200
    assert status_update.json()["status"] == "In Progress"
    assert client.get("/api/admin/users", headers=admin).status_code == 200


def test_admin_only_endpoints_reject_regular_users(client: TestClient):
    token = token_for(client, "alice@example.com", "AlicePass123!")
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/admin/tasks", headers=headers).status_code == 403
    assert client.get("/api/admin/users", headers=headers).status_code == 403


def test_invalid_status_is_rejected(client: TestClient):
    alice_token = token_for(client, "alice@example.com", "AlicePass123!")
    admin_token = token_for(client, "admin@example.com", "AdminPass123!")
    created = client.post("/api/tasks", json={"title": "Status check"}, headers={"Authorization": f"Bearer {alice_token}"})
    response = client.patch(
        f"/api/tasks/{created.json()['id']}/status",
        json={"status": "Archived"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 422


def test_ai_description_endpoint_returns_clear_configuration_error(client: TestClient, monkeypatch):
    from app.api import routes
    from app.ai.service import AIServiceError

    token = token_for(client, "alice@example.com", "AlicePass123!")

    def unavailable(_title: str) -> str:
        raise AIServiceError("AI service is not configured; set OPENAI_API_KEY")

    monkeypatch.setattr(routes, "generate_description", unavailable)
    response = client.post(
        "/api/tasks/generate-description",
        json={"title": "Plan a launch"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 503
    assert "OPENAI_API_KEY" in response.json()["detail"]