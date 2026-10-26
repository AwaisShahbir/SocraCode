from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel, Field


class RunResult(BaseModel):
    """Result of running student code."""

    stdout: str = Field(default="", description="Captured standard output")
    stderr: str = Field(default="", description="Captured standard error or traceback")
    exit_code: int = Field(default=0, description="Process exit code (0 is success)")
    duration_ms: float = Field(default=0.0, description="Execution duration in milliseconds")
    timed_out: bool = Field(default=False, description="Whether execution exceeded time limit")


class CodeRunner(ABC):
    """Abstract base runner interface for sandboxed execution."""

    @abstractmethod
    def run_python(
        self,
        code: str,
        stdin: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
    ) -> RunResult:
        """Execute a Python snippet and capture its output."""
        pass

    @abstractmethod
    def run_java(
        self,
        code: str,
        stdin: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
    ) -> RunResult:
        """Compile and execute a Java program and capture its output."""
        pass

    @abstractmethod
    def run_cpp(
        self,
        code: str,
        stdin: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
    ) -> RunResult:
        """Compile and execute a C++ program and capture its output."""
        pass
