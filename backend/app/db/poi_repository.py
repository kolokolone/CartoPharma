from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
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
