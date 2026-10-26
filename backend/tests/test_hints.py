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


def test_level_gate_full_five_levels_progression():
    """Test that LevelGate enforces unlocking 1 -> 2 -> 3 -> 4 -> 5 strictly in order."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_hints_5.db")
        init_db(db_path)
        repo = AttemptRepository(db_path=db_path)
        gate = LevelGate(repository=repo)

        attempt = repo.create_attempt(
            language="python",
            source="web",
            code="def add(a, b)\n    return a + b",
            error_text="SyntaxError: expected ':'",
            category=BugCategory.SYNTAX_ERROR.value,
            concept="syntax_rules",
            buggy_line=1,
            confidence=1.0,
            max_level_allowed=5,
        )
        attempt_id = attempt["id"]
        assert attempt["current_level"] == 0

        # Level 1: Nudge
        h1 = gate.unlock_next_hint(attempt_id)
        assert h1.level == 1
        assert h1.level_name == "Nudge"
        assert "?" in h1.text

        # Level 2: Concept
        h2 = gate.unlock_next_hint(attempt_id)
        assert h2.level == 2
        assert h2.level_name == "Concept"

        # Level 3: Location
        h3 = gate.unlock_next_hint(attempt_id)
        assert h3.level == 3
        assert h3.level_name == "Location"
        assert "line 1" in h3.text

        # Level 4: Similar Example
        h4 = gate.unlock_next_hint(attempt_id)
        assert h4.level == 4
        assert h4.level_name == "Similar Example"
        assert h4.example_code is not None

        # Level 5: Full Solution
        h5 = gate.unlock_next_hint(attempt_id)
        assert h5.level == 5
        assert h5.level_name == "Full Solution"
        assert h5.solution_code is not None
        assert "def add(a, b):" in h5.solution_code
        assert h5.is_last_available_level is True

        # Beyond level 5 -> LevelGateError
        with pytest.raises(LevelGateError):
            gate.unlock_next_hint(attempt_id)
