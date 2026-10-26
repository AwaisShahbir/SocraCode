from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.parser import parse_python_error
from app.rules import match_python_rules
from app.hints import LevelGate, LevelGateError, UnlockedHint
from app.db.repository import AttemptRepository

router = APIRouter(tags=["Attempts & Hints"])
repo = AttemptRepository()
gate = LevelGate(repository=repo)


class CreateAttemptRequest(BaseModel):
    language: str = Field(default="python", description="Language of snippet")
    source: str = Field(default="web", description="Origin client ('web' or 'extension')")
    code: str = Field(..., description="Student code snippet")
    error_text: str = Field(..., description="Captured error traceback or stderr")
    timed_out: bool = Field(default=False, description="Whether execution timed out")
    user_id: Optional[str] = Field(default=None, description="Optional student ID")
    assignment_id: Optional[str] = Field(default=None, description="Optional assignment ID")


class AttemptResponse(BaseModel):
    id: str
    language: str
    source: str
    category: str
    concept: str
    buggy_line: int
    confidence: float
    current_level: int
    max_level_allowed: int
    started_at: str


class ResolveAttemptRequest(BaseModel):
    reflection: Optional[str] = Field(
        default=None,
        description="Optional student reflection on what caused the bug and how it was fixed",
    )


class FeedbackRequest(BaseModel):
    helpful: bool = Field(..., description="True if hint was helpful, False otherwise")


@router.post("/attempts", response_model=AttemptResponse, status_code=status.HTTP_201_CREATED)
def create_attempt(req: CreateAttemptRequest) -> AttemptResponse:
    """Analyze code failure, match bug category, and initialize a student attempt."""
    if req.language.lower().strip() != "python":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language '{req.language}' not supported in Phase 1.",
        )

    # 1. Parse error
    parsed = parse_python_error(req.code, req.error_text, timed_out=req.timed_out)

    # 2. Rule matching
    matched = match_python_rules(req.code, parsed)

    # 3. Create persistent record
    attempt = repo.create_attempt(
        language=req.language,
        source=req.source,
        code=req.code,
        error_text=req.error_text,
        category=matched.category.value,
        concept=matched.concept,
        buggy_line=matched.line_number,
        confidence=matched.confidence,
        user_id=req.user_id,
        assignment_id=req.assignment_id,
        max_level_allowed=3,  # Capped at Level 3 for Step 2
    )

    return AttemptResponse(**attempt)


@router.post("/attempts/{attempt_id}/hint", response_model=UnlockedHint)
def get_next_hint(attempt_id: str) -> UnlockedHint:
    """Unlock the next sequential hint level. Level gate enforces strict progression."""
    try:
        return gate.unlock_next_hint(attempt_id)
    except LevelGateError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        )


@router.post("/attempts/{attempt_id}/resolve")
def resolve_attempt(attempt_id: str, req: Optional[ResolveAttemptRequest] = None) -> Dict[str, Any]:
    """Mark an attempt resolved after the student successfully fixes the bug."""
    reflection = req.reflection if req else None
    success = repo.resolve_attempt(attempt_id, reflection=reflection)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attempt '{attempt_id}' not found.",
        )
    return {"status": "resolved", "attempt_id": attempt_id}


@router.post("/hints/{hint_id}/feedback")
def submit_hint_feedback(hint_id: str, req: FeedbackRequest) -> Dict[str, Any]:
    """Record helpfulness rating for a displayed hint."""
    success = repo.record_hint_feedback(hint_id, helpful=req.helpful)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hint event '{hint_id}' not found.",
        )
    return {"status": "recorded", "hint_id": hint_id, "helpful": req.helpful}
