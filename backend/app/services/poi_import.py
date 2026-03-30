from __future__ import annotations

import csv
from contextlib import closing
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from app.core.config import get_csv_dir
from app.db.database import utc_now_iso
from app.db.poi_database import connect_poi, rebuild_poi_rtree


DEFAULT_LAYER_METADATA: dict[str, dict[str, object]] = {
    "pharmacies": {
        "label": "Pharmacies",
        "category": "Sante",
        "priority": 1,
        "color": "#1d4ed8",
        "visible_by_default": 1,
    },
    "health_professionals": {
        "label": "Autres professionnels de sante",
        "category": "Sante",
        "priority": 2,
        "color": "#0f766e",
        "visible_by_default": 1,
    },
    "public_transport": {
        "label": "Transports publics",
        "category": "Mobilite",
        "priority": 3,
        "color": "#7c3aed",
        "visible_by_default": 1,
    },
    "shops": {
        "label": "Commerces utiles",
        "category": "Services",
        "priority": 4,
        "color": "#c2410c",
        "visible_by_default": 0,
    },
    "points_of_interest": {
        "label": "Points d'interet",
        "category": "Services",
        "priority": 5,
        "color": "#be123c",
        "visible_by_default": 0,
    },
}

FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "source_record_id": ("source_record_id", "id", "record_id", "external_id"),
    "name": ("name", "nom", "raison_sociale", "officine"),
    "display_name": ("display_name", "display", "libelle"),
    "address_line_1": ("address_line_1", "address", "adresse", "adresse_ligne_1"),
    "address_line_2": ("address_line_2", "adresse_ligne_2"),
    "postal_code": ("postal_code", "postcode", "code_postal", "cp"),
    "city": ("city", "ville", "commune"),
    "department_code": ("department_code", "departement", "department"),
    "region": ("region",),
    "country_code": ("country_code", "country", "pays"),
    "phone": ("phone", "telephone", "tel"),
    "website": ("website", "site_web", "url"),
    "opening_hours": ("opening_hours", "horaires"),
    "latitude": ("latitude", "lat", "y"),
    "longitude": ("longitude", "lon", "lng", "x"),
    "finess": ("finess",),
    "rpps": ("rpps",),
    "adeli": ("adeli",),
    "siret": ("siret",),
}


@dataclass(frozen=True)
class PoiImportSummary:
    files_processed: int
    rows_imported: int
    rows_rejected: int
    indexed_rows: int


def discover_csv_files(csv_dir: Path | None = None) -> list[Path]:
    directory = csv_dir or get_csv_dir()
    if not directory.exists():
        return []
    return sorted(path for path in directory.glob("*.csv") if path.is_file())


def import_csv_directory(csv_dir: Path | None = None) -> PoiImportSummary:
    files = discover_csv_files(csv_dir)
    imported = 0
    rejected = 0

    for csv_path in files:
        file_imported, file_rejected = import_csv_file(csv_path)
        imported += file_imported
        rejected += file_rejected

    indexed_rows = rebuild_poi_rtree()
    return PoiImportSummary(
        files_processed=len(files),
        rows_imported=imported,
        rows_rejected=rejected,
        indexed_rows=indexed_rows,
    )


