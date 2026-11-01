import json
import sqlite3
from datetime import datetime, timezone
from urllib.parse import urlsplit

from app.database.connection import get_database_connection


def save_investigation(url: str, analysis: dict, session_id: int | None = None) -> int:
    hostname = urlsplit(url).hostname

    if not hostname:
        raise ValueError("Invalid hostname")

    score = analysis.get("risk_score")
    level = analysis.get("risk_level", "UNASSESSED")

    # Store only controlled evidence fields.
    indicators = [
        {
            "code": str(item.get("code", "")),
            "points": int(item.get("points", 0))
        }
        for item in analysis.get("indicators", [])
    ]

    created_at = datetime.now(timezone.utc).isoformat()

    with get_database_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO investigations (
                hostname,
                risk_score,
                risk_level,
                indicators_json,
                analysis_type,
                created_at,
                session_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                hostname,
                score,
                level,
                json.dumps(indicators),
                "offline_heuristic",
                created_at,
                session_id
            )
        )

        conn.commit()
        return cursor.lastrowid


def get_investigation_history(limit: int = 20) -> list:
    limit = max(1, min(int(limit), 100))

    with get_database_connection() as conn:
        conn.row_factory = sqlite3.Row

        rows = conn.execute(
            """
            SELECT id, hostname, risk_score, risk_level,
                   indicators_json, analysis_type, created_at
            FROM investigations
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

    return [
        {
            **{
                key: value
                for key, value in dict(row).items()
                if key != "indicators_json"
            },
            "indicators": json.loads(row["indicators_json"])
        }
        for row in rows
    ]



def get_private_investigation_history(
    session_id: int,
    limit: int = 20,
) -> list:
    """Return investigations belonging only to the supplied session."""
    if not isinstance(session_id, int) or isinstance(session_id, bool) or session_id <= 0:
        raise ValueError("Valid session ID required")

    limit = max(1, min(int(limit), 100))

    with get_database_connection() as conn:
        conn.row_factory = sqlite3.Row

        rows = conn.execute(
            """
            SELECT id, hostname, risk_score, risk_level,
                   indicators_json, analysis_type, created_at
            FROM investigations
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (session_id, limit),
        ).fetchall()

    return [
        {
            **{
                key: value
                for key, value in dict(row).items()
                if key != "indicators_json"
            },
            "indicators": json.loads(row["indicators_json"]),
        }
        for row in rows
    ]
