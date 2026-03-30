from __future__ import annotations

from contextlib import closing
import sqlite3
from pathlib import Path

from app.core.config import ensure_runtime_dirs, get_poi_database_path


def connect_poi(database_path: Path | None = None) -> sqlite3.Connection:
    ensure_runtime_dirs()
    db_path = database_path or get_poi_database_path()
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_poi_database(database_path: Path | None = None) -> Path:
    db_path = database_path or get_poi_database_path()
    ensure_runtime_dirs()

    with closing(connect_poi(db_path)) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS poi_layer (
                id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                category TEXT NOT NULL,
                priority INTEGER NOT NULL,
                color TEXT NOT NULL,
                visible_by_default INTEGER NOT NULL DEFAULT 0,
                is_active INTEGER NOT NULL DEFAULT 1,
                source_status TEXT NOT NULL DEFAULT 'imported',
                updated_at_utc TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS poi_source_file (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                layer_id TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                imported_at_utc TEXT NOT NULL,
                row_count INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (layer_id) REFERENCES poi_layer(id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS poi_import_error (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_file_id INTEGER,
                source_row_number INTEGER NOT NULL,
                layer_id TEXT NOT NULL,
                error_type TEXT NOT NULL,
                error_message TEXT NOT NULL,
                raw_payload_json TEXT NOT NULL,
                created_at_utc TEXT NOT NULL,
                FOREIGN KEY (source_file_id) REFERENCES poi_source_file(id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS poi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT NOT NULL,
                source_record_id TEXT NOT NULL,
                layer_id TEXT NOT NULL,
                name TEXT,
                display_name TEXT,
                address_line_1 TEXT,
                address_line_2 TEXT,
                postal_code TEXT,
                city TEXT,
                department_code TEXT,
                region TEXT,
                country_code TEXT,
                finess TEXT,
                rpps TEXT,
                adeli TEXT,
                siret TEXT,
                phone TEXT,
                website TEXT,
                opening_hours TEXT,
                pharmacy_establishment_id TEXT,
                pharmacist_count INTEGER NOT NULL DEFAULT 0,
                pharmacy_type TEXT,
                latitude REAL,
                longitude REAL,
                geocode_status TEXT NOT NULL DEFAULT 'pending',
                geocode_score REAL,
                geocode_provider TEXT,
                raw_address TEXT,
                normalized_address TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                last_seen_at_utc TEXT NOT NULL,
                created_at_utc TEXT NOT NULL,
                updated_at_utc TEXT NOT NULL,
                UNIQUE(layer_id, source_record_id),
                FOREIGN KEY (layer_id) REFERENCES poi_layer(id)
            )
            """
        )
        _ensure_column(connection, "poi", "pharmacy_establishment_id", "TEXT")
        _ensure_column(connection, "poi", "pharmacist_count", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(connection, "poi", "pharmacy_type", "TEXT")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS pharmacy_establishment (
                establishment_id TEXT PRIMARY KEY,
                establishment_type TEXT,
                display_name TEXT NOT NULL,
                legal_name TEXT,
                address_line_1 TEXT,
                postal_code TEXT,
                city TEXT,
                department TEXT,
                region TEXT,
                phone TEXT,
                fax TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at_utc TEXT NOT NULL,
                updated_at_utc TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS pharmacist (
                rpps TEXT PRIMARY KEY,
                title TEXT,
                last_name TEXT,
                first_name TEXT,
                first_registration_date TEXT,
                created_at_utc TEXT NOT NULL,
                updated_at_utc TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS pharmacist_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rpps TEXT NOT NULL,
                establishment_id TEXT NOT NULL,
                function_label TEXT,
                registration_date TEXT,
                section_code TEXT,
                is_primary_activity INTEGER NOT NULL DEFAULT 0,
                created_at_utc TEXT NOT NULL,
                updated_at_utc TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS pharmacist_degree (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rpps TEXT NOT NULL,
                degree_label TEXT,
                degree_date TEXT,
                university TEXT,
                region TEXT,
                created_at_utc TEXT NOT NULL,
                updated_at_utc TEXT NOT NULL
            )
            """
        )
        connection.execute("CREATE INDEX IF NOT EXISTS idx_poi_layer_id ON poi(layer_id)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_poi_is_active ON poi(is_active)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_poi_geocode_status ON poi(geocode_status)")
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_poi_pharmacy_establishment_id ON poi(pharmacy_establishment_id)"
        )
        connection.execute("CREATE INDEX IF NOT EXISTS idx_pharmacist_activity_rpps ON pharmacist_activity(rpps)")
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_pharmacist_activity_establishment_id ON pharmacist_activity(establishment_id)"
        )
        connection.execute("CREATE INDEX IF NOT EXISTS idx_pharmacist_degree_rpps ON pharmacist_degree(rpps)")
        connection.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS poi_rtree USING rtree(
                poi_id,
                min_lon, max_lon,
                min_lat, max_lat
            )
            """
        )
        connection.commit()

    return db_path


def rebuild_poi_rtree(database_path: Path | None = None) -> int:
    with closing(connect_poi(database_path)) as connection:
        connection.execute("DELETE FROM poi_rtree")
        connection.execute(
            """
            INSERT INTO poi_rtree (poi_id, min_lon, max_lon, min_lat, max_lat)
            SELECT id, longitude, longitude, latitude, latitude
            FROM poi
            WHERE is_active = 1
              AND latitude IS NOT NULL
              AND longitude IS NOT NULL
            """
        )
        inserted = connection.execute("SELECT COUNT(*) AS count FROM poi_rtree").fetchone()["count"]
        connection.commit()

    return int(inserted)


def _ensure_column(connection: sqlite3.Connection, table_name: str, column_name: str, definition: str) -> None:
    existing_columns = {
        row["name"]
        for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    }
    if column_name in existing_columns:
        return
    connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")
