import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.db.database import get_db_connection, init_db


class AttemptRepository:
    """Data access repository for student attempts and hint events."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        if self.db_path:
            init_db(self.db_path)
        else:
            init_db()

    def _get_connection(self):
        if self.db_path:
            return get_db_connection(self.db_path)
        return get_db_connection()

    def create_attempt(
        self,
        language: str,
        source: str,
        code: str,
        error_text: str,
        category: str,
        concept: str,
        buggy_line: int,
        confidence: float,
        user_id: Optional[str] = None,
        assignment_id: Optional[str] = None,
        max_level_allowed: int = 3,
    ) -> Dict[str, Any]:
        attempt_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc).isoformat()

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO attempts (
                    id, user_id, assignment_id, language, source, code, error_text,
                    category, concept, buggy_line, confidence, current_level,
                    max_level_allowed, started_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    attempt_id,
                    user_id,
                    assignment_id,
                    language,
                    source,
                    code,
                    error_text,
                    category,
                    concept,
                    buggy_line,
                    confidence,
                    0,  # starts at level 0 (no hints unlocked yet)
                    max_level_allowed,
                    started_at,
                ),
            )

        return self.get_attempt(attempt_id)  # type: ignore

    def get_attempt(self, attempt_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM attempts WHERE id = ?", (attempt_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def update_attempt_level(self, attempt_id: str, new_level: int) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE attempts SET current_level = ? WHERE id = ?",
                (new_level, attempt_id),
            )

    def record_hint_event(
        self,
        attempt_id: str,
        level: int,
        template_id: str,
        hint_text: str,
    ) -> Dict[str, Any]:
        event_id = str(uuid.uuid4())
        shown_at = datetime.now(timezone.utc).isoformat()

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO hint_events (id, attempt_id, level, template_id, hint_text, shown_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (event_id, attempt_id, level, template_id, hint_text, shown_at),
            )

        return {
            "id": event_id,
            "attempt_id": attempt_id,
            "level": level,
            "template_id": template_id,
            "hint_text": hint_text,
            "shown_at": shown_at,
            "helpful": None,
        }

    def get_hint_events(self, attempt_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM hint_events WHERE attempt_id = ? ORDER BY level ASC",
                (attempt_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def record_hint_feedback(self, hint_id: str, helpful: bool) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE hint_events SET helpful = ? WHERE id = ?",
                (1 if helpful else 0, hint_id),
            )
            return cursor.rowcount > 0

    def resolve_attempt(self, attempt_id: str, reflection: Optional[str] = None) -> bool:
        resolved_at = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE attempts SET resolved_at = ?, reflection = ? WHERE id = ?",
                (resolved_at, reflection, attempt_id),
            )
            return cursor.rowcount > 0
