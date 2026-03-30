from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.db.pharmacy_repository import get_pharmacy_details
from app.models.schemas import PharmacyDetailResponse


router = APIRouter(prefix="/pharmacies", tags=["pharmacies"])


@router.get("/{establishment_id}", response_model=PharmacyDetailResponse)
async def get_pharmacy_detail_route(establishment_id: str) -> PharmacyDetailResponse:
    payload = get_pharmacy_details(establishment_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Pharmacy not found")
    return payload
