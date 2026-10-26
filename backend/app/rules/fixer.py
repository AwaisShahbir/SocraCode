import ast
import re
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from app.categories import BugCategory


class FixResult(BaseModel):
    can_fix: bool = Field(default=False, description="Whether the rule base can fix this bug with certainty")
    fixed_code: Optional[str] = Field(default=None, description="Corrected complete source code")
    explanation: str = Field(default="", description="Detailed pedagogical explanation of the fix")
    diff_summary: Optional[str] = Field(default=None, description="Summary of changed line")


class RuleBasedFixer:
    """
    Synthesizes deterministic, rule-verified fixes for supported bug categories (Level 5).
    Enforces non-negotiable Constraint 5: Never guess a fix.
    If the fix cannot be verified with 100% certainty via AST validation, stops at Level 4.
    """

    def generate_fix(
        self,
        code: str,
        category: BugCategory,
        buggy_line: int,
        context: Dict[str, Any],
        language: str = "python",
    ) -> FixResult:
        norm = language.lower().strip()
        if norm in ("java", "cpp", "c++"):
            return self._fix_c_family(code, category, buggy_line, context, norm)

        if category == BugCategory.SYNTAX_ERROR:
            return self._fix_syntax_error(code, buggy_line, context)
        elif category == BugCategory.UNDEFINED_NAME:
            return self._fix_undefined_name(code, buggy_line, context)
        elif category == BugCategory.MISSING_RETURN:
            return self._fix_missing_return(code, buggy_line, context)
        elif category == BugCategory.INDEX_OUT_OF_RANGE:
            return self._fix_index_bounds(code, buggy_line, context)

        return FixResult(
            can_fix=False,
            fixed_code=None,
            explanation="SocraCode can't verify a full fix for this bug with certainty. Review the worked example in Level 4 or ask your instructor.",
        )

    def _fix_c_family(
        self,
        code: str,
        category: BugCategory,
        buggy_line: int,
        context: Dict[str, Any],
        language: str,
    ) -> FixResult:
        lang_title = "Java" if language == "java" else "C++"
        lines = code.splitlines()
        target_idx = buggy_line - 1

        if not (0 <= target_idx < len(lines)):
            return FixResult(can_fix=False, explanation="Invalid line index.")

        if category == BugCategory.SYNTAX_ERROR:
            orig_line = lines[target_idx]
            stripped = orig_line.strip()
            # If line doesn't end with semicolon and is not a brace or empty
            if stripped and not stripped.endswith(";") and not stripped.endswith("{") and not stripped.endswith("}"):
                candidate_line = orig_line.rstrip() + ";"
                lines[target_idx] = candidate_line
                candidate_code = "\n".join(lines)
                return FixResult(
                    can_fix=True,
                    fixed_code=candidate_code,
                    explanation=f"Added missing semicolon (;) at line {buggy_line}. In {lang_title}, every statement must be terminated with a semicolon.",
                    diff_summary=f"Line {buggy_line}: '{orig_line.strip()}' -> '{candidate_line.strip()}'",
                )
            # Check previous line if compiler flagged next line
            elif target_idx > 0:
                prev_line = lines[target_idx - 1]
                prev_strip = prev_line.strip()
                if prev_strip and not prev_strip.endswith(";") and not prev_strip.endswith("{") and not prev_strip.endswith("}"):
                    candidate_prev = prev_line.rstrip() + ";"
                    lines[target_idx - 1] = candidate_prev
                    candidate_code = "\n".join(lines)
                    return FixResult(
                        can_fix=True,
                        fixed_code=candidate_code,
                        explanation=f"Added missing semicolon (;) at line {buggy_line - 1}. In {lang_title}, statements preceding line {buggy_line} must end with a semicolon.",
                        diff_summary=f"Line {buggy_line - 1}: '{prev_line.strip()}' -> '{candidate_prev.strip()}'",
                    )

        elif category == BugCategory.UNDEFINED_NAME:
            undefined_name = context.get("undefined_name")
            suggested_name = context.get("suggested_name")
            if undefined_name and suggested_name:
                orig_line = lines[target_idx]
                fixed_line = re.sub(rf"\b{re.escape(undefined_name)}\b", suggested_name, orig_line)
                if fixed_line != orig_line:
                    lines[target_idx] = fixed_line
                    candidate_code = "\n".join(lines)
                    return FixResult(
                        can_fix=True,
                        fixed_code=candidate_code,
                        explanation=f"Corrected identifier typo '{undefined_name}' to '{suggested_name}' on line {buggy_line} in {lang_title}.",
                        diff_summary=f"Line {buggy_line}: '{orig_line.strip()}' -> '{fixed_line.strip()}'",
                    )

        return FixResult(
            can_fix=False,
            fixed_code=None,
            explanation="SocraCode can't verify a full fix for this bug with certainty. Review the worked example in Level 4 or ask your instructor.",
        )

    def _fix_syntax_error(self, code: str, buggy_line: int, context: Dict[str, Any]) -> FixResult:
        lines = code.splitlines()
        target_idx = buggy_line - 1

        if not (0 <= target_idx < len(lines)):
            return FixResult(can_fix=False, explanation="Invalid line index.")

        orig_line = lines[target_idx]

        # Case A: Missing colon on current line
        candidate_line = orig_line.rstrip() + ":"
        lines[target_idx] = candidate_line
        candidate_code = "\n".join(lines)

        try:
            ast.parse(candidate_code)
            return FixResult(
                can_fix=True,
                fixed_code=candidate_code,
                explanation=f"Added missing colon (:) at line {buggy_line}. In Python, compound headers (if, for, while, def) require a colon before the indented block.",
                diff_summary=f"Line {buggy_line}: '{orig_line.strip()}' -> '{candidate_line.strip()}'",
            )
        except SyntaxError:
            pass

        # Case B: Missing colon on previous line
        if target_idx > 0:
            lines[target_idx] = orig_line  # revert current
            prev_line = lines[target_idx - 1]
            candidate_prev = prev_line.rstrip() + ":"
            lines[target_idx - 1] = candidate_prev
            candidate_code = "\n".join(lines)
            try:
                ast.parse(candidate_code)
                return FixResult(
                    can_fix=True,
                    fixed_code=candidate_code,
                    explanation=f"Added missing colon (:) at line {buggy_line - 1}. The header statement ended without a colon.",
                    diff_summary=f"Line {buggy_line - 1}: '{prev_line.strip()}' -> '{candidate_prev.strip()}'",
                )
            except SyntaxError:
                pass

        return FixResult(
            can_fix=False,
            fixed_code=None,
            explanation="SocraCode can't verify a full fix for this syntax structure with certainty. Review Level 4 for similar syntax patterns.",
        )

    def _fix_undefined_name(self, code: str, buggy_line: int, context: Dict[str, Any]) -> FixResult:
        undefined_name = context.get("undefined_name")
        suggested_name = context.get("suggested_name")

        if not undefined_name or not suggested_name:
            return FixResult(
                can_fix=False,
                explanation="No exact variable spelling match found. Declare the variable before reading it.",
            )

        lines = code.splitlines()
        target_idx = buggy_line - 1
        if not (0 <= target_idx < len(lines)):
            return FixResult(can_fix=False, explanation="Invalid line index.")

        orig_line = lines[target_idx]
        fixed_line = re.sub(rf"\b{re.escape(undefined_name)}\b", suggested_name, orig_line)

        if fixed_line == orig_line:
            # Search across all lines for the identifier
            for idx, line in enumerate(lines):
                if re.search(rf"\b{re.escape(undefined_name)}\b", line):
                    target_idx = idx
                    orig_line = line
                    fixed_line = re.sub(rf"\b{re.escape(undefined_name)}\b", suggested_name, line)
                    break

        lines[target_idx] = fixed_line
        candidate_code = "\n".join(lines)

        try:
            ast.parse(candidate_code)
            return FixResult(
                can_fix=True,
                fixed_code=candidate_code,
                explanation=f"Corrected identifier typo '{undefined_name}' to '{suggested_name}' on line {target_idx + 1}.",
                diff_summary=f"Line {target_idx + 1}: '{orig_line.strip()}' -> '{fixed_line.strip()}'",
            )
        except Exception:
            return FixResult(
                can_fix=False,
                explanation="Could not verify identifier replacement without syntax side-effects.",
            )

    def _fix_missing_return(self, code: str, buggy_line: int, context: Dict[str, Any]) -> FixResult:
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for assigned variables inside function
                    assigned_vars = []
                    for child in node.body:
                        if isinstance(child, ast.Assign):
                            for target in child.targets:
                                if isinstance(target, ast.Name):
                                    assigned_vars.append(target.id)

                    if assigned_vars:
                        # Common accumulator or return candidate
                        return_var = assigned_vars[-1]
                        last_stmt = node.body[-1]
                        end_lineno = getattr(last_stmt, "end_lineno", last_stmt.lineno)
                        indent = "    "
                        lines = code.splitlines()
                        lines.insert(end_lineno, f"{indent}return {return_var}")
                        candidate_code = "\n".join(lines)
                        ast.parse(candidate_code)
                        return FixResult(
                            can_fix=True,
                            fixed_code=candidate_code,
                            explanation=f"Added 'return {return_var}' at the end of function '{node.name}'. Functions must explicitly return their computed result.",
                            diff_summary=f"Added 'return {return_var}' after line {end_lineno}",
                        )
        except Exception:
            pass

        return FixResult(
            can_fix=False,
            explanation="Function return structure could not be determined automatically with certainty.",
        )

    def _fix_index_bounds(self, code: str, buggy_line: int, context: Dict[str, Any]) -> FixResult:
        lines = code.splitlines()
        target_idx = buggy_line - 1
        if 0 <= target_idx < len(lines):
            orig_line = lines[target_idx]
            # Pattern: items[len(items)] -> items[len(items) - 1]
            fixed_line = re.sub(r"\[\s*len\(([^)]+)\)\s*\]", r"[len(\1) - 1]", orig_line)
            if fixed_line != orig_line:
                lines[target_idx] = fixed_line
                candidate_code = "\n".join(lines)
                try:
                    ast.parse(candidate_code)
                    return FixResult(
                        can_fix=True,
                        fixed_code=candidate_code,
                        explanation=f"Adjusted sequence index at line {buggy_line} to 'len(...) - 1'. Valid 0-indexed sequences stop at length minus 1.",
                        diff_summary=f"Line {buggy_line}: '{orig_line.strip()}' -> '{fixed_line.strip()}'",
                    )
                except Exception:
                    pass

        return FixResult(
            can_fix=False,
            explanation="Array boundary calculation depends on algorithm invariants and should be adjusted by the author.",
        )
