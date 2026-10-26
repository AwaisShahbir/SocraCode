from fastapi import APIRouter
from app.api.routes_health import router as health_router
from app.api.routes_run import router as run_router
from app.api.routes_attempts import router as attempts_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(run_router)
api_router.include_router(attempts_router)

__all__ = ["api_router"]
