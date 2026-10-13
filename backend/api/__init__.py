from fastapi import APIRouter
from backend.api import health, notes, ui
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(notes.router, prefix="/api", tags=["notes"])
api_router.include_router(ui.router, tags=["ui"])