def import_csv_file(csv_path: Path) -> tuple[int, int]:
    layer_id = csv_path.stem
    metadata = DEFAULT_LAYER_METADATA.get(
        layer_id,
        {
            "label": layer_id.replace("_", " ").title(),
            "category": "POI",
            "priority": 5,
            "color": "#334155",
            "visible_by_default": 0,
        },
    )
    timestamp = utc_now_iso()
    file_hash = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    imported = 0
    rejected = 0

    with closing(connect_poi()) as connection:
        connection.execute(
            """
            INSERT INTO poi_layer (id, label, category, priority, color, visible_by_default, is_active, source_status, updated_at_utc)
            VALUES (?, ?, ?, ?, ?, ?, 1, 'imported', ?)
            ON CONFLICT(id) DO UPDATE SET
                label = excluded.label,
                category = excluded.category,
                priority = excluded.priority,
                color = excluded.color,
                visible_by_default = excluded.visible_by_default,
                is_active = 1,
                source_status = excluded.source_status,
                updated_at_utc = excluded.updated_at_utc
            """,
            (
                layer_id,
                metadata["label"],
                metadata["category"],
                metadata["priority"],
                metadata["color"],
                metadata["visible_by_default"],
                timestamp,
            ),
        )
        connection.execute("DELETE FROM poi WHERE layer_id = ? AND source_name = ?", (layer_id, csv_path.stem))

        source_file_id = connection.execute(
            """
            INSERT INTO poi_source_file (layer_id, file_name, file_path, file_hash, imported_at_utc, row_count, status, notes)
            VALUES (?, ?, ?, ?, ?, 0, 'running', NULL)
            """,
            (layer_id, csv_path.name, str(csv_path), file_hash, timestamp),
        ).lastrowid

        with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = _build_csv_reader(handle, csv_path)
            for row_number, row in enumerate(reader, start=2):
                try:
                    normalized = _normalize_row(row, layer_id=layer_id, source_name=csv_path.stem, row_number=row_number)
                    connection.execute(
                        """
                        INSERT INTO poi (
                            source_name, source_record_id, layer_id, name, display_name, address_line_1, address_line_2,
                            postal_code, city, department_code, region, country_code, finess, rpps, adeli, siret,
                            phone, website, opening_hours, latitude, longitude, geocode_status, geocode_score,
                            geocode_provider, raw_address, normalized_address, is_active, last_seen_at_utc,
                            created_at_utc, updated_at_utc
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
                        ON CONFLICT(layer_id, source_record_id) DO UPDATE SET
                            name = excluded.name,
                            display_name = excluded.display_name,
                            address_line_1 = excluded.address_line_1,
                            address_line_2 = excluded.address_line_2,
                            postal_code = excluded.postal_code,
                            city = excluded.city,
                            department_code = excluded.department_code,
                            region = excluded.region,
                            country_code = excluded.country_code,
                            finess = excluded.finess,
                            rpps = excluded.rpps,
                            adeli = excluded.adeli,
                            siret = excluded.siret,
                            phone = excluded.phone,
                            website = excluded.website,
                            opening_hours = excluded.opening_hours,
                            latitude = excluded.latitude,
                            longitude = excluded.longitude,
                            geocode_status = excluded.geocode_status,
                            geocode_score = excluded.geocode_score,
                            geocode_provider = excluded.geocode_provider,
                            raw_address = excluded.raw_address,
                            normalized_address = excluded.normalized_address,
                            is_active = 1,
                            last_seen_at_utc = excluded.last_seen_at_utc,
                            updated_at_utc = excluded.updated_at_utc
                        """,
                        normalized,
                    )
                    imported += 1
                except ValueError as exc:
                    rejected += 1
                    connection.execute(
                        """
                        INSERT INTO poi_import_error (
                            source_file_id, source_row_number, layer_id, error_type, error_message, raw_payload_json, created_at_utc
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (source_file_id, row_number, layer_id, "validation", str(exc), json.dumps(row, ensure_ascii=True), utc_now_iso()),
                    )

        connection.execute(
            "UPDATE poi_source_file SET row_count = ?, status = ?, notes = ? WHERE id = ?",
            (imported + rejected, "success", f"Imported={imported}; rejected={rejected}", source_file_id),
        )
        connection.commit()

    return imported, rejected


def _build_csv_reader(handle, csv_path: Path) -> csv.DictReader[str]:
    sample = csv_path.read_text(encoding="utf-8-sig")
    try:
        dialect = csv.Sniffer().sniff(sample[:2048], delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    return csv.DictReader(handle, dialect=dialect)


def _normalize_row(
    row: dict[str, str | None],
    *,
    layer_id: str,
    source_name: str,
    row_number: int,
) -> tuple[object, ...]:
    name = _pick_value(row, "name")
    display_name = _pick_value(row, "display_name") or name
    address_line_1 = _pick_value(row, "address_line_1")
    postal_code = _pick_value(row, "postal_code")
    city = _pick_value(row, "city")
    if not (name or display_name):
        raise ValueError("Missing name/display_name")
    if not (address_line_1 or city):
        raise ValueError("Missing address context")

    latitude = _parse_float(_pick_value(row, "latitude"))
    longitude = _parse_float(_pick_value(row, "longitude"))
    geocode_status = "resolved" if latitude is not None and longitude is not None else "pending"
    geocode_score = 1.0 if geocode_status == "resolved" else None
    geocode_provider = "csv_coordinates" if geocode_status == "resolved" else None
    timestamp = utc_now_iso()

    source_record_id = (
        _pick_value(row, "source_record_id")
        or _pick_value(row, "finess")
        or _pick_value(row, "rpps")
        or _pick_value(row, "adeli")
        or _pick_value(row, "siret")
        or f"{source_name}:{row_number}"
    )
    raw_address = ", ".join(part for part in [address_line_1, postal_code, city] if part)

    return (
        source_name,
        source_record_id,
        layer_id,
        name,
        display_name,
        address_line_1,
        _pick_value(row, "address_line_2"),
        postal_code,
        city,
        _pick_value(row, "department_code"),
        _pick_value(row, "region"),
        _pick_value(row, "country_code") or "FR",
        _pick_value(row, "finess"),
        _pick_value(row, "rpps"),
        _pick_value(row, "adeli"),
        _pick_value(row, "siret"),
        _pick_value(row, "phone"),
        _pick_value(row, "website"),
        _pick_value(row, "opening_hours"),
        latitude,
        longitude,
        geocode_status,
        geocode_score,
        geocode_provider,
        raw_address,
        raw_address,
        timestamp,
        timestamp,
        timestamp,
    )


def _pick_value(row: dict[str, str | None], target: str) -> str | None:
    aliases = FIELD_ALIASES.get(target, (target,))
    for key in aliases:
        value = row.get(key)
        if value is None:
            continue
        normalized = value.strip()
        if normalized:
            return normalized
    return None


def _parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    normalized = value.strip().replace(",", ".")
    if not normalized:
        return None
    try:
        return float(normalized)
    except ValueError as exc:
        raise ValueError(f"Invalid coordinate value: {value}") from exc
