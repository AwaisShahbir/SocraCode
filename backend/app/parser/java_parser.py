import re
from typing import Optional
from app.parser.python_parser import ParsedError


class JavaErrorParser:
    """Parses Java compiler (javac) errors and JVM runtime exception stack traces."""

    # Matches javac error line: Solution.java:5: error: ';' expected
    JAVAC_ERROR_REGEX = re.compile(
        r'([A-Za-z0-9_]+\.java):(\d+):\s*(?:error:\s*)?([^\n]+)', re.IGNORECASE
    )

    # Matches Java exception header: Exception in thread "main" java.lang.ArrayIndexOutOfBoundsException: Index 5 out of bounds for length 5
    EXCEPTION_HEADER_REGEX = re.compile(
        r'(?:Exception in thread "[^"]*"\s+)?([A-Za-z0-9_$.]+(?:Exception|Error))(?::\s*([^\n]+))?'
    )

    # Matches stack frame: at Solution.main(Solution.java:8)
    STACK_FRAME_REGEX = re.compile(
        r'at\s+[A-Za-z0-9_$.]+\.[A-Za-z0-9_<>]+\(([A-Za-z0-9_]+\.java):(\d+)\)'
    )

    def parse(self, code: str, stderr: str, timed_out: bool = False) -> ParsedError:
        """Parse source code and stderr into a structured ParsedError."""
        clean_stderr = stderr.strip()

        # 1. Timeout check
        if timed_out or "timed out" in clean_stderr.lower():
            return ParsedError(
                has_error=True,
                error_type="TimeoutError",
                message="Execution timed out. Possible infinite loop or excessive recursion.",
                line_number=1,
                code_line=None,
            )

        if not clean_stderr:
            return ParsedError(has_error=False)

        code_lines = code.splitlines()

        # 2. Check for javac compilation errors
        javac_match = self.JAVAC_ERROR_REGEX.search(clean_stderr)
        if javac_match:
            _, line_str, msg = javac_match.groups()
            line_no = int(line_str)
            offending_line = (
                code_lines[line_no - 1] if 0 < line_no <= len(code_lines) else None
            )

            # Map compiler message to clean error type name
            error_type = "CompilationError"
            msg_lower = msg.lower()
            if any(k in msg_lower for k in [";' expected", "; expected", ")' expected", ") expected", "}' expected", "} expected", "illegal start", "not a statement"]):
                error_type = "SyntaxError"
            elif "cannot find symbol" in msg_lower:
                error_type = "NameError"
            elif "incompatible types" in msg_lower or "possible loss of precision" in msg_lower:
                error_type = "TypeError"
            elif "missing return statement" in msg_lower:
                error_type = "ReturnError"

            return ParsedError(
                has_error=True,
                error_type=error_type,
                message=msg.strip(),
                line_number=line_no,
                code_line=offending_line,
            )

        # 3. Check for JVM runtime exceptions
        exc_match = self.EXCEPTION_HEADER_REGEX.search(clean_stderr)
        if exc_match:
            full_class, exc_msg = exc_match.groups()
            simple_name = full_class.split(".")[-1]
            desc = exc_msg.strip() if exc_msg else simple_name

            # Look for user frame
            line_no = 1
            frame_match = self.STACK_FRAME_REGEX.search(clean_stderr)
            if frame_match:
                line_no = int(frame_match.group(2))

            offending_line = (
                code_lines[line_no - 1] if 0 < line_no <= len(code_lines) else None
            )

            return ParsedError(
                has_error=True,
                error_type=simple_name,
                message=desc,
                line_number=line_no,
                code_line=offending_line,
            )

        # 4. Fallback for unclassified stderr
        return ParsedError(
            has_error=True,
            error_type="RuntimeError",
            message=clean_stderr.splitlines()[0] if clean_stderr else "Execution error",
            line_number=1,
            code_line=None,
        )
