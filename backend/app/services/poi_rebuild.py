from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from contextlib import closing
import threading
import time

from app.db.poi_database import connect_poi
from app.db.poi_database import init_poi_database
from app.services.pharmacy_directory_import import import_pharmacy_directory
from app.services.poi_geocoding import synchronize_geocode_statuses
from app.services.poi_import import import_csv_directory


class PoiRebuildInProgressError(RuntimeError):
    pass


@dataclass(frozen=True)
class PoiRebuildReport:
    database: str
    files_detected: int
    generic_files_processed: int
    pharmacy_files_detected: int
    used_specialized_pharmacy_directory: bool
    generic_rows_imported: int
    pharmacies_imported: int
    pharmacists_imported: int
    activities_imported: int
    degrees_imported: int
    rows_rejected: int
    poi_rows_rebuilt: int
    geocoded_resolved: int
    geocoded_pending: int
    duration_ms: int


_REBUILD_LOCK = threading.Lock()


def rebuild_poi_database() -> PoiRebuildReport:
    if not _REBUILD_LOCK.acquire(blocking=False):
        raise PoiRebuildInProgressError("A POI rebuild is already running")

    try:
        started_at = time.perf_counter()
        database_path = init_poi_database()
        _reset_existing_poi_projection(database_path)
        pharmacy_summary = import_pharmacy_directory()
        excluded_layers = {"pharmacies"}
        generic_summary = import_csv_directory(exclude_layer_ids=excluded_layers)
        geocoding_report = synchronize_geocode_statuses()
        duration_ms = int((time.perf_counter() - started_at) * 1000)

        return PoiRebuildReport(
            database=str(database_path),
            files_detected=generic_summary.files_processed + pharmacy_summary.files_detected,
            generic_files_processed=generic_summary.files_processed,
            pharmacy_files_detected=pharmacy_summary.files_detected,
            used_specialized_pharmacy_directory=pharmacy_summary.used_specialized_directory,
            generic_rows_imported=generic_summary.rows_imported,
            pharmacies_imported=pharmacy_summary.establishments_imported,
            pharmacists_imported=pharmacy_summary.pharmacists_imported,
            activities_imported=pharmacy_summary.activities_imported,
            degrees_imported=pharmacy_summary.degrees_imported,
            rows_rejected=generic_summary.rows_rejected + pharmacy_summary.rows_rejected,
            poi_rows_rebuilt=geocoding_report["indexed_rows"],
            geocoded_resolved=geocoding_report["resolved"],
            geocoded_pending=geocoding_report["pending"],
            duration_ms=duration_ms,
        )
    finally:
        _REBUILD_LOCK.release()


def _reset_existing_poi_projection(database_path: str | Path) -> None:
    with closing(connect_poi(Path(database_path))) as connection:
        connection.execute("DELETE FROM poi_import_error")
        connection.execute("DELETE FROM poi_source_file")
        connection.execute("DELETE FROM poi")
        connection.execute("UPDATE poi_layer SET is_active = 0, source_status = 'stale'")
        connection.commit()
