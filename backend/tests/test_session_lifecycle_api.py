from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from main import app, limiter
from app.database import connection


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "lifecycle_test.db"

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
        headers={"Origin": "http://127.0.0.1:5173"},
    ) as test_client:
        yield test_client

    limiter.reset()


def test_expired_session_cannot_read_history(client):
    assert client.post("/api/session").status_code == 200

    with connection.get_database_connection() as conn:
        conn.execute(
            "UPDATE investigation_sessions SET expires_at = ?",
            (
                (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
            ),
        )
        conn.commit()

    response = client.get("/api/history")
    assert response.status_code == 401


def test_revoked_session_cannot_read_history(client):
    assert client.post("/api/session").status_code == 200

    with connection.get_database_connection() as conn:
        conn.execute(
            "UPDATE investigation_sessions SET revoked_at = ?",
            (datetime.now(timezone.utc).isoformat(),),
        )
        conn.commit()

    response = client.get("/api/history")
    assert response.status_code == 401


def test_expired_session_is_replaced(client):
    assert client.post("/api/session").status_code == 200
    old_token = client.cookies.get("phantomlink_session")

    with connection.get_database_connection() as conn:
        conn.execute(
            "UPDATE investigation_sessions SET expires_at = ?",
            (
                (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
            ),
        )
        conn.commit()

    response = client.post("/api/session")
    new_token = client.cookies.get("phantomlink_session")

    assert response.status_code == 200
    assert new_token != old_token


def test_revoked_session_is_replaced(client):
    assert client.post("/api/session").status_code == 200
    old_token = client.cookies.get("phantomlink_session")

    with connection.get_database_connection() as conn:
        conn.execute(
            "UPDATE investigation_sessions SET revoked_at = ?",
            (datetime.now(timezone.utc).isoformat(),),
        )
        conn.commit()

    response = client.post("/api/session")
    new_token = client.cookies.get("phantomlink_session")

    assert response.status_code == 200
    assert new_token != old_token
