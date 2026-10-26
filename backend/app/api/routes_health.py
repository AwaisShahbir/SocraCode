from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from app.config import settings

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    version: str
    runner: str
    languages_supported: List[str]


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Return system and runner operational status."""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        runner=settings.runner_type,
        languages_supported=["python", "java", "cpp"],
    )
