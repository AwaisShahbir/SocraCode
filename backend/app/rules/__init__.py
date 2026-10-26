from app.rules.python_rules import PythonRuleEngine, RuleMatch
from app.rules.java_rules import JavaRuleEngine
from app.rules.cpp_rules import CppRuleEngine
from app.parser.python_parser import ParsedError

_python_rules = PythonRuleEngine()
_java_rules = JavaRuleEngine()
_cpp_rules = CppRuleEngine()


def match_python_rules(code: str, error: ParsedError) -> RuleMatch:
    return _python_rules.match(code, error)


def match_java_rules(code: str, error: ParsedError) -> RuleMatch:
    return _java_rules.match(code, error)


def match_cpp_rules(code: str, error: ParsedError) -> RuleMatch:
    return _cpp_rules.match(code, error)


def match_rules(language: str, code: str, error: ParsedError) -> RuleMatch:
    normalized = language.lower().strip()
    if normalized == "java":
        return match_java_rules(code, error)
    elif normalized in ("cpp", "c++"):
        return match_cpp_rules(code, error)
    else:
        return match_python_rules(code, error)


__all__ = [
    "PythonRuleEngine",
    "JavaRuleEngine",
    "CppRuleEngine",
    "RuleMatch",
    "match_python_rules",
    "match_java_rules",
    "match_cpp_rules",
    "match_rules",
]
