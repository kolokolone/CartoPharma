from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


LayerType = str


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
    source_status: str | None = None
    updated_at_utc: str | None = None


class LayersCatalogResponse(BaseModel):
    country_scope: Literal["FRANCE"] = "FRANCE"
    layers: list[LayerDefinition]


class GeoPointProperties(BaseModel):
    id: str
    layer: LayerType
    layer_label: str | None = None
    layer_color: str | None = None
    name: str
    display_name: str | None = None
    city: str
    address_line_1: str | None = None
    address_line_2: str | None = None
    postal_code: str | None = None
    department_code: str | None = None
    region: str | None = None
    country_code: str | None = None
    phone: str | None = None
    website: str | None = None
    opening_hours: str | None = None
    source_name: str | None = None
    source_record_id: str | None = None
    geocode_status: str | None = None
    geocode_score: float | None = None
    geocode_provider: str | None = None
    finess: str | None = None
    rpps: str | None = None
    adeli: str | None = None
    siret: str | None = None
    last_updated_at: str | None = None


class GeoPointFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    geometry: dict
    properties: GeoPointProperties


class GeoPointCollectionResponse(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[GeoPointFeature]
