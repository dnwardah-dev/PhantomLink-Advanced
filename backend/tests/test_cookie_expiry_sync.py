import re
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from main import app, limiter
from app.database import connection


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "cookie_expiry_test.db"
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
        """)

    limiter.reset()

    with TestClient(
        app,
        headers={"Origin": "http://127.0.0.1:5173"},
    ) as test_client:
        yield test_client

    limiter.reset()


def cookie_max_age(response):
    cookie = response.headers["set-cookie"]
    match = re.search(r"max-age=(\d+)", cookie.lower())
    assert match is not None
    return int(match.group(1))


def test_rotation_preserves_remaining_cookie_lifetime(client):
    initial = client.post("/api/session")
    assert initial.status_code == 200

    with connection.get_database_connection() as conn:
        conn.execute(
            """
            UPDATE investigation_sessions
            SET expires_at = ?
            """,
            (
                (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            ),
        )
        conn.commit()

    rotated = client.post("/api/session/rotate")

    assert rotated.status_code == 200
    assert 3500 <= cookie_max_age(rotated) <= 3600


def test_existing_session_does_not_extend_cookie_lifetime(client):
    initial = client.post("/api/session")
    assert initial.status_code == 200

    with connection.get_database_connection() as conn:
        conn.execute(
            "UPDATE investigation_sessions SET expires_at = ?",
            (
                (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            ),
        )
        conn.commit()

    refreshed = client.post("/api/session")

    assert refreshed.status_code == 200
    assert 3500 <= cookie_max_age(refreshed) <= 3600
