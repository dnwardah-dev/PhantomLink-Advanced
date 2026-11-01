import re
import pytest
from fastapi.testclient import TestClient

from main import app, limiter
from app.database import connection
from app.services.session_manager import (
    get_session_id,
    hash_session_token,
)


@pytest.fixture
def client(tmp_path, monkeypatch):
    database_path = tmp_path / "cookie_test.db"

    monkeypatch.setattr(connection, "DATABASE_PATH", database_path)
    monkeypatch.setenv("PHANTOMLINK_COOKIE_SECURE", "false")

    with connection.get_database_connection() as conn:
        conn.execute("""
            CREATE TABLE investigation_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_hash TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                expires_at TEXT,
                revoked_at TEXT
            )
        """)

    limiter.reset()

    with TestClient(app, headers={"Origin": "http://127.0.0.1:5173"}) as test_client:
        yield test_client

    limiter.reset()


def test_session_cookie_security_attributes(client):
    response = client.post("/api/session")

    assert response.status_code == 200

    cookie = response.headers["set-cookie"].lower()

    assert "httponly" in cookie
    assert "samesite=lax" in cookie
    match = re.search(r"max-age=(\d+)", cookie)
    assert match is not None

    max_age = int(match.group(1))
    assert 1 <= max_age <= 604800


def test_existing_session_is_reused(client):
    first = client.post("/api/session")
    first_token = client.cookies.get("phantomlink_session")

    second = client.post("/api/session")
    second_token = client.cookies.get("phantomlink_session")

    assert first.status_code == 200
    assert second.status_code == 200
    assert first_token == second_token
    assert get_session_id(first_token) is not None


def test_invalid_cookie_is_replaced(client):
    client.cookies.set(
        "phantomlink_session",
        "invalid-token",
        domain="testserver.local",
        path="/",
    )

    response = client.post("/api/session")
    token = client.cookies.get("phantomlink_session")

    assert response.status_code == 200
    assert token != "invalid-token"
    assert get_session_id(token) is not None


def test_token_not_exposed_in_json(client):
    response = client.post("/api/session")
    token = client.cookies.get("phantomlink_session")

    assert response.status_code == 200
    assert token not in response.text
    assert "token_hash" not in response.text
    assert response.json()["status"] == "active"


def test_only_token_hash_is_stored(client):
    response = client.post("/api/session")
    token = client.cookies.get("phantomlink_session")

    assert response.status_code == 200

    with connection.get_database_connection() as conn:
        stored_hash = conn.execute(
            "SELECT token_hash FROM investigation_sessions"
        ).fetchone()[0]

    assert stored_hash == hash_session_token(token)
    assert stored_hash != token
