import json
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from app.categories import BugCategory
from app.hints.templates import get_template
from app.db.repository import AttemptRepository


class UnlockedHint(BaseModel):
    attempt_id: str
    level: int
    level_name: str
    text: str
    shown_at: str
    is_last_available_level: bool = False
    hint_id: str


LEVEL_NAMES = {
    1: "Nudge",
    2: "Concept",
    3: "Location",
    4: "Similar Example",
    5: "Full Solution",
}


class LevelGateError(Exception):
    """Raised when level progression violates sequential unlocking constraints."""
    pass


class LevelGate:
    """Enforces sequential hint unlocking on the backend."""

    def __init__(self, repository: Optional[AttemptRepository] = None):
        self.repo = repository or AttemptRepository()

    def unlock_next_hint(self, attempt_id: str) -> UnlockedHint:
        attempt = self.repo.get_attempt(attempt_id)
        if not attempt:
            raise LevelGateError(f"Attempt with ID '{attempt_id}' not found.")

        current_level = attempt["current_level"]
        max_allowed = attempt["max_level_allowed"]

        if current_level >= max_allowed:
            raise LevelGateError(
                f"Maximum allowed hint level ({max_allowed}) already reached for this attempt."
            )

        target_level = current_level + 1

        # Hydrate template
        try:
            category = BugCategory(attempt["category"])
        except ValueError:
            category = BugCategory.SYNTAX_ERROR

        raw_template = get_template(category, target_level)

        # Contextual hydration
        undefined_name = "variable"
        # Parse error text if available to find identifier
        error_text = attempt.get("error_text", "")
        if "name '" in error_text:
            try:
                undefined_name = error_text.split("name '")[1].split("'")[0]
            except Exception:
                pass

        hydrated_text = raw_template.format(
            line_number=attempt["buggy_line"],
            undefined_name=undefined_name,
        )

        template_id = f"py_{category.value}_lvl{target_level}"

        # Persist hint event
        event = self.repo.record_hint_event(
            attempt_id=attempt_id,
            level=target_level,
            template_id=template_id,
            hint_text=hydrated_text,
        )

        # Update attempt level
        self.repo.update_attempt_level(attempt_id, target_level)

        return UnlockedHint(
            attempt_id=attempt_id,
            level=target_level,
            level_name=LEVEL_NAMES.get(target_level, f"Level {target_level}"),
            text=hydrated_text,
            shown_at=event["shown_at"],
            is_last_available_level=(target_level >= max_allowed),
            hint_id=event["id"],
        )
