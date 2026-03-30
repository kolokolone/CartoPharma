from fastapi import APIRouter, Query

from app.models.schemas import GeoPointCollectionResponse, LayerType, LayersCatalogResponse
from app.services.mock_data import LAYER_CATALOG, MOCK_POINTS


router = APIRouter(prefix="/layers", tags=["layers"])


@router.get("", response_model=LayersCatalogResponse)
async def get_layers_catalog() -> LayersCatalogResponse:
    return LayersCatalogResponse(layers=LAYER_CATALOG)


@router.get("/points", response_model=GeoPointCollectionResponse)
async def get_layer_points(
    layers: list[LayerType] = Query(default=[]),
) -> GeoPointCollectionResponse:
    if not layers:
        features = MOCK_POINTS
    else:
        active = set(layers)
        features = [feature for feature in MOCK_POINTS if feature.properties.layer in active]

    return GeoPointCollectionResponse(features=features)
