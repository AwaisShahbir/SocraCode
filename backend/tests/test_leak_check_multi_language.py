import re
import pytest
from app.categories import BugCategory
from app.hints.templates_java import HINT_TEMPLATES_JAVA
from app.hints.templates_cpp import HINT_TEMPLATES_CPP

LEAK_CODE_PATTERNS = [
    r"def\s+[a-zA-Z0-9_]+\s*\(",
    r"return\s+[a-zA-Z0-9_]+",
    r"=\s*[a-zA-Z0-9_]+\s*[\+\-\*\/]",
    r"\bimport\s+[a-zA-Z0-9_]+",
    r"\bfor\s+[a-zA-Z0-9_]+\s+in\s+",
    r"\bwhile\s+[a-zA-Z0-9_]+\s*<",
    r"\bpublic\s+static\s+void\s+main\b",
    r"\bSystem\.out\.println\(",
    r"\bstd::cout\s*<<",
    r"#include\s+<",
]


def test_leak_check_java_templates_levels_1_to_3():
    """Verify that Java hint templates for Levels 1 to 3 contain zero solution code leaks."""
    for category, levels in HINT_TEMPLATES_JAVA.items():
        for lvl in [1, 2, 3]:
            template = levels.get(lvl, "")
            assert len(template) > 10, f"Java Template for {category.value} L{lvl} is too short"
            for pattern in LEAK_CODE_PATTERNS:
                match = re.search(pattern, template)
                assert match is None, (
                    f"LEAK DETECTED in Java {category.value} Level {lvl}: "
                    f"Found pattern '{pattern}' in text: '{template}'"
                )


def test_leak_check_cpp_templates_levels_1_to_3():
    """Verify that C++ hint templates for Levels 1 to 3 contain zero solution code leaks."""
    for category, levels in HINT_TEMPLATES_CPP.items():
        for lvl in [1, 2, 3]:
            template = levels.get(lvl, "")
            assert len(template) > 10, f"C++ Template for {category.value} L{lvl} is too short"
            for pattern in LEAK_CODE_PATTERNS:
                match = re.search(pattern, template)
                assert match is None, (
                    f"LEAK DETECTED in C++ {category.value} Level {lvl}: "
                    f"Found pattern '{pattern}' in text: '{template}'"
                )
