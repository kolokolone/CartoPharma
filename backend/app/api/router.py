from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.indexing import router as indexing_router
from app.api.routes.layers import router as layers_router
from app.api.routes.pharmacies import router as pharmacies_router
from app.api.routes.search import router as search_router
from app.api.routes.settings import router as settings_router


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(settings_router)
api_router.include_router(indexing_router)
api_router.include_router(layers_router)
api_router.include_router(pharmacies_router)
api_router.include_router(search_router)
