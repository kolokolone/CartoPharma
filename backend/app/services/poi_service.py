from __future__ import annotations

from app.db.poi_repository import PoiBoundingBox, list_poi_layers, list_poi_points, poi_database_has_layers
from app.models.schemas import GeoPointCollectionResponse, GeoPointFeature, GeoPointProperties, LayerDefinition, LayersCatalogResponse
from app.services.mock_data import LAYER_CATALOG, MOCK_POINTS


def get_layers_catalog_response() -> LayersCatalogResponse:
    if not poi_database_has_layers():
        return LayersCatalogResponse(layers=LAYER_CATALOG)

    layers = [
        LayerDefinition(
            id=row["id"],
            label=row["label"],
            category=row["category"],
            color=row["color"],
            priority=row["priority"],
            visible_by_default=bool(row["visible_by_default"]),
            source_status=row["source_status"],
            updated_at_utc=row["updated_at_utc"],
        )
        for row in list_poi_layers()
    ]
    return LayersCatalogResponse(layers=layers)


def get_points_response(*, layers: list[str], bbox: PoiBoundingBox | None = None) -> GeoPointCollectionResponse:
    if not poi_database_has_layers():
        features = MOCK_POINTS if not layers else [feature for feature in MOCK_POINTS if feature.properties.layer in set(layers)]
        if bbox is not None:
            features = [feature for feature in features if _feature_in_bbox(feature, bbox)]
        return GeoPointCollectionResponse(features=features)

    rows = list_poi_points(layers=layers, bbox=bbox)
    features = [
        GeoPointFeature(
            geometry={"type": "Point", "coordinates": [row["longitude"], row["latitude"]]},
            properties=GeoPointProperties(
                id=str(row["id"]),
                layer=row["layer_id"],
                layer_label=row["layer_label"],
                layer_color=row["layer_color"],
                name=row["name"] or row["display_name"] or row["source_record_id"],
                display_name=row["display_name"],
                city=row["city"] or "",
                address_line_1=row["address_line_1"],
                address_line_2=row["address_line_2"],
                postal_code=row["postal_code"],
                department_code=row["department_code"],
                region=row["region"],
                country_code=row["country_code"],
                phone=row["phone"],
                website=row["website"],
                opening_hours=row["opening_hours"],
                source_name=row["source_name"],
                source_record_id=row["source_record_id"],
                geocode_status=row["geocode_status"],
                geocode_score=row["geocode_score"],
                geocode_provider=row["geocode_provider"],
                finess=row["finess"],
                rpps=row["rpps"],
                adeli=row["adeli"],
                siret=row["siret"],
                pharmacy_establishment_id=row["pharmacy_establishment_id"],
                pharmacist_count=row["pharmacist_count"],
                pharmacy_type=row["pharmacy_type"],
                last_updated_at=row["updated_at_utc"],
            ),
        )
        for row in rows
        if row["latitude"] is not None and row["longitude"] is not None
    ]
    return GeoPointCollectionResponse(features=features)


def _feature_in_bbox(feature: GeoPointFeature, bbox: PoiBoundingBox) -> bool:
    longitude, latitude = feature.geometry["coordinates"]
    return bbox.min_lon <= longitude <= bbox.max_lon and bbox.min_lat <= latitude <= bbox.max_lat
