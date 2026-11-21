import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient

SERVICE_ROOT = Path(__file__).resolve().parents[1]
TEST_DATABASE = SERVICE_ROOT / "test_user_profile.db"

if TEST_DATABASE.exists():
    TEST_DATABASE.unlink()

os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DATABASE.as_posix()}"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"
sys.path.insert(0, str(SERVICE_ROOT))

from app import app  # noqa: E402


def test_user_registration_login_and_profile_flow():
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok", "service": "user-profile"}

        registration = {
            "name": "Ada Lovelace",
            "email": "Ada@example.com",
            "mobile": "+905551112233",
            "password": "secure-password",
        }
        created = client.post("/auth/register", json=registration)
        assert created.status_code == 201
        assert created.json() == {
            "id": 1,
            "name": "Ada Lovelace",
            "email": "ada@example.com",
            "mobile": "+905551112233",
        }
        assert "password" not in created.json()

        duplicate = client.post("/auth/register", json=registration)
        assert duplicate.status_code == 409

        invalid_login = client.post("/auth/login", json={"email": "ada@example.com", "password": "wrong-password"})
        assert invalid_login.status_code == 401

        login = client.post("/auth/login", json={"email": "ada@example.com", "password": "secure-password"})
        assert login.status_code == 200
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        profile = client.get("/users/me", headers=headers)
        assert profile.status_code == 200
        assert profile.json()["email"] == "ada@example.com"

        updated = client.put("/users/me", headers=headers, json={"name": "Ada Byron"})
        assert updated.status_code == 200
        assert updated.json()["name"] == "Ada Byron"


def test_profile_requires_a_valid_bearer_token():
    with TestClient(app) as client:
        assert client.get("/users/me").status_code == 401
        assert client.get("/users/me", headers={"Authorization": "Bearer invalid"}).status_code == 401
