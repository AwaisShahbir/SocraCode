from app.parser.python_parser import ParsedError, PythonErrorParser

_default_python_parser = PythonErrorParser()

def parse_python_error(code: str, stderr: str, timed_out: bool = False) -> ParsedError:
    return _default_python_parser.parse(code, stderr, timed_out=timed_out)

__all__ = ["ParsedError", "PythonErrorParser", "parse_python_error"]
