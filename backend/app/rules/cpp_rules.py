import re
import difflib
from typing import Any, Dict, List, Optional

from app.categories import BugCategory, get_category_metadata
from app.parser.python_parser import ParsedError
from app.rules.python_rules import RuleMatch


class CppRuleEngine:
    """Deterministic expert system matching C++ compiler and runtime errors to the 8 canonical bug categories."""

    def match(self, code: str, error: ParsedError) -> RuleMatch:
        if not error.has_error:
            meta = get_category_metadata(BugCategory.SYNTAX_ERROR)
            return RuleMatch(
                category=BugCategory.SYNTAX_ERROR,
                concept=meta.concept if meta else "syntax_rules",
                line_number=1,
                context={},
                confidence=1.0,
            )

        # 1. Timeout / Infinite Loop
        if error.error_type == "TimeoutError":
            meta = get_category_metadata(BugCategory.LOOP_BOUNDARY)
            loop_line = self._find_first_loop_line(code)
            return RuleMatch(
                category=BugCategory.LOOP_BOUNDARY,
                concept=meta.concept if meta else "iteration_and_termination",
                line_number=loop_line,
                context={"loop_type": "loop"},
                confidence=1.0,
            )

        # 2. Syntax Errors (expected ';', expected '}')
        if error.error_type == "SyntaxError" or "expected ';'" in error.message or "expected '}'" in error.message or "expected ')'" in error.message:
            meta = get_category_metadata(BugCategory.SYNTAX_ERROR)
            missing_token = ";" if "expected ';'" in error.message else ("}" if "expected '}'" in error.message else ")")
            return RuleMatch(
                category=BugCategory.SYNTAX_ERROR,
                concept=meta.concept if meta else "syntax_rules",
                line_number=error.line_number,
                context={"missing_token": missing_token, "line_text": error.code_line or ""},
                confidence=1.0,
            )

        # 3. Not declared in this scope -> Undefined name or typo
        if error.error_type == "NameError" or "not declared in this scope" in error.message.lower() or "was not declared" in error.message.lower():
            meta = get_category_metadata(BugCategory.UNDEFINED_NAME)
            symbol_match = re.search(r"['‘]([A-Za-z0-9_]+)['’]\s+(?:was\s+)?not\s+declared", error.message)
            unknown_name = symbol_match.group(1) if symbol_match else ""
            declared = self._find_declared_identifiers(code)
            suggestions = difflib.get_close_matches(unknown_name, declared, n=1, cutoff=0.6)
            suggested = suggestions[0] if suggestions else None

            return RuleMatch(
                category=BugCategory.UNDEFINED_NAME,
                concept=meta.concept if meta else "variables_and_scope",
                line_number=error.line_number,
                context={
                    "undefined_name": unknown_name,
                    "suggested_name": suggested,
                    "is_typo": suggested is not None,
                },
                confidence=1.0,
            )

        # 4. Type Incompatibility
        if error.error_type == "TypeError" or "cannot convert" in error.message.lower() or "no matching function for call" in error.message.lower():
            meta = get_category_metadata(BugCategory.TYPE_ERROR)
            return RuleMatch(
                category=BugCategory.TYPE_ERROR,
                concept=meta.concept if meta else "data_types",
                line_number=error.line_number,
                context={"message": error.message},
                confidence=1.0,
            )

        # 5. Segmentation fault or Out of Range
        if error.error_type in ("SegmentationFault", "IndexError") or "out_of_range" in error.message.lower():
            meta = get_category_metadata(BugCategory.INDEX_OUT_OF_RANGE)
            return RuleMatch(
                category=BugCategory.INDEX_OUT_OF_RANGE,
                concept=meta.concept if meta else "array_indexing",
                line_number=error.line_number,
                context={"message": error.message},
                confidence=1.0,
            )

        # 6. Missing return statement
        if error.error_type == "ReturnError" or "control reaches end of non-void function" in error.message.lower():
            meta = get_category_metadata(BugCategory.MISSING_RETURN)
            return RuleMatch(
                category=BugCategory.MISSING_RETURN,
                concept=meta.concept if meta else "functions_and_returns",
                line_number=error.line_number,
                context={},
                confidence=1.0,
            )

        # 7. Invalid operands -> Wrong operator
        if "invalid operands" in error.message.lower():
            meta = get_category_metadata(BugCategory.WRONG_OPERATOR)
            return RuleMatch(
                category=BugCategory.WRONG_OPERATOR,
                concept=meta.concept if meta else "operators_and_expressions",
                line_number=error.line_number,
                context={},
                confidence=1.0,
            )

        # Fallback to syntax_error
        meta = get_category_metadata(BugCategory.SYNTAX_ERROR)
        return RuleMatch(
            category=BugCategory.SYNTAX_ERROR,
            concept=meta.concept if meta else "syntax_rules",
            line_number=error.line_number,
            context={"message": error.message},
            confidence=0.7,
        )

    def _find_first_loop_line(self, code: str) -> int:
        lines = code.splitlines()
        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("while ") or stripped.startswith("while(") or stripped.startswith("for ") or stripped.startswith("for("):
                return idx
        return 1

    def _find_declared_identifiers(self, code: str) -> List[str]:
        # Extract variables from C++ declarations: int count = 0, std::string text, auto val
        pattern = re.compile(r"\b(?:int|double|float|long|bool|char|string|std::string|auto|[A-Za-z0-9_]+)\s+([A-Za-z_][A-Za-z0-9_]*)\s*(=|;|,|\()")
        return [m.group(1) for m in pattern.finditer(code)]
