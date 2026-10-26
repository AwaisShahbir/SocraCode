import sqlite3
import os
from contextlib import contextmanager
from typing import Generator
from app.config import settings


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS attempts (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    assignment_id TEXT,
    language TEXT NOT NULL,
    source TEXT NOT NULL,
    code TEXT NOT NULL,
    error_text TEXT NOT NULL,
    category TEXT NOT NULL,
    concept TEXT NOT NULL,
    buggy_line INTEGER NOT NULL,
    confidence REAL NOT NULL,
    current_level INTEGER NOT NULL DEFAULT 0,
    max_level_allowed INTEGER NOT NULL DEFAULT 3,
    started_at TEXT NOT NULL,
    resolved_at TEXT,
    reflection TEXT
);

CREATE TABLE IF NOT EXISTS hint_events (
    id TEXT PRIMARY KEY,
    attempt_id TEXT NOT NULL,
    level INTEGER NOT NULL,
    template_id TEXT NOT NULL,
    hint_text TEXT NOT NULL,
    shown_at TEXT NOT NULL,
    helpful INTEGER,
    FOREIGN KEY(attempt_id) REFERENCES attempts(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_attempts_user_id ON attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_hint_events_attempt_id ON hint_events(attempt_id);
"""


def init_db(db_path: str = settings.db_path) -> None:
    """Initialize the SQLite database schema."""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()


@contextmanager
def get_db_connection(db_path: str = settings.db_path) -> Generator[sqlite3.Connection, None, None]:
    """Provide a transactional SQLite database connection."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
