from __future__ import annotations

from fastapi import APIRouter, Query

from app.models.schemas import SearchResponse
from app.services.search_service import search_catalog


router = APIRouter(prefix='/search', tags=['search'])


@router.get('', response_model=SearchResponse)
async def search_route(
    q: str = Query(default=''),
    kind: str = Query(default='results', pattern='^(suggestions|results)$'),
    limit: int = Query(default=20, ge=1, le=50),
) -> SearchResponse:
    return search_catalog(query=q, kind=kind, limit=limit)
