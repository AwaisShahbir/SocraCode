import pytest
from app.categories import BugCategory
from app.parser.python_parser import PythonErrorParser
from app.rules.python_rules import PythonRuleEngine


def test_rule_match_syntax_error():
    engine = PythonRuleEngine()
    parser = PythonErrorParser()
    code = "for i in range(5)\n    print(i)"
    parsed = parser.parse(code, "")
    match = engine.match(code, parsed)
    assert match.category == BugCategory.SYNTAX_ERROR
    assert match.line_number == 1
    assert match.confidence >= 0.9


def test_rule_match_undefined_name_with_typo():
    engine = PythonRuleEngine()
    parser = PythonErrorParser()
    code = "total_sum = 100\nprint(total_sun)"
    stderr = "NameError: name 'total_sun' is not defined"
    parsed = parser.parse(code, stderr)
    match = engine.match(code, parsed)
    assert match.category == BugCategory.UNDEFINED_NAME
    assert match.line_number == 2
    assert match.context.get("is_typo") is True
    assert match.context.get("suggested_name") == "total_sum"


def test_rule_match_index_error():
    engine = PythonRuleEngine()
    parser = PythonErrorParser()
    code = "arr = [1, 2, 3]\nprint(arr[10])"
    stderr = "IndexError: list index out of range"
    parsed = parser.parse(code, stderr)
    match = engine.match(code, parsed)
    assert match.category == BugCategory.INDEX_OUT_OF_RANGE
    assert match.line_number == 2


def test_rule_match_type_error():
    engine = PythonRuleEngine()
    parser = PythonErrorParser()
    code = 'score = "100"\ntotal = score + 5'
    stderr = "TypeError: can only concatenate str (not 'int') to str"
    parsed = parser.parse(code, stderr)
    match = engine.match(code, parsed)
    assert match.category == BugCategory.TYPE_ERROR
    assert match.line_number == 2


def test_rule_match_timeout_loop():
    engine = PythonRuleEngine()
    parser = PythonErrorParser()
    code = "i = 0\nwhile i < 10:\n    print(i)"
    parsed = parser.parse(code, "timed out", timed_out=True)
    match = engine.match(code, parsed)
    assert match.category == BugCategory.LOOP_BOUNDARY
    assert match.line_number == 2
