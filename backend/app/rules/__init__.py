from app.rules.python_rules import PythonRuleEngine, RuleMatch
from app.parser.python_parser import ParsedError

_default_python_rules = PythonRuleEngine()

def match_python_rules(code: str, error: ParsedError) -> RuleMatch:
    return _default_python_rules.match(code, error)

__all__ = ["PythonRuleEngine", "RuleMatch", "match_python_rules"]
