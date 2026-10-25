from app.runner.base import CodeRunner, RunResult
from app.runner.local_runner import LocalSubprocessRunner

# Factory function to obtain the appropriate runner
def get_runner() -> CodeRunner:
    return LocalSubprocessRunner()

__all__ = ["CodeRunner", "RunResult", "LocalSubprocessRunner", "get_runner"]
