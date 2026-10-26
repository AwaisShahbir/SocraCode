from app.parser.python_parser import ParsedError, PythonErrorParser
from app.parser.java_parser import JavaErrorParser
from app.parser.cpp_parser import CppErrorParser

_default_python_parser = PythonErrorParser()
_default_java_parser = JavaErrorParser()
_default_cpp_parser = CppErrorParser()

def parse_python_error(code: str, stderr: str, timed_out: bool = False) -> ParsedError:
    return _default_python_parser.parse(code, stderr, timed_out=timed_out)

def parse_java_error(code: str, stderr: str, timed_out: bool = False) -> ParsedError:
    return _default_java_parser.parse(code, stderr, timed_out=timed_out)

def parse_cpp_error(code: str, stderr: str, timed_out: bool = False) -> ParsedError:
    return _default_cpp_parser.parse(code, stderr, timed_out=timed_out)


def parse_error(language: str, code: str, stderr: str, timed_out: bool = False) -> ParsedError:
    """Unified error parsing dispatch for Python, Java, and C++."""
    norm = language.lower().strip()
    if norm == "java":
        return parse_java_error(code, stderr, timed_out=timed_out)
    elif norm in ("cpp", "c++"):
        return parse_cpp_error(code, stderr, timed_out=timed_out)
    else:
        return parse_python_error(code, stderr, timed_out=timed_out)


__all__ = [
    "ParsedError",
    "PythonErrorParser",
    "JavaErrorParser",
    "CppErrorParser",
    "parse_python_error",
    "parse_java_error",
    "parse_cpp_error",
    "parse_error",
]
