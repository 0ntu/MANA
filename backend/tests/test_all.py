# backend tests
# may split into multiple files when more tests are added
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from zoneinfo import ZoneInfo
from bson import ObjectId
from fastapi.testclient import TestClient
from app.main import app
from app.authentication import (
    create_jwt_token,
    hash_password,
)

est = ZoneInfo("America/New_York")

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def user_id():
    return ObjectId()

@pytest.fixture
def sample_user(user_id):
    return {
        "_id": user_id,
        "username": "testuser",
        "hashed_pass": hash_password("password123"),
        "created_time": datetime.now(est),
        "current_energy": 7.5,
    }

@pytest.fixture
def auth_header(user_id):
    token = create_jwt_token(str(user_id))
    return {"Authorization": f"Bearer {token}"}

# health checks
def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "UF MANA is running"

def test_healthcheck_endpoint(client):
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert "status" in response.json()

# ---

# signup creates account & token
def test_signup_success(client):
    with patch("app.apis.users") as mock_users:
        mock_users.find_one.side_effect = [
            None,
            {"_id": ObjectId(), "username": "newuser", "created_time": datetime.now(est), "current_energy": 0.0}
        ]
        mock_users.insert_one.return_value = MagicMock(inserted_id=ObjectId())

        response = client.post(
            "/authentication/signup",
            json={"username": "newuser", "password": "securepass123"}
        )

        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "user" in data


# valid login returns token
def test_login_success(client, sample_user):
    with patch("app.apis.users") as mock_users:
        mock_users.find_one.return_value = sample_user

        response = client.post(
            "/authentication/login",
            json={"username": "testuser", "password": "password123"}
        )

        assert response.status_code == 200
        assert "access_token" in response.json()


# dashboard summary data for logged in user
def test_dashboard_returns_summary(client, sample_user, auth_header):
    with patch("app.apis.users") as mock_users, \
         patch("app.apis.tasks") as mock_tasks, \
         patch("app.authentication.users", mock_users):
        mock_users.find_one.return_value = sample_user
        mock_tasks.find.return_value = []
        mock_tasks.count_documents.return_value = 0

        response = client.get("/dashboard/summary", headers=auth_header)

        assert response.status_code == 200
        data = response.json()
        assert "current_energy" in data
        assert "mana_stress" in data
        assert "overload_warning" in data


# create task
def test_create_task_success(client, sample_user, auth_header):
    scheduled = (datetime.now(est) + timedelta(hours=2)).isoformat()

    with patch("app.apis.users") as mock_users, \
         patch("app.apis.tasks") as mock_tasks, \
         patch("app.authentication.users", mock_users):
        mock_users.find_one.return_value = sample_user
        mock_tasks.insert_one.return_value = MagicMock(inserted_id=ObjectId())

        response = client.post(
            "/tasks/create",
            headers=auth_header,
            json={
                "title": "Study for exam",
                "scheduled_time": scheduled,
                "energy_cost": 5.0
            }
        )

        assert response.status_code == 201
        assert response.json()["status"] == "planned"


# log energy page
def test_log_energy_success(client, sample_user, auth_header):
    with patch("app.apis.users") as mock_users, \
         patch("app.apis.energy_logs") as mock_logs, \
         patch("app.authentication.users", mock_users):
        mock_users.find_one.return_value = sample_user
        mock_logs.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        mock_users.update_one.return_value = None

        response = client.post(
            "/energy/log",
            headers=auth_header,
            json={"energy_level": 8.5}
        )

        assert response.status_code == 200
        assert response.json()["energy_level"] == 8.5
