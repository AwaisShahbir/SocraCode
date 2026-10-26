import os
import sys
import time
import tempfile
import subprocess
from typing import Optional

from app.config import settings
from app.runner.base import CodeRunner, RunResult


class LocalSubprocessRunner(CodeRunner):
    """
    Executes student code in a constrained local subprocess.
    Isolates file execution inside a temporary directory and enforces timeouts.
    """

    def __init__(
        self,
        timeout_seconds: Optional[float] = None,
        max_output_bytes: Optional[int] = None,
    ):
        self.default_timeout = (
            timeout_seconds if timeout_seconds is not None else settings.runner_timeout_seconds
        )
        self.max_output_bytes = (
            max_output_bytes if max_output_bytes is not None else settings.runner_max_output_bytes
        )

    def run_python(
        self,
        code: str,
        stdin: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
    ) -> RunResult:
        timeout = timeout_seconds if timeout_seconds is not None else self.default_timeout
        start_time = time.perf_counter()

        with tempfile.TemporaryDirectory(prefix="socra_run_") as tmpdir:
            script_path = os.path.join(tmpdir, "solution.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code)

            # Use current python executable with isolated environment flags (-I, -u)
            cmd = [sys.executable, "-I", "-u", script_path]

            proc: Optional[subprocess.Popen[bytes]] = None
            try:
                proc = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=tmpdir,
                    env={
                        "PYTHONIOENCODING": "utf-8",
                        "PYTHONDONTWRITEBYTECODE": "1",
                        "PATH": os.environ.get("PATH", ""),
                    },
                )

                input_bytes = stdin.encode("utf-8") if stdin is not None else None
                stdout_bytes, stderr_bytes = proc.communicate(
                    input=input_bytes, timeout=timeout
                )

                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

                # Truncate if exceeds bounds
                if len(stdout_bytes) > self.max_output_bytes:
                    stdout_bytes = (
                        stdout_bytes[: self.max_output_bytes]
                        + b"\n... [Output truncated after limit]"
                    )
                if len(stderr_bytes) > self.max_output_bytes:
                    stderr_bytes = (
                        stderr_bytes[: self.max_output_bytes]
                        + b"\n... [Error output truncated after limit]"
                    )

                stdout_str = stdout_bytes.decode("utf-8", errors="replace")
                stderr_str = stderr_bytes.decode("utf-8", errors="replace")

                return RunResult(
                    stdout=stdout_str,
                    stderr=stderr_str,
                    exit_code=proc.returncode,
                    duration_ms=duration_ms,
                    timed_out=False,
                )

            except subprocess.TimeoutExpired:
                # Force kill process tree
                if proc is not None:
                    self._terminate_process(proc)
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                return RunResult(
                    stdout="",
                    stderr=f"Execution timed out after {timeout} seconds. Check for an infinite loop or heavy recursion.",
                    exit_code=-1,
                    duration_ms=duration_ms,
                    timed_out=True,
                )
            except Exception as exc:
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                return RunResult(
                    stdout="",
                    stderr=f"Internal runner error: {str(exc)}",
                    exit_code=-1,
                    duration_ms=duration_ms,
                    timed_out=False,
                )

    def _terminate_process(self, proc: subprocess.Popen) -> None:
        """Safely terminate process tree across platforms."""
        try:
            if sys.platform == "win32":
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )
            else:
                proc.kill()
            proc.communicate(timeout=1.0)
        except Exception:
            pass
