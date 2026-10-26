import os
import re
import sys
import time
import shutil
import tempfile
import subprocess
from typing import Optional, Tuple

from app.config import settings
from app.runner.base import CodeRunner, RunResult


class LocalSubprocessRunner(CodeRunner):
    """
    Executes student code in a constrained local subprocess.
    Supports Python, Java, and C++ with compiler diagnostic capture,
    sandboxed temp directories, strict 5-second timeouts, and output limits.
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

    @staticmethod
    def _find_java_binaries() -> Tuple[Optional[str], Optional[str]]:
        """Locates javac and java executables from PATH or known JDK paths."""
        javac = shutil.which("javac")
        java = shutil.which("java")

        if not javac or not java:
            candidates = [
                r"C:\Program Files\Android\Android Studio\jbr\bin",
                os.environ.get("JAVA_HOME", "") + r"\bin",
                r"C:\Program Files\Java\jdk-21\bin",
                r"C:\Program Files\Eclipse Adoptium\jdk-21\bin",
            ]
            for candidate in candidates:
                if candidate and os.path.exists(candidate):
                    if not javac and os.path.exists(os.path.join(candidate, "javac.exe")):
                        javac = os.path.join(candidate, "javac.exe")
                    if not java and os.path.exists(os.path.join(candidate, "java.exe")):
                        java = os.path.join(candidate, "java.exe")
        return javac, java

    @staticmethod
    def _find_cpp_compiler() -> Optional[str]:
        """Locates g++ or clang++ compiler."""
        gpp = shutil.which("g++")
        if gpp:
            return gpp
        clangpp = shutil.which("clang++")
        if clangpp:
            return clangpp

        candidates = [
            r"C:\Program Files\WinLibs\bin\g++.exe",
            r"C:\WinLibs\bin\g++.exe",
            r"C:\msys64\ucrt64\bin\g++.exe",
            r"C:\msys64\mingw64\bin\g++.exe",
            r"C:\w64devkit\bin\g++.exe",
            r"C:\Program Files\LLVM\bin\clang++.exe",
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return None

    def run_python(
        self,
        code: str,
        stdin: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
    ) -> RunResult:
        timeout = timeout_seconds if timeout_seconds is not None else self.default_timeout
        start_time = time.perf_counter()

        with tempfile.TemporaryDirectory(prefix="socra_run_py_") as tmpdir:
            script_path = os.path.join(tmpdir, "solution.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code)

            cmd = [sys.executable, "-I", "-u", script_path]
            return self._execute_process(cmd, tmpdir, stdin, timeout, start_time)

    def run_java(
        self,
        code: str,
        stdin: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
    ) -> RunResult:
        timeout = timeout_seconds if timeout_seconds is not None else self.default_timeout
        start_time = time.perf_counter()

        javac, java = self._find_java_binaries()
        if not javac or not java:
            return RunResult(
                stdout="",
                stderr="Java compiler (javac) or runtime (java) not found on host system.",
                exit_code=-1,
                duration_ms=0.0,
                timed_out=False,
            )

        # Detect class name from code
        class_match = re.search(r"public\s+class\s+([A-Za-z0-9_]+)", code)
        if not class_match:
            class_match = re.search(r"class\s+([A-Za-z0-9_]+)", code)
        class_name = class_match.group(1) if class_match else "Solution"

        with tempfile.TemporaryDirectory(prefix="socra_run_java_") as tmpdir:
            src_path = os.path.join(tmpdir, f"{class_name}.java")
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(code)

            # Step 1: Compile with javac
            compile_cmd = [javac, f"{class_name}.java"]
            try:
                compile_proc = subprocess.run(
                    compile_cmd,
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                if compile_proc.returncode != 0:
                    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                    err_msg = compile_proc.stderr or compile_proc.stdout or "Compilation error"
                    return RunResult(
                        stdout="",
                        stderr=err_msg.strip(),
                        exit_code=compile_proc.returncode,
                        duration_ms=duration_ms,
                        timed_out=False,
                    )
            except subprocess.TimeoutExpired:
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                return RunResult(
                    stdout="",
                    stderr=f"Java compilation timed out after {timeout} seconds.",
                    exit_code=-1,
                    duration_ms=duration_ms,
                    timed_out=True,
                )

            # Step 2: Execute with java (isolated heap limit)
            run_cmd = [java, "-Xmx256m", "-Xms16m", class_name]
            return self._execute_process(run_cmd, tmpdir, stdin, timeout, start_time)

    def run_cpp(
        self,
        code: str,
        stdin: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
    ) -> RunResult:
        timeout = timeout_seconds if timeout_seconds is not None else self.default_timeout
        start_time = time.perf_counter()

        compiler = self._find_cpp_compiler()
        if not compiler:
            return RunResult(
                stdout="",
                stderr="C++ compiler (g++ / clang++) not found on host system.",
                exit_code=-1,
                duration_ms=0.0,
                timed_out=False,
            )

        with tempfile.TemporaryDirectory(prefix="socra_run_cpp_") as tmpdir:
            src_path = os.path.join(tmpdir, "solution.cpp")
            exe_path = os.path.join(tmpdir, "solution.exe" if sys.platform == "win32" else "solution")
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(code)

            # Step 1: Compile with g++
            compile_cmd = [compiler, "-O2", "-std=c++17", "-Wall", "solution.cpp", "-o", exe_path]
            try:
                compile_proc = subprocess.run(
                    compile_cmd,
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                if compile_proc.returncode != 0:
                    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                    err_msg = compile_proc.stderr or compile_proc.stdout or "Compilation error"
                    return RunResult(
                        stdout="",
                        stderr=err_msg.strip(),
                        exit_code=compile_proc.returncode,
                        duration_ms=duration_ms,
                        timed_out=False,
                    )
            except subprocess.TimeoutExpired:
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                return RunResult(
                    stdout="",
                    stderr=f"C++ compilation timed out after {timeout} seconds.",
                    exit_code=-1,
                    duration_ms=duration_ms,
                    timed_out=True,
                )

            # Step 2: Execute compiled binary
            run_cmd = [exe_path]
            return self._execute_process(run_cmd, tmpdir, stdin, timeout, start_time)

    def _execute_process(
        self,
        cmd: list[str],
        cwd: str,
        stdin: Optional[str],
        timeout: float,
        start_time: float,
    ) -> RunResult:
        proc: Optional[subprocess.Popen[bytes]] = None
        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
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
