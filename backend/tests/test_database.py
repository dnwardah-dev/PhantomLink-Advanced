from pathlib import Path

import pytest

from app.database import models
from app.database import connection


@pytest.fixture
def temporary_database(tmp_path, monkeypatch):
    db_path = tmp_path / "phantomlink_test.db"

    monkeypatch.setattr(connection, "DATABASE_PATH", db_path)

    with connection.get_database_connection() as conn:
        conn.execute("""
            CREATE TABLE investigations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hostname TEXT NOT NULL,
                risk_score INTEGER,
                risk_level TEXT NOT NULL,
                indicators_json TEXT NOT NULL,
                analysis_type TEXT NOT NULL DEFAULT 'offline_heuristic',
                created_at TEXT NOT NULL,
                session_id INTEGER,
                CHECK (risk_score IS NULL OR risk_score BETWEEN 0 AND 100)
            )
        """)

    return db_path


def test_save_investigation(temporary_database):
    analysis = {
        "risk_score": 25,
        "risk_level": "LOW",
        "indicators": [
            {"code": "SUSPICIOUS_KEYWORD", "points": 15}
        ]
    }

    investigation_id = models.save_investigation(
        "https://example.com/verify-account",
        analysis
    )

    assert isinstance(investigation_id, int)
    assert investigation_id > 0


def test_history_preserves_privacy(temporary_database):
    models.save_investigation(
        "https://example.com/private-secret-path",
        {
            "risk_score": 10,
            "risk_level": "LOW",
            "indicators": []
        }
    )

    history = models.get_investigation_history(20)

    assert len(history) == 1
    assert history[0]["hostname"] == "example.com"
    assert "private-secret-path" not in str(history)
    assert "url" not in history[0]


def test_history_limit(temporary_database):
    for index in range(5):
        models.save_investigation(
            f"https://example.com/check-{index}",
            {
                "risk_score": 5,
                "risk_level": "LOW",
                "indicators": []
            }
        )

    history = models.get_investigation_history(2)

    assert len(history) == 2
    assert history[0]["id"] > history[1]["id"]


def test_invalid_risk_score_rejected(temporary_database):
    with pytest.raises(Exception):
        models.save_investigation(
            "https://example.com",
            {
                "risk_score": 150,
                "risk_level": "HIGH",
                "indicators": []
            }
        )
