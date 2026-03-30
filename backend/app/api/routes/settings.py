from fastapi import APIRouter

from app.db.settings_repository import get_settings, update_settings
from app.models.schemas import SettingsPatchRequest, SettingsResponse


router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
async def get_settings_route() -> SettingsResponse:
    return get_settings()


@router.patch("", response_model=SettingsResponse)
async def patch_settings(payload: SettingsPatchRequest) -> SettingsResponse:
    return update_settings(payload)
