import re
from typing import Optional
from app.parser.python_parser import ParsedError


class CppErrorParser:
    """Parses C++ GCC/Clang compiler diagnostics and runtime segmentation faults."""

    # Matches GCC/Clang diagnostic: solution.cpp:7:5: error: expected ';' before 'return'
    GCC_ERROR_REGEX = re.compile(
        r'([A-Za-z0-9_]+\.cpp):(\d+):(?:(\d+):)?\s*(?:fatal\s+)?error:\s*([^\n]+)', re.IGNORECASE
    )

    def parse(self, code: str, stderr: str, timed_out: bool = False) -> ParsedError:
        """Parse source code and stderr into a structured ParsedError."""
        clean_stderr = stderr.strip()

        # 1. Timeout check
        if timed_out or "timed out" in clean_stderr.lower():
            return ParsedError(
                has_error=True,
                error_type="TimeoutError",
                message="Execution timed out. Possible infinite loop or recursion without termination.",
                line_number=1,
                code_line=None,
            )

        if not clean_stderr:
            return ParsedError(has_error=False)

        code_lines = code.splitlines()

        # 2. Check for GCC / Clang compilation errors
        gcc_match = self.GCC_ERROR_REGEX.search(clean_stderr)
        if gcc_match:
            _, line_str, col_str, msg = gcc_match.groups()
            line_no = int(line_str)
            col_no = int(col_str) if col_str else None
            offending_line = (
                code_lines[line_no - 1] if 0 < line_no <= len(code_lines) else None
            )

            msg_lower = msg.lower()
            error_type = "CompilationError"
            if any(k in msg_lower for k in ["expected ';'", "expected '}'", "expected ')'", "expected primary-expression"]):
                error_type = "SyntaxError"
            elif "not declared in this scope" in msg_lower or "was not declared" in msg_lower:
                error_type = "NameError"
            elif "cannot convert" in msg_lower or "invalid operands" in msg_lower:
                error_type = "TypeError"
            elif "control reaches end of non-void function" in msg_lower:
                error_type = "ReturnError"

            return ParsedError(
                has_error=True,
                error_type=error_type,
                message=msg.strip(),
                line_number=line_no,
                column_number=col_no,
                code_line=offending_line,
            )

        # 3. Check for runtime faults (Segmentation fault, abort, out of range)
        stderr_lower = clean_stderr.lower()
        if "segmentation fault" in stderr_lower or "access violation" in stderr_lower or "sigsegv" in stderr_lower:
            return ParsedError(
                has_error=True,
                error_type="SegmentationFault",
                message="Memory access violation (Segmentation fault). Likely an invalid array index or null pointer access.",
                line_number=1,
                code_line=None,
            )

        if "out_of_range" in stderr_lower or "range_check" in stderr_lower:
            return ParsedError(
                has_error=True,
                error_type="IndexError",
                message="Container subscript out of bounds (std::out_of_range).",
                line_number=1,
                code_line=None,
            )

        return ParsedError(
            has_error=True,
            error_type="RuntimeError",
            message=clean_stderr.splitlines()[0] if clean_stderr else "Execution error",
            line_number=1,
            code_line=None,
        )
