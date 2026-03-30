from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.layers import router as layers_router
from app.api.routes.settings import router as settings_router


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(settings_router)
api_router.include_router(layers_router)
