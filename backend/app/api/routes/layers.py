from fastapi import APIRouter, HTTPException, Query

from app.db.poi_repository import PoiBoundingBox
from app.models.schemas import GeoPointCollectionResponse, LayersCatalogResponse
from app.services.poi_service import get_layers_catalog_response, get_points_response


router = APIRouter(prefix="/layers", tags=["layers"])


@router.get("", response_model=LayersCatalogResponse)
async def get_layers_catalog() -> LayersCatalogResponse:
    return get_layers_catalog_response()


@router.get("/points", response_model=GeoPointCollectionResponse)
async def get_layer_points(
    layers: list[str] = Query(default=[]),
    bbox: str | None = Query(default=None, description="minLon,minLat,maxLon,maxLat"),
) -> GeoPointCollectionResponse:
    return get_points_response(layers=layers, bbox=_parse_bbox(bbox))


def _parse_bbox(raw_bbox: str | None) -> PoiBoundingBox | None:
    if raw_bbox is None or not raw_bbox.strip():
        return None

    values = [segment.strip() for segment in raw_bbox.split(",")]
    if len(values) != 4:
        raise HTTPException(status_code=422, detail="bbox must contain exactly four comma-separated numbers")

    try:
        min_lon, min_lat, max_lon, max_lat = (float(value) for value in values)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="bbox must contain valid numbers") from exc

    if min_lon > max_lon or min_lat > max_lat:
        raise HTTPException(status_code=422, detail="bbox min values must be lower than max values")

    return PoiBoundingBox(min_lon=min_lon, min_lat=min_lat, max_lon=max_lon, max_lat=max_lat)
