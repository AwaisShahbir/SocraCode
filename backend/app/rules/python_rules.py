import ast
import re
import difflib
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.categories import BugCategory, get_category_metadata
from app.parser.python_parser import ParsedError


class RuleMatch(BaseModel):
    """Result of expert-system rule analysis."""

    category: BugCategory = Field(..., description="Identified bug category")
    concept: str = Field(..., description="Pedagogical concept key")
    line_number: int = Field(default=1, description="Buggy line number")
    context: Dict[str, Any] = Field(default_factory=dict, description="Extracted context for hint hydration")
    confidence: float = Field(default=1.0, description="Rule certainty (0.0 to 1.0)")


class PythonRuleEngine:
    """Deterministic expert system matching Python errors to bug categories and concepts."""

    def match(self, code: str, error: ParsedError) -> RuleMatch:
        """Analyze code and parsed error to identify category, line, and pedagogical context."""
        if not error.has_error:
            meta = get_category_metadata(BugCategory.SYNTAX_ERROR)
            return RuleMatch(
                category=BugCategory.SYNTAX_ERROR,
                concept=meta.concept if meta else "syntax_rules",
                line_number=1,
                context={},
                confidence=1.0,
            )

        # 1. Timeout -> Loop boundary / infinite loop
        if error.error_type == "TimeoutError":
            meta = get_category_metadata(BugCategory.LOOP_BOUNDARY)
            # Find the first while or for loop in code
            loop_line = self._find_first_loop_line(code)
            return RuleMatch(
                category=BugCategory.LOOP_BOUNDARY,
                concept=meta.concept if meta else "iteration_and_termination",
                line_number=loop_line,
                context={"loop_type": "loop"},
                confidence=1.0,
            )

        # 2. SyntaxError / IndentationError
        if error.error_type in ("SyntaxError", "IndentationError"):
            return self._match_syntax_error(code, error)

        # 3. NameError / UnboundLocalError -> Undefined name or typo
        if error.error_type in ("NameError", "UnboundLocalError"):
            return self._match_name_error(code, error)

        # 4. IndexError -> Index out of range
        if error.error_type == "IndexError":
            meta = get_category_metadata(BugCategory.INDEX_OUT_OF_RANGE)
            return RuleMatch(
                category=BugCategory.INDEX_OUT_OF_RANGE,
                concept=meta.concept if meta else "indexing_and_bounds",
                line_number=error.line_number,
                context={"error_msg": error.message},
                confidence=1.0,
            )

        # 5. TypeError -> Type incompatibility or NoneType return issue
        if error.error_type == "TypeError":
            if "'nonetype'" in error.message.lower() and self._has_fruitless_function(code):
                meta = get_category_metadata(BugCategory.MISSING_RETURN)
                return RuleMatch(
                    category=BugCategory.MISSING_RETURN,
                    concept=meta.concept if meta else "functions_and_returns",
                    line_number=error.line_number,
                    context={"error_msg": error.message},
                    confidence=0.95,
                )
            meta = get_category_metadata(BugCategory.TYPE_ERROR)
            return RuleMatch(
                category=BugCategory.TYPE_ERROR,
                concept=meta.concept if meta else "data_types",
                line_number=error.line_number,
                context={"error_msg": error.message},
                confidence=1.0,
            )

        # 6. ZeroDivisionError -> Loop boundary / calculation condition
        if error.error_type == "ZeroDivisionError":
            meta = get_category_metadata(BugCategory.WRONG_OPERATOR)
            return RuleMatch(
                category=BugCategory.WRONG_OPERATOR,
                concept=meta.concept if meta else "conditional_logic",
                line_number=error.line_number,
                context={"error_msg": error.message},
                confidence=0.9,
            )

        # 7. Static Check for Missing Return if runtime error or logic issue
        if self._has_fruitless_function(code):
            meta = get_category_metadata(BugCategory.MISSING_RETURN)
            return RuleMatch(
                category=BugCategory.MISSING_RETURN,
                concept=meta.concept if meta else "functions_and_returns",
                line_number=error.line_number,
                context={"error_msg": error.message},
                confidence=0.85,
            )

        # Fallback for unexpected exceptions
        meta = get_category_metadata(BugCategory.SYNTAX_ERROR)
        return RuleMatch(
            category=BugCategory.SYNTAX_ERROR,
            concept=meta.concept if meta else "syntax_rules",
            line_number=error.line_number,
            context={"error_msg": error.message},
            confidence=0.6,
        )

    def _match_syntax_error(self, code: str, error: ParsedError) -> RuleMatch:
        meta = get_category_metadata(BugCategory.SYNTAX_ERROR)
        line_no = error.line_number
        lines = code.splitlines()
        target_line = lines[line_no - 1] if 0 < line_no <= len(lines) else ""

        # Check if previous line was missing a colon
        if line_no > 1 and not lines[line_no - 2].rstrip().endswith(":"):
            prev_line = lines[line_no - 2].strip()
            if any(prev_line.startswith(kw) for kw in ("def ", "if ", "elif ", "else", "for ", "while ", "class ")):
                line_no = line_no - 1
                target_line = lines[line_no - 1]

        missing_colon = any(
            target_line.strip().startswith(kw)
            for kw in ("def ", "if ", "elif ", "else", "for ", "while ", "class ")
        ) and not target_line.rstrip().endswith(":")

        return RuleMatch(
            category=BugCategory.SYNTAX_ERROR,
            concept=meta.concept if meta else "syntax_rules",
            line_number=line_no,
            context={
                "code_line": target_line,
                "missing_colon": missing_colon,
                "error_msg": error.message,
            },
            confidence=1.0,
        )

    def _match_name_error(self, code: str, error: ParsedError) -> RuleMatch:
        meta = get_category_metadata(BugCategory.UNDEFINED_NAME)
        # Extract name from: name 'xyz' is not defined
        match = re.search(r"name\s+['\"]([A-Za-z0-9_]+)['\"]", error.message)
        undefined_name = match.group(1) if match else ""

        # Find existing identifiers in code to detect spelling typos
        all_identifiers = self._extract_identifiers(code)
        close_matches = [
            cand for cand in all_identifiers
            if cand != undefined_name and len(cand) >= 2
        ]
        best_match = None
        if undefined_name and close_matches:
            matches = difflib.get_close_matches(undefined_name, close_matches, n=1, cutoff=0.6)
            if matches:
                best_match = matches[0]

        return RuleMatch(
            category=BugCategory.UNDEFINED_NAME,
            concept=meta.concept if meta else "variable_scope_and_declaration",
            line_number=error.line_number,
            context={
                "undefined_name": undefined_name,
                "suggested_name": best_match,
                "is_typo": bool(best_match),
            },
            confidence=1.0,
        )

    def _find_first_loop_line(self, code: str) -> int:
        lines = code.splitlines()
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("while ") or stripped.startswith("for "):
                return i + 1
        return 1

    def _extract_identifiers(self, code: str) -> List[str]:
        try:
            tree = ast.parse(code)
            names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    names.add(node.id)
                elif isinstance(node, ast.FunctionDef):
                    names.add(node.name)
            return list(names)
        except Exception:
            return re.findall(r"[A-Za-z_][A-Za-z0-9_]*", code)

    def _has_fruitless_function(self, code: str) -> bool:
        """Detect functions that calculate a result but omit the return statement."""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if body has calculations but no Return node
                    returns = [n for n in ast.walk(node) if isinstance(n, ast.Return)]
                    if not returns and len(node.body) > 1:
                        return True
            return False
        except Exception:
            return False
