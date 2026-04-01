from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from app.core.config import ensure_runtime_dirs, get_database_path


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def connect(database_path: Path | None = None) -> sqlite3.Connection:
    ensure_runtime_dirs()
    db_path = database_path or get_database_path()
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_database() -> Path:
    db_path = get_database_path()
    ensure_runtime_dirs()

    with connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                theme TEXT NOT NULL DEFAULT 'light',
                show_labels INTEGER NOT NULL DEFAULT 1,
                compact_controls INTEGER NOT NULL DEFAULT 0,
                updated_at_utc TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            INSERT OR IGNORE INTO app_settings (id, theme, show_labels, compact_controls, updated_at_utc)
            VALUES (1, 'light', 1, 0, ?)
            """,
            (utc_now_iso(),),
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS favorite_pharmacy (
                establishment_id TEXT PRIMARY KEY,
                created_at_utc TEXT NOT NULL
            )
            """
        )
        connection.commit()

    return db_path
