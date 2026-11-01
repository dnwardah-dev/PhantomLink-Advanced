import pytest
from fastapi.testclient import TestClient

from main import app, limiter
from app.database import connection
from app.services.session_manager import get_session_id


TRUSTED_ORIGIN = "http://127.0.0.1:5173"


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "rotation_api_test.db"

    monkeypatch.setattr(connection, "DATABASE_PATH", db_path)
    monkeypatch.setenv("PHANTOMLINK_COOKIE_SECURE", "false")

    with connection.get_database_connection() as conn:
        conn.executescript("""
            CREATE TABLE investigation_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_hash TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                expires_at TEXT,
                revoked_at TEXT
            );

            CREATE TABLE investigations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hostname TEXT NOT NULL,
                risk_score INTEGER,
                risk_level TEXT NOT NULL,
                indicators_json TEXT NOT NULL,
                analysis_type TEXT NOT NULL DEFAULT 'offline_heuristic',
                created_at TEXT NOT NULL,
                session_id INTEGER REFERENCES investigation_sessions(id),
                CHECK (risk_score IS NULL OR risk_score BETWEEN 0 AND 100)
            );
        """)

    limiter.reset()

    with TestClient(
        app,
        headers={"Origin": TRUSTED_ORIGIN},
    ) as test_client:
        yield test_client

    limiter.reset()


def test_rotation_preserves_history(client):
    scan = client.post(
        "/api/investigate",
        json={"url": "https://example.com/verify-account"},
    )
    assert scan.status_code == 200, scan.text

    original_token = client.cookies.get("phantomlink_session")
    original_session_id = get_session_id(original_token)

    before = client.get("/api/history")
    assert before.status_code == 200
    original_history = before.json()["history"]
    assert len(original_history) == 1

    rotated = client.post("/api/session/rotate")
    assert rotated.status_code == 200, rotated.text

    new_token = client.cookies.get("phantomlink_session")

    assert new_token != original_token
    assert get_session_id(original_token) is None
    assert get_session_id(new_token) == original_session_id

    after = client.get("/api/history")
    assert after.status_code == 200
    assert after.json()["history"] == original_history


def test_rotation_requires_valid_session(client):
    response = client.post("/api/session/rotate")
    assert response.status_code == 401


def test_rotation_cookie_attributes(client):
    assert client.post("/api/session").status_code == 200

    response = client.post("/api/session/rotate")
    assert response.status_code == 200

    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie
    assert "samesite=lax" in cookie


def test_rotation_does_not_expose_token(client):
    assert client.post("/api/session").status_code == 200

    response = client.post("/api/session/rotate")
    token = client.cookies.get("phantomlink_session")

    assert response.status_code == 200
    assert token not in response.text
    assert "token_hash" not in response.text


def test_old_token_cannot_access_history(client):
    assert client.post("/api/session").status_code == 200
    old_token = client.cookies.get("phantomlink_session")

    assert client.post("/api/session/rotate").status_code == 200

    client.cookies.set(
        "phantomlink_session",
        old_token,
        domain="testserver.local",
        path="/",
    )

    response = client.get("/api/history")
    assert response.status_code == 401
