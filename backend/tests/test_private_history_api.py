import pytest
from fastapi.testclient import TestClient

from main import app, limiter
from app.database import connection
from app.database.models import save_investigation


@pytest.fixture
def private_api_db(tmp_path, monkeypatch):
    db_path = tmp_path / "private_api_test.db"

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


def scan(client, url):
    response = client.post(
        "/api/investigate",
        json={"url": url},
    )
    assert response.status_code == 200, response.text
    return response


def test_users_only_see_their_own_history(private_api_db):
    with TestClient(app, headers={"Origin": "http://127.0.0.1:5173"}) as user_a, TestClient(app, headers={"Origin": "http://127.0.0.1:5173"}) as user_b:
        scan(user_a, "https://example.com/verify")
        scan(user_b, "https://example.org/account")

        history_a = user_a.get("/api/history")
        history_b = user_b.get("/api/history")

        assert history_a.status_code == 200
        assert history_b.status_code == 200

        records_a = history_a.json()["history"]
        records_b = history_b.json()["history"]

        assert len(records_a) == 1
        assert len(records_b) == 1

        assert records_a[0]["hostname"] == "example.com"
        assert records_b[0]["hostname"] == "example.org"

        assert records_a[0]["id"] != records_b[0]["id"]


def test_no_cookie_cannot_access_history(private_api_db):
    with TestClient(app, headers={"Origin": "http://127.0.0.1:5173"}) as visitor:
        response = visitor.get("/api/history")

        assert response.status_code == 401


def test_fake_cookie_cannot_access_history(private_api_db):
    with TestClient(app, headers={"Origin": "http://127.0.0.1:5173"}) as visitor:
        visitor.cookies.set(
            "phantomlink_session",
            "invalid-token",
            domain="testserver.local",
            path="/",
        )

        response = visitor.get("/api/history")

        assert response.status_code == 401


def test_legacy_history_is_not_visible(private_api_db):
    save_investigation(
        "https://legacy.example/private",
        {
            "risk_score": 10,
            "risk_level": "LOW",
            "indicators": [],
        },
        session_id=None,
    )

    with TestClient(app, headers={"Origin": "http://127.0.0.1:5173"}) as visitor:
        session_response = visitor.post("/api/session")
        assert session_response.status_code == 200

        history = visitor.get("/api/history")

        assert history.status_code == 200
        assert history.json()["history"] == []


def test_history_requires_valid_limit(private_api_db):
    with TestClient(app, headers={"Origin": "http://127.0.0.1:5173"}) as visitor:
        assert visitor.post("/api/session").status_code == 200

        for limit in (0, -1, 101):
            response = visitor.get(
                "/api/history",
                params={"limit": limit},
            )
            assert response.status_code == 422
