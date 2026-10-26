import json
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from app.categories import BugCategory
from app.hints.templates import get_template
from app.db.repository import AttemptRepository
from app.retrieval.tfidf_matcher import retrieve_worked_example
from app.rules.fixer import RuleBasedFixer


class UnlockedHint(BaseModel):
    attempt_id: str
    level: int
    level_name: str
    text: str
    shown_at: str
    is_last_available_level: bool = False
    hint_id: str
    example_code: Optional[str] = None
    solution_code: Optional[str] = None
    explanation: Optional[str] = None
    diff_summary: Optional[str] = None


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
        self.fixer = RuleBasedFixer()

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

        try:
            category = BugCategory(attempt["category"])
        except ValueError:
            category = BugCategory.SYNTAX_ERROR

        example_code = None
        solution_code = None
        explanation = None
        diff_summary = None

        if target_level <= 3:
            # Hydrate template for Levels 1 to 3
            raw_template = get_template(category, target_level)
            undefined_name = "variable"
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
        elif target_level == 4:
            # Level 4: Worked parallel example via TF-IDF retrieval
            example = retrieve_worked_example(
                category=category,
                student_code=attempt["code"],
                error_text=attempt.get("error_text", ""),
            )
            example_code = example.code
            explanation = example.explanation
            hydrated_text = (
                f"Worked Parallel Example: {example.title}\n\n"
                f"{example.problem_description}\n\n"
                f"{example.code}\n\n"
                f"Pattern Note: {example.explanation}"
            )
        elif target_level == 5:
            # Level 5: Full verified solution and detailed explanation
            context = {
                "undefined_name": "variable",
                "suggested_name": None,
            }
            error_text = attempt.get("error_text", "")
            if "name '" in error_text:
                try:
                    context["undefined_name"] = error_text.split("name '")[1].split("'")[0]
                except Exception:
                    pass

            fix_result = self.fixer.generate_fix(
                code=attempt["code"],
                category=category,
                buggy_line=attempt["buggy_line"],
                context=context,
            )

            if fix_result.can_fix and fix_result.fixed_code:
                solution_code = fix_result.fixed_code
                explanation = fix_result.explanation
                diff_summary = fix_result.diff_summary
                hydrated_text = (
                    f"Full Solution & Explanation:\n\n"
                    f"{fix_result.diff_summary}\n\n"
                    f"{fix_result.fixed_code}\n\n"
                    f"Why this fix works:\n{fix_result.explanation}"
                )
            else:
                hydrated_text = (
                    "SocraCode can't verify a full fix for this bug with certainty. "
                    "Review the worked example in Level 4 or ask your instructor."
                )
                explanation = hydrated_text
        else:
            raise LevelGateError(f"Unsupported hint level: {target_level}")

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
            example_code=example_code,
            solution_code=solution_code,
            explanation=explanation,
            diff_summary=diff_summary,
        )
