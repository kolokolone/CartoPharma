from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.db.favorites_repository import (
    delete_favorite_pharmacy,
    get_favorite_pharmacy_status,
    put_favorite_pharmacy,
)
from app.db.pharmacy_repository import get_pharmacy_details, get_pharmacy_nearby_poi
from app.models.schemas import FavoriteStatusResponse, PharmacyDetailResponse, PharmacyNearbyPoiResponse


router = APIRouter(prefix="/pharmacies", tags=["pharmacies"])


@router.get("/{establishment_id}", response_model=PharmacyDetailResponse)
async def get_pharmacy_detail_route(establishment_id: str) -> PharmacyDetailResponse:
    payload = get_pharmacy_details(establishment_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Pharmacy not found")
    return payload


@router.get('/{establishment_id}/nearby-poi', response_model=PharmacyNearbyPoiResponse)
async def get_pharmacy_nearby_poi_route(
    establishment_id: str,
    radius_m: int = Query(default=1000, ge=100, le=10_000),
) -> PharmacyNearbyPoiResponse:
    payload = get_pharmacy_nearby_poi(establishment_id, radius_m=radius_m)
    if payload is None:
        raise HTTPException(status_code=404, detail='Pharmacy not found')
    return payload


@router.get('/{establishment_id}/favorite', response_model=FavoriteStatusResponse)
async def get_pharmacy_favorite_route(establishment_id: str) -> FavoriteStatusResponse:
    payload = get_pharmacy_details(establishment_id)
    if payload is None:
        raise HTTPException(status_code=404, detail='Pharmacy not found')
    return get_favorite_pharmacy_status(establishment_id)


@router.put('/{establishment_id}/favorite', response_model=FavoriteStatusResponse)
async def put_pharmacy_favorite_route(establishment_id: str) -> FavoriteStatusResponse:
    payload = get_pharmacy_details(establishment_id)
    if payload is None:
        raise HTTPException(status_code=404, detail='Pharmacy not found')
    return put_favorite_pharmacy(establishment_id)


@router.delete('/{establishment_id}/favorite', response_model=FavoriteStatusResponse)
async def delete_pharmacy_favorite_route(establishment_id: str) -> FavoriteStatusResponse:
    payload = get_pharmacy_details(establishment_id)
    if payload is None:
        raise HTTPException(status_code=404, detail='Pharmacy not found')
    return delete_favorite_pharmacy(establishment_id)
