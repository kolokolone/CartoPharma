from fastapi import APIRouter

from app.core.config import get_database_path
from app.models.schemas import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    return HealthResponse(status="healthy", scope="foundation", database=str(get_database_path()))
