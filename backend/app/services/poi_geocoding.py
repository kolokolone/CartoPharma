from __future__ import annotations

from contextlib import closing
from pathlib import Path

from app.db.poi_database import connect_poi, rebuild_poi_rtree


def synchronize_geocode_statuses(database_path: Path | None = None) -> dict[str, int]:
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
