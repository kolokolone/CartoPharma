from __future__ import annotations

from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool

from app.models.schemas import RebuildPoiResponse
from app.services.poi_rebuild import PoiRebuildInProgressError, rebuild_poi_database


router = APIRouter(prefix="/indexing", tags=["indexing"])


@router.post("/rebuild-poi", response_model=RebuildPoiResponse)
async def rebuild_poi_route() -> RebuildPoiResponse:
    try:
        report = await run_in_threadpool(rebuild_poi_database)
    except PoiRebuildInProgressError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return RebuildPoiResponse(**report.__dict__)
