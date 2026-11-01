import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent / "phantomlink.db"


def initialize_database():
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS investigations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hostname TEXT NOT NULL,
                risk_score INTEGER,
                risk_level TEXT NOT NULL,
                indicators_json TEXT NOT NULL,
                analysis_type TEXT NOT NULL DEFAULT 'offline_heuristic',
                created_at TEXT NOT NULL,
                CHECK (risk_score IS NULL OR risk_score BETWEEN 0 AND 100)
            )
        """)

        conn.commit()

    return DATABASE_PATH


def get_database_connection():
    """Create a configured SQLite connection."""
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    conn.execute("PRAGMA busy_timeout = 10000")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
