from pathlib import Path

import pytest

from app.database import connection
from app.services.session_manager import (
    create_anonymous_session,
    get_session_id,
    hash_session_token,
)


@pytest.fixture
def session_database(tmp_path, monkeypatch):
    database_path = tmp_path / "session_test.db"

    monkeypatch.setattr(
        connection,
        "DATABASE_PATH",
        database_path,
    )

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

    return database_path


def test_session_token_is_unique(session_database):
    first_token, _ = create_anonymous_session()
    second_token, _ = create_anonymous_session()

    assert first_token != second_token


def test_sessions_have_different_ids(session_database):
    _, first_id = create_anonymous_session()
    _, second_id = create_anonymous_session()

    assert first_id != second_id


def test_fake_token_is_rejected(session_database):
    create_anonymous_session()

    fake_token = "A" * 43

    assert get_session_id(fake_token) is None


def test_raw_token_is_not_stored(session_database):
    token, session_id = create_anonymous_session()

    with connection.get_database_connection() as conn:
        stored_hash = conn.execute(
            """
            SELECT token_hash
            FROM investigation_sessions
            WHERE id = ?
            """,
            (session_id,),
        ).fetchone()[0]

    assert stored_hash != token
    assert stored_hash == hash_session_token(token)
    assert get_session_id(token) == session_id


@pytest.mark.parametrize(
    "invalid_token",
    [
        None,
        "",
        "short",
        "X" * 129,
    ],
)
def test_invalid_token_is_rejected(
    session_database,
    invalid_token,
):
    assert get_session_id(invalid_token) is None



def test_session_expiration(session_database):
    from datetime import datetime, timedelta, timezone
    from app.services.session_manager import get_session_id

    token, session_id = create_anonymous_session()

    with connection.get_database_connection() as conn:
        conn.execute(
            "UPDATE investigation_sessions SET expires_at = ? WHERE id = ?",
            (
                (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
                session_id,
            ),
        )
        conn.commit()

    assert get_session_id(token) is None


def test_session_revocation(session_database):
    from app.services.session_manager import revoke_anonymous_session

    token, session_id = create_anonymous_session()

    assert get_session_id(token) == session_id
    assert revoke_anonymous_session(token) is True
    assert get_session_id(token) is None
    assert revoke_anonymous_session(token) is False


def test_session_without_expiration_is_rejected(session_database):
    token, session_id = create_anonymous_session()

    with connection.get_database_connection() as conn:
        conn.execute(
            "UPDATE investigation_sessions SET expires_at = NULL WHERE id = ?",
            (session_id,),
        )
        conn.commit()

    assert get_session_id(token) is None


def test_new_session_has_seven_day_expiration(session_database):
    from datetime import datetime, timedelta, timezone

    token, session_id = create_anonymous_session()

    with connection.get_database_connection() as conn:
        created_at, expires_at = conn.execute(
            "SELECT created_at, expires_at FROM investigation_sessions WHERE id = ?",
            (session_id,),
        ).fetchone()

    duration = (
        datetime.fromisoformat(expires_at)
        - datetime.fromisoformat(created_at)
    )

    assert duration == timedelta(days=7)
    assert get_session_id(token) == session_id
