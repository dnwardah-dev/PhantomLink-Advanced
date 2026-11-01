"""Anonymous investigation session management."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from app.database.connection import get_database_connection


def hash_session_token(token: str) -> str:
    """Hash a session token before database storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_anonymous_session() -> tuple[str, int]:
    """Create a cryptographically random session token."""
    token = secrets.token_urlsafe(32)
    token_hash = hash_session_token(token)
    now = datetime.now(timezone.utc)
    created_at = now.isoformat()
    expires_at = (now + timedelta(days=7)).isoformat()

    with get_database_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO investigation_sessions
                (token_hash, created_at, expires_at)
            VALUES (?, ?, ?)
            """,
            (token_hash, created_at, expires_at),
        )
        conn.commit()
        session_id = cursor.lastrowid

    return token, session_id


def get_session_id(token: str | None) -> int | None:
    """Return session ID only for a recognized token."""
    if not token or not isinstance(token, str):
        return None

    # Reject malformed or oversized values before hashing.
    if len(token) > 128 or len(token) < 32:
        return None

    token_hash = hash_session_token(token)

    with get_database_connection() as conn:
        row = conn.execute(
            """
            SELECT id
            FROM investigation_sessions
            WHERE token_hash = ?
              AND revoked_at IS NULL
              AND expires_at IS NOT NULL
              AND expires_at > ?
            """,
            (token_hash, datetime.now(timezone.utc).isoformat()),
        ).fetchone()

    return row[0] if row else None



def revoke_anonymous_session(token: str | None) -> bool:
    """Revoke an active anonymous session."""
    session_id = get_session_id(token)

    if session_id is None:
        return False

    with get_database_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE investigation_sessions
            SET revoked_at = ?
            WHERE id = ?
              AND revoked_at IS NULL
            """,
            (datetime.now(timezone.utc).isoformat(), session_id),
        )
        conn.commit()

    return cursor.rowcount == 1



def rotate_anonymous_session(token: str | None) -> tuple[str, int] | None:
    """Rotate an active token while preserving its session ID and expiry.

    The conditional UPDATE is atomic. A concurrent request using
    the same old token cannot rotate it successfully twice.
    """
    if not isinstance(token, str) or not 32 <= len(token) <= 128:
        return None

    old_hash = hash_session_token(token)
    new_token = secrets.token_urlsafe(32)
    new_hash = hash_session_token(new_token)
    now = datetime.now(timezone.utc).isoformat()

    with get_database_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE investigation_sessions
            SET token_hash = ?
            WHERE token_hash = ?
              AND revoked_at IS NULL
              AND expires_at IS NOT NULL
              AND expires_at > ?
            """,
            (new_hash, old_hash, now),
        )

        if cursor.rowcount != 1:
            conn.rollback()
            return None

        row = conn.execute(
            """
            SELECT id
            FROM investigation_sessions
            WHERE token_hash = ?
            """,
            (new_hash,),
        ).fetchone()

        if row is None:
            conn.rollback()
            raise RuntimeError("Session rotation verification failed")

        session_id = row[0]
        conn.commit()

    return new_token, session_id



def get_session_remaining_seconds(session_id: int) -> int:
    """Return remaining whole seconds for an active session."""
    if not isinstance(session_id, int) or isinstance(session_id, bool):
        return 0

    with get_database_connection() as conn:
        row = conn.execute(
            """
            SELECT expires_at, revoked_at
            FROM investigation_sessions
            WHERE id = ?
            """,
            (session_id,),
        ).fetchone()

    if row is None or row[1] is not None or not row[0]:
        return 0

    expires_at = datetime.fromisoformat(row[0])
    remaining = (expires_at - datetime.now(timezone.utc)).total_seconds()

    return max(0, int(remaining))
