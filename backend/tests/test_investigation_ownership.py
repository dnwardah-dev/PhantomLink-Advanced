import sqlite3

import pytest
from fastapi.testclient import TestClient

from main import app, limiter
from app.database import connection
from app.services.session_manager import get_session_id


@pytest.fixture
def ownership_database(tmp_path, monkeypatch):
    db_path = tmp_path / "ownership_test.db"

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
    yield db_path
    limiter.reset()


def investigate(client, url):
    response = client.post(
        "/api/investigate",
        json={"url": url},
    )
    assert response.status_code == 200, response.text
    return response


def test_investigation_creates_owner_session(ownership_database):
    with TestClient(app, headers={"Origin": "http://127.0.0.1:5173"}) as client:
        response = investigate(
            client, "https://example.com/verify-account"
        )

        token = client.cookies.get("phantomlink_session")
        session_id = get_session_id(token)

        assert session_id is not None

        investigation_id = response.json()["investigation"]["id"]

        with connection.get_database_connection() as conn:
            row = conn.execute(
                "SELECT session_id FROM investigations WHERE id = ?",
                (investigation_id,),
            ).fetchone()

        assert row is not None
        assert row[0] == session_id


def test_different_users_have_different_sessions(ownership_database):
    with TestClient(app, headers={"Origin": "http://127.0.0.1:5173"}) as user_a, TestClient(app, headers={"Origin": "http://127.0.0.1:5173"}) as user_b:
        investigate(user_a, "https://example.com/check-a")
        investigate(user_b, "https://example.org/check-b")

        token_a = user_a.cookies.get("phantomlink_session")
        token_b = user_b.cookies.get("phantomlink_session")

        assert token_a != token_b
        assert get_session_id(token_a) != get_session_id(token_b)


def test_existing_session_is_reused(ownership_database):
    with TestClient(app, headers={"Origin": "http://127.0.0.1:5173"}) as client:
        first = investigate(client, "https://example.com/check-one")
        token_before = client.cookies.get("phantomlink_session")

        second = investigate(client, "https://example.com/check-two")
        token_after = client.cookies.get("phantomlink_session")

        assert first.status_code == 200
        assert second.status_code == 200
        assert token_before == token_after

        session_id = get_session_id(token_after)

        with connection.get_database_connection() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM investigations WHERE session_id = ?",
                (session_id,),
            ).fetchone()[0]

        assert count == 2


def test_investigation_does_not_expose_session_token(ownership_database):
    with TestClient(app, headers={"Origin": "http://127.0.0.1:5173"}) as client:
        response = investigate(client, "https://example.com/check")
        token = client.cookies.get("phantomlink_session")

        assert token not in response.text
        assert "session_id" not in response.json()["investigation"]
