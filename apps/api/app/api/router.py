from fastapi import APIRouter

from app.api import auth, households

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(households.router)
