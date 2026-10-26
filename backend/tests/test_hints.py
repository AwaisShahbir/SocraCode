import pytest
import tempfile
import os
from app.categories import BugCategory
from app.hints.templates import HINT_TEMPLATES_PYTHON
from app.hints.level_gate import LevelGate, LevelGateError
from app.db.database import init_db
from app.db.repository import AttemptRepository


def test_leak_check_levels_1_to_3():
    """
    Automated check verifying that hint levels 1 to 3 contain ZERO code fixes,
    functions, assignment fixes, or solution syntax.
    """
    prohibited_code_patterns = [
        "def ",
        "return ",
        "lambda ",
        " = ",
        "import ",
        "class ",
    ]

    for category, level_map in HINT_TEMPLATES_PYTHON.items():
        for level in (1, 2, 3):
            template = level_map[level]
            # Level 1 must be a question
            if level == 1:
                assert "?" in template, f"Level 1 hint for {category} must be a guiding question ending with '?'"

            # Must not contain code solutions
            for pattern in prohibited_code_patterns:
                assert pattern not in template, (
                    f"Leak violation: Found code pattern '{pattern}' in level {level} for {category}: '{template}'"
                )


def test_level_gate_sequential_progression():
    """Test that LevelGate enforces unlocking 1 -> 2 -> 3 strictly in order."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_hints.db")
        init_db(db_path)
        repo = AttemptRepository(db_path=db_path)
        gate = LevelGate(repository=repo)

        attempt = repo.create_attempt(
            language="python",
            source="web",
            code="print(x)",
            error_text="NameError: name 'x' is not defined",
            category=BugCategory.UNDEFINED_NAME.value,
            concept="variable_scope_and_declaration",
            buggy_line=1,
            confidence=1.0,
            max_level_allowed=3,
        )
        attempt_id = attempt["id"]
        assert attempt["current_level"] == 0

        # 1. Unlock Level 1 (Nudge)
        hint_1 = gate.unlock_next_hint(attempt_id)
        assert hint_1.level == 1
        assert hint_1.level_name == "Nudge"
        assert "?" in hint_1.text

        # 2. Unlock Level 2 (Concept)
        hint_2 = gate.unlock_next_hint(attempt_id)
        assert hint_2.level == 2
        assert hint_2.level_name == "Concept"
        assert "Variable Scope" in hint_2.text

        # 3. Unlock Level 3 (Location)
        hint_3 = gate.unlock_next_hint(attempt_id)
        assert hint_3.level == 3
        assert hint_3.level_name == "Location"
        assert "line 1" in hint_3.text
        assert hint_3.is_last_available_level is True

        # 4. Attempt to unlock Level 4 when max is 3 -> LevelGateError
        with pytest.raises(LevelGateError):
            gate.unlock_next_hint(attempt_id)
