import pytest

from app.database import connection
from app.database.models import (
    save_investigation,
    get_private_investigation_history,
)
from app.services.session_manager import create_anonymous_session


@pytest.fixture
def private_history_db(tmp_path, monkeypatch):
    db_path = tmp_path / "private_history_test.db"
    monkeypatch.setattr(connection, "DATABASE_PATH", db_path)

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

    return db_path


def analysis():
    return {
        "risk_score": 25,
        "risk_level": "LOW",
        "indicators": [
            {"code": "SUSPICIOUS_KEYWORD", "points": 15}
        ],
    }


def test_user_a_only_sees_own_history(private_history_db):
    _, user_a = create_anonymous_session()
    _, user_b = create_anonymous_session()

    save_investigation(
        "https://user-a.example/verify", analysis(), session_id=user_a
    )
    save_investigation(
        "https://user-b.example/login", analysis(), session_id=user_b
    )

    history_a = get_private_investigation_history(user_a)

    assert len(history_a) == 1
    assert history_a[0]["hostname"] == "user-a.example"
    assert "user-b.example" not in str(history_a)


def test_user_b_cannot_see_user_a_history(private_history_db):
    _, user_a = create_anonymous_session()
    _, user_b = create_anonymous_session()

    save_investigation(
        "https://private.example/check", analysis(), session_id=user_a
    )

    assert get_private_investigation_history(user_b) == []


def test_legacy_unowned_history_is_hidden(private_history_db):
    _, user_a = create_anonymous_session()

    save_investigation(
        "https://legacy.example/check", analysis(), session_id=None
    )

    assert get_private_investigation_history(user_a) == []


def test_private_history_respects_limit(private_history_db):
    _, user_a = create_anonymous_session()

    for index in range(5):
        save_investigation(
            f"https://example.com/check-{index}",
            analysis(),
            session_id=user_a,
        )

    history = get_private_investigation_history(user_a, limit=2)

    assert len(history) == 2
    assert history[0]["id"] > history[1]["id"]


@pytest.mark.parametrize("invalid_id", [None, 0, -1, True, "1"])
def test_invalid_session_id_rejected(private_history_db, invalid_id):
    with pytest.raises(ValueError):
        get_private_investigation_history(invalid_id)
