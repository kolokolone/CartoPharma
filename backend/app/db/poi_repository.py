from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
import math
from pathlib import Path
import sqlite3

from app.db.poi_database import connect_poi


@dataclass(frozen=True)
class PoiBoundingBox:
    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float


def poi_database_has_layers(database_path: Path | None = None) -> bool:
    try:
        with closing(connect_poi(database_path)) as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM poi_layer WHERE is_active = 1"
            ).fetchone()
            return bool(row and row["count"] > 0)
    except sqlite3.Error:
        return False


def list_poi_layers(database_path: Path | None = None) -> list[sqlite3.Row]:
    with closing(connect_poi(database_path)) as connection:
        rows = connection.execute(
            """
            SELECT id, label, category, priority, color, visible_by_default, source_status, updated_at_utc
            FROM poi_layer
            WHERE is_active = 1
            ORDER BY priority ASC, label ASC
            """
        ).fetchall()

    return list(rows)


def list_poi_points(
    *,
    layers: list[str] | None = None,
    bbox: PoiBoundingBox | None = None,
    limit: int = 2000,
    database_path: Path | None = None,
) -> list[sqlite3.Row]:
    params: list[object] = []
    joins = ["INNER JOIN poi_layer ON poi_layer.id = poi.layer_id"]
    where = ["poi.is_active = 1", "poi_layer.is_active = 1"]

    if bbox is not None:
        joins.append("INNER JOIN poi_rtree ON poi_rtree.poi_id = poi.id")
        where.extend(
            [
                "poi_rtree.min_lon <= ?",
                "poi_rtree.max_lon >= ?",
                "poi_rtree.min_lat <= ?",
                "poi_rtree.max_lat >= ?",
            ]
        )
        params.extend([bbox.max_lon, bbox.min_lon, bbox.max_lat, bbox.min_lat])

    if layers:
        placeholders = ", ".join("?" for _ in layers)
        where.append(f"poi.layer_id IN ({placeholders})")
        params.extend(layers)

    params.append(limit)

    query = f"""
        SELECT
            poi.id,
            poi.layer_id,
            poi.name,
            poi.display_name,
            poi.address_line_1,
            poi.address_line_2,
            poi.postal_code,
            poi.city,
            poi.department_code,
            poi.region,
            poi.country_code,
            poi.finess,
            poi.rpps,
            poi.adeli,
            poi.siret,
            poi.phone,
            poi.website,
            poi.opening_hours,
            poi.pharmacy_establishment_id,
            poi.pharmacist_count,
            poi.pharmacy_type,
            poi.latitude,
            poi.longitude,
            poi.geocode_status,
            poi.geocode_score,
            poi.geocode_provider,
            poi.source_name,
            poi.source_record_id,
            poi.updated_at_utc,
            poi_layer.label AS layer_label,
            poi_layer.color AS layer_color
        FROM poi
        {' '.join(joins)}
        WHERE {' AND '.join(where)}
        ORDER BY poi.layer_id ASC, poi.display_name ASC, poi.name ASC
        LIMIT ?
    """

    with closing(connect_poi(database_path)) as connection:
        rows = connection.execute(query, params).fetchall()

    return list(rows)


def list_poi_nearby_pharmacy(
    establishment_id: str,
    *,
    radius_m: int = 1000,
    limit: int = 100,
    database_path: Path | None = None,
) -> list[dict[str, object]]:
    with closing(connect_poi(database_path)) as connection:
        source = connection.execute(
            """
            SELECT id, latitude, longitude
            FROM poi
            WHERE pharmacy_establishment_id = ?
              AND is_active = 1
              AND latitude IS NOT NULL
              AND longitude IS NOT NULL
            ORDER BY updated_at_utc DESC
            LIMIT 1
            """,
            (establishment_id,),
        ).fetchone()

        if source is None:
            return []

        source_latitude = float(source["latitude"])
        source_longitude = float(source["longitude"])
        latitude_delta = radius_m / 111_320
        longitude_divisor = 111_320 * max(math.cos(math.radians(source_latitude)), 0.01)
        longitude_delta = radius_m / longitude_divisor

        rows = connection.execute(
            """
            SELECT
                poi.id,
                poi.layer_id,
                poi.display_name,
                poi.name,
                poi.city,
                poi.postal_code,
                poi.latitude,
                poi.longitude,
                poi.pharmacy_establishment_id,
                poi_layer.label AS layer_label,
                poi_layer.category AS layer_category
            FROM poi
            INNER JOIN poi_layer ON poi_layer.id = poi.layer_id
            WHERE poi.is_active = 1
              AND poi_layer.is_active = 1
              AND poi.latitude IS NOT NULL
              AND poi.longitude IS NOT NULL
              AND poi.latitude BETWEEN ? AND ?
              AND poi.longitude BETWEEN ? AND ?
              AND poi.id != ?
              AND (
                    poi.pharmacy_establishment_id IS NULL
                 OR poi.pharmacy_establishment_id != ?
              )
            ORDER BY poi_layer.priority ASC, poi_layer.label ASC, poi.display_name ASC, poi.name ASC
            LIMIT ?
            """,
            (
                source_latitude - latitude_delta,
                source_latitude + latitude_delta,
                source_longitude - longitude_delta,
                source_longitude + longitude_delta,
                source["id"],
                establishment_id,
                limit * 4,
            ),
        ).fetchall()

    nearby_items: list[dict[str, object]] = []
    for row in rows:
        distance_m = round(
            _haversine_distance_m(
                source_latitude,
                source_longitude,
                float(row["latitude"]),
                float(row["longitude"]),
            )
        )
        if distance_m > radius_m:
            continue

        nearby_items.append(
            {
                "id": str(row["id"]),
                "label": row["display_name"] or row["name"] or row["layer_label"],
                "secondary_label": _build_secondary_label(row["postal_code"], row["city"]),
                "layer_id": row["layer_id"],
                "layer_label": row["layer_label"],
                "category": row["layer_category"],
                "city": row["city"],
                "distance_m": distance_m,
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "target_href": _build_poi_target_href(row["layer_id"], row["pharmacy_establishment_id"]),
                "pharmacy_establishment_id": row["pharmacy_establishment_id"],
            }
        )

        if len(nearby_items) >= limit:
            break

    return nearby_items


def _build_secondary_label(postal_code: str | None, city: str | None) -> str | None:
    value = " ".join(part for part in [postal_code, city] if part)
    return value or None


def _build_poi_target_href(layer_id: str, pharmacy_establishment_id: str | None) -> str:
    if layer_id == "pharmacies" and pharmacy_establishment_id:
        return f"/pharmacie/{pharmacy_establishment_id}"
    return "/map"


def _haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6_371_000
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c
