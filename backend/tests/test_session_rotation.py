import pytest

from app.database import connection
from app.services.session_manager import (
    create_anonymous_session,
    get_session_id,
    hash_session_token,
    rotate_anonymous_session,
)


@pytest.fixture
def rotation_db(tmp_path, monkeypatch):
    path = tmp_path / "rotation_test.db"
    monkeypatch.setattr(connection, "DATABASE_PATH", path)

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

    return path


def test_rotation_creates_new_token(rotation_db):
    old_token, session_id = create_anonymous_session()

    result = rotate_anonymous_session(old_token)

    assert result is not None
    new_token, new_id = result
    assert new_token != old_token
    assert new_id == session_id


def test_old_token_is_rejected(rotation_db):
    old_token, _ = create_anonymous_session()

    new_token, session_id = rotate_anonymous_session(old_token)

    assert get_session_id(old_token) is None
    assert get_session_id(new_token) == session_id


def test_rotation_preserves_expiration(rotation_db):
    old_token, session_id = create_anonymous_session()

    with connection.get_database_connection() as conn:
        before = conn.execute(
            "SELECT expires_at FROM investigation_sessions WHERE id = ?",
            (session_id,),
        ).fetchone()[0]

    new_token, new_id = rotate_anonymous_session(old_token)

    with connection.get_database_connection() as conn:
        after = conn.execute(
            "SELECT expires_at FROM investigation_sessions WHERE id = ?",
            (new_id,),
        ).fetchone()[0]

    assert before == after


@pytest.mark.parametrize(
    "invalid_token",
    [None, "", "short", "X" * 129],
)
def test_invalid_token_cannot_rotate(rotation_db, invalid_token):
    assert rotate_anonymous_session(invalid_token) is None


def test_old_token_cannot_rotate_twice(rotation_db):
    old_token, _ = create_anonymous_session()

    first_rotation = rotate_anonymous_session(old_token)
    second_rotation = rotate_anonymous_session(old_token)

    assert first_rotation is not None
    assert second_rotation is None
