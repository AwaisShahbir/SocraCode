import pytest
from app.parser.python_parser import PythonErrorParser


def test_parse_syntax_error():
    parser = PythonErrorParser()
    code = "def calculate()\n    return 42"
    result = parser.parse(code, "")
    assert result.has_error is True
    assert result.error_type == "SyntaxError"
    assert result.line_number == 1
    assert "def calculate()" in (result.code_line or "")


def test_parse_runtime_traceback_name_error():
    parser = PythonErrorParser()
    code = "x = 10\nprint(y)"
    stderr = """Traceback (most recent call last):
  File "solution.py", line 2, in <module>
    print(y)
NameError: name 'y' is not defined"""
    result = parser.parse(code, stderr)
    assert result.has_error is True
    assert result.error_type == "NameError"
    assert result.line_number == 2
    assert "name 'y' is not defined" in result.message


def test_parse_index_error():
    parser = PythonErrorParser()
    code = "items = [1, 2]\nprint(items[5])"
    stderr = """Traceback (most recent call last):
  File "solution.py", line 2, in <module>
    print(items[5])
IndexError: list index out of range"""
    result = parser.parse(code, stderr)
    assert result.has_error is True
    assert result.error_type == "IndexError"
    assert result.line_number == 2


def test_parse_timeout_error():
    parser = PythonErrorParser()
    code = "while True: pass"
    result = parser.parse(code, "Execution timed out after 5.0 seconds.", timed_out=True)
    assert result.has_error is True
    assert result.error_type == "TimeoutError"
