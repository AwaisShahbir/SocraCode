import ast
import re
from typing import Optional
from pydantic import BaseModel, Field


class ParsedError(BaseModel):
    """Structured representation of a compiler or runtime failure."""

    has_error: bool = Field(default=False, description="Whether an error was detected")
    error_type: str = Field(default="", description="Exception or error type name (e.g. NameError, SyntaxError)")
    message: str = Field(default="", description="Error description or message")
    line_number: int = Field(default=1, description="1-indexed line number where failure occurred")
    column_number: Optional[int] = Field(default=None, description="Column offset if available")
    code_line: Optional[str] = Field(default=None, description="Source code text at buggy line")


class PythonErrorParser:
    """Parses Python compiler and interpreter failures into structured diagnostic records."""

    # Matches traceback frame: File "<filename>", line 12, in <module>
    FRAME_REGEX = re.compile(r'File\s+["\']([^"\']+)["\'],\s+line\s+(\d+)(?:,\s+in\s+([^\n]+))?')
    # Matches final exception line: NameError: name 'x' is not defined
    EXCEPTION_REGEX = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*(?:Error|Exception|Warning|Interrupt)):\s*(.*)$", re.MULTILINE)

    def parse(self, code: str, stderr: str, timed_out: bool = False) -> ParsedError:
        """Parse source code and stderr into a structured ParsedError."""
        # 1. Check for execution timeout
        if timed_out or "timed out" in stderr.lower():
            return ParsedError(
                has_error=True,
                error_type="TimeoutError",
                message="Execution timed out. Possible infinite loop or excessive recursion.",
                line_number=1,
                code_line=None,
            )

        # 2. Check for syntax error via ast.parse first for high-precision line/column reporting
        try:
            ast.parse(code)
        except SyntaxError as syn_err:
            line_no = syn_err.lineno or 1
            code_lines = code.splitlines()
            offending_line = code_lines[line_no - 1] if 0 < line_no <= len(code_lines) else None
            return ParsedError(
                has_error=True,
                error_type=syn_err.__class__.__name__,
                message=syn_err.msg or "Invalid syntax",
                line_number=line_no,
                column_number=syn_err.offset,
                code_line=offending_line,
            )

        # If there is no stderr and ast parsed cleanly, no error exists
        clean_stderr = stderr.strip()
        if not clean_stderr:
            return ParsedError(has_error=False)

        # 3. Parse Runtime Traceback from stderr
        exception_match = self.EXCEPTION_REGEX.search(clean_stderr)
        error_type = exception_match.group(1) if exception_match else "RuntimeError"
        message = exception_match.group(2).strip() if exception_match else clean_stderr.splitlines()[-1]

        # Extract frames to find the user's line number (typically the last frame in user code)
        frame_matches = list(self.FRAME_REGEX.finditer(clean_stderr))
        line_number = None
        if frame_matches:
            # Pick the deepest user frame
            last_frame = frame_matches[-1]
            try:
                line_number = int(last_frame.group(2))
            except (ValueError, TypeError):
                line_number = None

        code_lines = code.splitlines()

        # Heuristic fallback if frame line number wasn't found
        if line_number is None or line_number > len(code_lines):
            line_number = self._infer_buggy_line(code_lines, error_type, message)

        code_line = code_lines[line_number - 1] if 0 < line_number <= len(code_lines) else None

        return ParsedError(
            has_error=True,
            error_type=error_type,
            message=message,
            line_number=line_number,
            column_number=None,
            code_line=code_line,
        )

    def _infer_buggy_line(self, lines: list, error_type: str, message: str) -> int:
        """Infer probable line number from error message when traceback frames are absent."""
        if not lines:
            return 1

        # Check for undefined variable name
        if error_type in ("NameError", "UnboundLocalError"):
            name_match = re.search(r"name\s+['\"]([A-Za-z0-9_]+)['\"]", message)
            if name_match:
                target_name = name_match.group(1)
                pattern = re.compile(rf"\b{re.escape(target_name)}\b")
                # Search from bottom to top for where the undefined variable is evaluated
                for i in range(len(lines) - 1, -1, -1):
                    if pattern.search(lines[i]):
                        return i + 1

        # Check for indexing
        if error_type == "IndexError":
            for i in range(len(lines) - 1, -1, -1):
                if "[" in lines[i] and "]" in lines[i]:
                    return i + 1

        # Check for type errors (e.g. string concatenation or arithmetic)
        if error_type == "TypeError":
            for i in range(len(lines) - 1, -1, -1):
                line = lines[i]
                if any(op in line for op in (" + ", " - ", " * ", " / ", " % ")):
                    return i + 1

        return 1

