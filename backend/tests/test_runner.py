import pytest
from app.runner.local_runner import LocalSubprocessRunner


def test_runner_python_success():
    runner = LocalSubprocessRunner(timeout_seconds=3.0)
    result = runner.run_python('print("Hello from SocraCode")')
    assert result.exit_code == 0
    assert result.timed_out is False
    assert "Hello from SocraCode" in result.stdout
    assert result.stderr == ""
    assert result.duration_ms > 0


def test_runner_python_syntax_error():
    runner = LocalSubprocessRunner(timeout_seconds=3.0)
    result = runner.run_python('for i in range(5)\n    print(i)')
    assert result.exit_code != 0
    assert result.timed_out is False
    assert "SyntaxError" in result.stderr


def test_runner_python_runtime_error():
    runner = LocalSubprocessRunner(timeout_seconds=3.0)
    result = runner.run_python('items = [1, 2, 3]\nprint(items[10])')
    assert result.exit_code != 0
    assert result.timed_out is False
    assert "IndexError" in result.stderr


def test_runner_python_stdin():
    runner = LocalSubprocessRunner(timeout_seconds=3.0)
    code = 'name = input()\nprint(f"Welcome, {name}!")'
    result = runner.run_python(code, stdin="SocraStudent")
    assert result.exit_code == 0
    assert "Welcome, SocraStudent!" in result.stdout


def test_runner_timeout_kill():
    # Strict short timeout to verify runaway loop is stopped
    runner = LocalSubprocessRunner(timeout_seconds=1.0)
    code = 'while True:\n    pass'
    result = runner.run_python(code, timeout_seconds=1.0)
    assert result.timed_out is True
    assert result.exit_code == -1
    assert "timed out" in result.stderr.lower()


def test_runner_output_truncation():
    # Runner caps maximum output bytes to prevent memory exhaustion
    runner = LocalSubprocessRunner(timeout_seconds=3.0, max_output_bytes=500)
    code = 'for i in range(1000): print(f"Line {i} flooding stdout with lots of extra text")'
    result = runner.run_python(code)
    assert result.exit_code == 0
    assert "truncated after limit" in result.stdout
    assert len(result.stdout) < 1000
