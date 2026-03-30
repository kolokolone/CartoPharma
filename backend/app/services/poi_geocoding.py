from __future__ import annotations

import csv
from contextlib import closing
from dataclasses import dataclass
import io
from pathlib import Path

import requests

from app.core.config import APP_NAME, APP_VERSION, get_geocoding_api_base_url, get_geocoding_batch_size, is_batch_geocoding_enabled
from app.db.database import utc_now_iso
from app.db.poi_database import connect_poi, rebuild_poi_rtree


GEOCODING_PROVIDER = "geoplateforme_search_csv"


@dataclass(frozen=True)
class PendingGeocodeRow:
    poi_id: int
    address_line_1: str
    postal_code: str
    city: str


def synchronize_geocode_statuses(database_path: Path | None = None) -> dict[str, int]:
    if is_batch_geocoding_enabled():
        pending_rows = _load_pending_geocode_rows(database_path)
        if pending_rows:
            _geocode_pending_rows(pending_rows, database_path)

    with closing(connect_poi(database_path)) as connection:
        connection.execute(
            """
            UPDATE poi
            SET geocode_status = CASE
                    WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 'resolved'
                    ELSE 'pending'
                END,
                geocode_score = CASE
                    WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN COALESCE(geocode_score, 1.0)
                    ELSE NULL
                END,
                geocode_provider = CASE
                    WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN COALESCE(geocode_provider, 'csv_coordinates')
                    ELSE NULL
                END
            """
        )
        resolved = connection.execute(
            "SELECT COUNT(*) AS count FROM poi WHERE geocode_status = 'resolved'"
        ).fetchone()["count"]
        pending = connection.execute(
            "SELECT COUNT(*) AS count FROM poi WHERE geocode_status = 'pending'"
        ).fetchone()["count"]
        connection.commit()

    indexed_rows = rebuild_poi_rtree(database_path)
    return {"resolved": int(resolved), "pending": int(pending), "indexed_rows": indexed_rows}


def _load_pending_geocode_rows(database_path: Path | None = None) -> list[PendingGeocodeRow]:
    with closing(connect_poi(database_path)) as connection:
        rows = connection.execute(
            """
            SELECT id, address_line_1, postal_code, city
            FROM poi
            WHERE is_active = 1
              AND latitude IS NULL
              AND longitude IS NULL
              AND address_line_1 IS NOT NULL
              AND postal_code IS NOT NULL
              AND city IS NOT NULL
            ORDER BY id ASC
            """
        ).fetchall()

    return [
        PendingGeocodeRow(
            poi_id=int(row["id"]),
            address_line_1=row["address_line_1"],
            postal_code=row["postal_code"],
            city=row["city"],
        )
        for row in rows
    ]


def _geocode_pending_rows(rows: list[PendingGeocodeRow], database_path: Path | None = None) -> None:
    batch_size = get_geocoding_batch_size()
    for chunk_start in range(0, len(rows), batch_size):
        chunk = rows[chunk_start : chunk_start + batch_size]
        response_text = _submit_batch_geocoding(chunk)
        updates = _parse_batch_response(response_text)
        if updates:
            _apply_geocode_updates(updates, database_path)


def _submit_batch_geocoding(rows: list[PendingGeocodeRow]) -> str:
    csv_buffer = io.StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=["poi_id", "address_line_1", "postal_code", "city"])
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                "poi_id": row.poi_id,
                "address_line_1": row.address_line_1,
                "postal_code": row.postal_code,
                "city": row.city,
            }
        )

    response = requests.post(
        f"{get_geocoding_api_base_url()}/search/csv",
        files={"data": ("pending-poi.csv", csv_buffer.getvalue().encode("utf-8"), "text/csv")},
        data=[
            ("columns", "address_line_1"),
            ("postcode", "postal_code"),
            ("city", "city"),
            ("indexes", "address"),
        ],
        headers={"User-Agent": f"{APP_NAME}/{APP_VERSION}"},
        timeout=(30, 600),
    )
    response.raise_for_status()
    response.encoding = response.encoding or "utf-8"
    return response.text


def _parse_batch_response(response_text: str) -> list[tuple[float, float, float | None, int]]:
    updates: list[tuple[float, float, float | None, int]] = []
    reader = csv.DictReader(io.StringIO(response_text))
    for row in reader:
        poi_id = _try_parse_int(row.get("poi_id"))
        longitude = _try_parse_float(row.get("longitude"))
        latitude = _try_parse_float(row.get("latitude"))
        result_status = (row.get("result_status") or "").strip().lower()
        if poi_id is None or longitude is None or latitude is None:
            continue
        if result_status and result_status != "ok":
            continue
        score = _try_parse_float(row.get("result_score"))
        updates.append((latitude, longitude, score, poi_id))
    return updates


def _apply_geocode_updates(updates: list[tuple[float, float, float | None, int]], database_path: Path | None = None) -> None:
    timestamp = utc_now_iso()
    with closing(connect_poi(database_path)) as connection:
        connection.executemany(
            """
            UPDATE poi
            SET latitude = ?,
                longitude = ?,
                geocode_status = 'resolved',
                geocode_score = ?,
                geocode_provider = ?,
                updated_at_utc = ?
            WHERE id = ?
            """,
            [
                (latitude, longitude, score, GEOCODING_PROVIDER, timestamp, poi_id)
                for latitude, longitude, score, poi_id in updates
            ],
        )
        connection.commit()


def _try_parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    normalized = value.replace(",", ".").strip()
    if not normalized:
        return None
    try:
        return float(normalized)
    except ValueError:
        return None


def _try_parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    try:
        return int(normalized)
    except ValueError:
        return None
