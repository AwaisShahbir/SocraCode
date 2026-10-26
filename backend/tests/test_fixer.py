import pytest
import ast
from app.categories import BugCategory
from app.rules.fixer import RuleBasedFixer


def test_fix_missing_colon():
    fixer = RuleBasedFixer()
    code = "def is_valid(x)\n    return x > 0"
    res = fixer.generate_fix(code, BugCategory.SYNTAX_ERROR, buggy_line=1, context={})
    assert res.can_fix is True
    assert res.fixed_code is not None
    assert "def is_valid(x):" in res.fixed_code
    # Validate Python AST of fixed code
    ast.parse(res.fixed_code)


def test_fix_undefined_name_typo():
    fixer = RuleBasedFixer()
    code = "counter = 1\nprint(contuer)"
    res = fixer.generate_fix(
        code,
        BugCategory.UNDEFINED_NAME,
        buggy_line=2,
        context={"undefined_name": "contuer", "suggested_name": "counter"},
    )
    assert res.can_fix is True
    assert res.fixed_code is not None
    assert "print(counter)" in res.fixed_code
    ast.parse(res.fixed_code)


def test_unverified_fix_fallback():
    fixer = RuleBasedFixer()
    code = "def complex_algo():\n    pass"
    res = fixer.generate_fix(code, BugCategory.WRONG_OPERATOR, buggy_line=1, context={})
    assert res.can_fix is False
    assert "can't verify a full fix" in res.explanation
