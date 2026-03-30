from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


LayerType = Literal["pharmacies", "health_professionals", "public_transport", "shops", "points_of_interest"]


class ApiStatusResponse(BaseModel):
    message: str
    version: str
    status: str


class HealthResponse(BaseModel):
    status: str
    scope: str
    database: str


class SettingsResponse(BaseModel):
    country_scope: Literal["FRANCE"] = "FRANCE"
    theme: Literal["light", "dark", "system"] = "light"
    show_labels: bool = True
    compact_controls: bool = False


class SettingsPatchRequest(BaseModel):
    theme: Literal["light", "dark", "system"] | None = None
    show_labels: bool | None = None
    compact_controls: bool | None = None


class LayerDefinition(BaseModel):
    id: LayerType
    label: str
    category: str
    color: str
    priority: int = Field(ge=1, le=5)
    visible_by_default: bool


class LayersCatalogResponse(BaseModel):
    country_scope: Literal["FRANCE"] = "FRANCE"
    layers: list[LayerDefinition]


class GeoPointProperties(BaseModel):
    id: str
    layer: LayerType
    name: str
    city: str


class GeoPointFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    geometry: dict
    properties: GeoPointProperties


class GeoPointCollectionResponse(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[GeoPointFeature]
