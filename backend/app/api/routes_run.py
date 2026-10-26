from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.runner import get_runner, RunResult

router = APIRouter(tags=["Code Execution"])


class RunRequest(BaseModel):
    language: str = Field(
        default="python",
        description="Programming language identifier (e.g. 'python')",
    )
    code: str = Field(
        ...,
        description="Source code to execute",
    )
    stdin: Optional[str] = Field(
        default=None,
        description="Optional standard input string",
    )


@router.post("/runs", response_model=RunResult, status_code=status.HTTP_200_OK)
def run_code(req: RunRequest) -> RunResult:
    """
    Executes student code within the sandboxed environment.
    Captures stdout, stderr, execution duration, and exit status.
    """
    normalized_lang = req.language.lower().strip()
    if normalized_lang in ("cpp", "c++"):
        normalized_lang = "cpp"

    supported_languages = ["python", "java", "cpp"]
    if normalized_lang not in supported_languages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language '{req.language}' is not yet supported. Supported: {supported_languages}",
        )

    runner = get_runner()
    if normalized_lang == "java":
        result = runner.run_java(code=req.code, stdin=req.stdin)
    elif normalized_lang == "cpp":
        result = runner.run_cpp(code=req.code, stdin=req.stdin)
    else:
        result = runner.run_python(code=req.code, stdin=req.stdin)
    return result
