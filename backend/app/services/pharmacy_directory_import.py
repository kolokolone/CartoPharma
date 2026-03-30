from __future__ import annotations

import csv
from contextlib import closing
from dataclasses import dataclass
import hashlib
import io
from pathlib import Path
import sqlite3
import unicodedata

from app.core.config import get_csv_dir
from app.db.database import utc_now_iso
from app.db.poi_database import connect_poi, rebuild_poi_rtree
from app.services.poi_import import DEFAULT_LAYER_METADATA


PHARMACY_LAYER_ID = "pharmacies"
PHARMACY_SOURCE_NAME = "pharmacy_directory"
REQUIRED_PHARMACY_CATEGORIES = ("etablissements", "pharmaciens", "activites", "diplomes")
CSV_ENCODINGS = ("utf-16", "utf-16-le", "utf-16-be", "utf-8-sig", "utf-8", "cp1252")


@dataclass(frozen=True)
class PharmacyDirectoryImportSummary:
    files_detected: int
    used_specialized_directory: bool
    establishments_imported: int
    pharmacists_imported: int
    activities_imported: int
    degrees_imported: int
    rows_rejected: int
    poi_rows_projected: int


def import_pharmacy_directory(csv_dir: Path | None = None) -> PharmacyDirectoryImportSummary:
    directory = (csv_dir or get_csv_dir()) / PHARMACY_LAYER_ID
    if not directory.exists():
        return PharmacyDirectoryImportSummary(0, False, 0, 0, 0, 0, 0, 0)

    selected_files = discover_pharmacy_files(directory)
    if not selected_files:
        return PharmacyDirectoryImportSummary(0, False, 0, 0, 0, 0, 0, 0)

    establishments_rows = _read_csv_rows(selected_files["etablissements"])
    pharmacists_rows = _read_csv_rows(selected_files["pharmaciens"])
    activities_rows = _read_csv_rows(selected_files["activites"])
    degrees_rows = _read_csv_rows(selected_files["diplomes"])

    rows_rejected = 0
    timestamp = utc_now_iso()

    establishments: dict[str, dict[str, str | float | None]] = {}
    pharmacists: dict[str, dict[str, str | None]] = {}
    activities: list[dict[str, str | bool | None]] = []
    degrees: list[dict[str, str | None]] = []

    for row in establishments_rows:
        establishment_id = _pick_first(row, "numero_d_etablissement", "numero_etablissement", "establishment_id")
        if not establishment_id:
            rows_rejected += 1
            continue
        display_name = _pick_first(row, "denomination_commerciale", "raison_sociale") or establishment_id
        establishments[establishment_id] = {
            "establishment_id": establishment_id,
            "establishment_type": _pick_first(row, "type_etablissement"),
            "display_name": display_name,
            "legal_name": _pick_first(row, "raison_sociale"),
            "address_line_1": _pick_first(row, "adresse"),
            "postal_code": _pick_first(row, "code_postal"),
            "city": _pick_first(row, "commune", "ville"),
            "department": _pick_first(row, "departement", "department"),
            "region": _pick_first(row, "region"),
            "phone": _pick_first(row, "telephone", "phone"),
            "fax": _pick_first(row, "fax"),
            "website": _pick_first(row, "site_web", "website", "url"),
            "opening_hours": _pick_first(row, "horaires", "opening_hours"),
            "siret": _pick_first(row, "siret"),
            "latitude": _try_parse_float(_pick_first(row, "latitude", "lat", "y")),
            "longitude": _try_parse_float(_pick_first(row, "longitude", "lon", "lng", "x")),
        }

    for row in pharmacists_rows:
        rpps = _pick_first(row, "n_rpps", "n_rpps_pharmacien", "rpps")
        if not rpps:
            rows_rejected += 1
            continue
        pharmacists[rpps] = {
            "rpps": rpps,
            "title": _pick_first(row, "titre", "title"),
            "last_name": _pick_first(row, "nom_d_exercice", "nom", "last_name"),
            "first_name": _pick_first(row, "prenom", "first_name"),
            "first_registration_date": _pick_first(row, "date_de_premiere_inscription", "first_registration_date"),
        }

    for row in activities_rows:
        establishment_id = _pick_first(row, "numero_d_etablissement", "numero_etablissement", "establishment_id")
        rpps = _pick_first(row, "n_rpps_pharmacien", "n_rpps", "rpps")
        if not establishment_id or not rpps:
            rows_rejected += 1
            continue
        if establishment_id not in establishments or rpps not in pharmacists:
            rows_rejected += 1
            continue
        activities.append(
            {
                "rpps": rpps,
                "establishment_id": establishment_id,
                "function_label": _pick_first(row, "fonction", "function_label"),
                "registration_date": _pick_first(row, "date_d_inscription", "registration_date"),
                "section_code": _pick_first(row, "section", "section_code"),
                "is_primary_activity": _parse_bool(_pick_first(row, "activite_principale", "is_primary_activity")),
            }
        )

    for row in degrees_rows:
        rpps = _pick_first(row, "n_rpps_pharmacien", "n_rpps", "rpps")
        if not rpps:
            rows_rejected += 1
            continue
        if rpps not in pharmacists:
            rows_rejected += 1
            continue
        degrees.append(
            {
                "rpps": rpps,
                "degree_label": _pick_first(row, "diplome", "degree_label"),
                "degree_date": _pick_first(row, "date_d_obtention", "degree_date"),
                "university": _pick_first(row, "universite", "university"),
                "region": _pick_first(row, "region"),
            }
        )

    counts_by_establishment: dict[str, int] = {}
    distinct_rpps_by_establishment: dict[str, set[str]] = {}
    for activity in activities:
        establishment_id = str(activity["establishment_id"])
        rpps = str(activity["rpps"])
        distinct_rpps_by_establishment.setdefault(establishment_id, set()).add(rpps)
    for establishment_id, rpps_values in distinct_rpps_by_establishment.items():
        counts_by_establishment[establishment_id] = len(rpps_values)

    with closing(connect_poi()) as connection:
        _upsert_pharmacy_layer(connection, timestamp)
        _reset_pharmacy_domain(connection)
        for category, path in selected_files.items():
            _record_source_file(connection, category, path, timestamp)

        connection.executemany(
            """
            INSERT INTO pharmacy_establishment (
                establishment_id, establishment_type, display_name, legal_name, address_line_1,
                postal_code, city, department, region, phone, fax, is_active, created_at_utc, updated_at_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """,
            [
                (
                    record["establishment_id"],
                    record["establishment_type"],
                    record["display_name"],
                    record["legal_name"],
                    record["address_line_1"],
                    record["postal_code"],
                    record["city"],
                    record["department"],
                    record["region"],
                    record["phone"],
                    record["fax"],
                    timestamp,
                    timestamp,
                )
                for record in establishments.values()
            ],
        )
        connection.executemany(
            """
            INSERT INTO pharmacist (
                rpps, title, last_name, first_name, first_registration_date, created_at_utc, updated_at_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    record["rpps"],
                    record["title"],
                    record["last_name"],
                    record["first_name"],
                    record["first_registration_date"],
                    timestamp,
                    timestamp,
                )
                for record in pharmacists.values()
            ],
        )
        connection.executemany(
            """
            INSERT INTO pharmacist_activity (
                rpps, establishment_id, function_label, registration_date, section_code,
                is_primary_activity, created_at_utc, updated_at_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    activity["rpps"],
                    activity["establishment_id"],
                    activity["function_label"],
                    activity["registration_date"],
                    activity["section_code"],
                    1 if activity["is_primary_activity"] else 0,
                    timestamp,
                    timestamp,
                )
                for activity in activities
            ],
        )
        connection.executemany(
            """
            INSERT INTO pharmacist_degree (
                rpps, degree_label, degree_date, university, region, created_at_utc, updated_at_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    degree["rpps"],
                    degree["degree_label"],
                    degree["degree_date"],
                    degree["university"],
                    degree["region"],
                    timestamp,
                    timestamp,
                )
                for degree in degrees
            ],
        )

        projected_rows = 0
        for record in establishments.values():
            latitude = record["latitude"]
            longitude = record["longitude"]
            geocode_status = "resolved" if latitude is not None and longitude is not None else "pending"
            geocode_score = 1.0 if geocode_status == "resolved" else None
            geocode_provider = "source_coordinates" if geocode_status == "resolved" else None
            raw_address = ", ".join(
                part
                for part in [record["address_line_1"], record["postal_code"], record["city"]]
                if isinstance(part, str) and part
            )

            connection.execute(
                """
                INSERT INTO poi (
                    source_name, source_record_id, layer_id, name, display_name, address_line_1, address_line_2,
                    postal_code, city, department_code, region, country_code, finess, rpps, adeli, siret,
                    phone, website, opening_hours, pharmacy_establishment_id, pharmacist_count, pharmacy_type,
                    latitude, longitude, geocode_status, geocode_score, geocode_provider, raw_address,
                    normalized_address, is_active, last_seen_at_utc, created_at_utc, updated_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
                """,
                (
                    PHARMACY_SOURCE_NAME,
                    record["establishment_id"],
                    PHARMACY_LAYER_ID,
                    record["display_name"],
                    record["display_name"],
                    record["address_line_1"],
                    None,
                    record["postal_code"],
                    record["city"],
                    record["department"],
                    record["region"],
                    "FR",
                    None,
                    None,
                    None,
                    record["siret"],
                    record["phone"],
                    record["website"],
                    record["opening_hours"],
                    record["establishment_id"],
                    counts_by_establishment.get(str(record["establishment_id"]), 0),
                    record["establishment_type"],
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
                ),
            )
            projected_rows += 1

        connection.commit()

    rebuild_poi_rtree()
    return PharmacyDirectoryImportSummary(
        files_detected=len(selected_files),
        used_specialized_directory=True,
        establishments_imported=len(establishments),
        pharmacists_imported=len(pharmacists),
        activities_imported=len(activities),
        degrees_imported=len(degrees),
        rows_rejected=rows_rejected,
        poi_rows_projected=projected_rows,
    )


def discover_pharmacy_files(directory: Path) -> dict[str, Path]:
    candidates: dict[str, list[Path]] = {key: [] for key in REQUIRED_PHARMACY_CATEGORIES}
    for path in directory.glob("*.csv"):
        category = _classify_filename(path.name)
        if category is not None:
            candidates[category].append(path)

    if not all(candidates[category] for category in REQUIRED_PHARMACY_CATEGORIES):
        return {}

    return {category: _select_preferred_file(paths) for category, paths in candidates.items()}


def _upsert_pharmacy_layer(connection: sqlite3.Connection, timestamp: str) -> None:
    metadata = DEFAULT_LAYER_METADATA[PHARMACY_LAYER_ID]
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
            PHARMACY_LAYER_ID,
            metadata["label"],
            metadata["category"],
            metadata["priority"],
            metadata["color"],
            metadata["visible_by_default"],
            timestamp,
        ),
    )


def _reset_pharmacy_domain(connection: sqlite3.Connection) -> None:
    connection.execute("DELETE FROM pharmacist_degree")
    connection.execute("DELETE FROM pharmacist_activity")
    connection.execute("DELETE FROM pharmacist")
    connection.execute("DELETE FROM pharmacy_establishment")
    connection.execute("DELETE FROM poi WHERE layer_id = ?", (PHARMACY_LAYER_ID,))


def _record_source_file(connection: sqlite3.Connection, category: str, path: Path, timestamp: str) -> None:
    file_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    row_count = len(_read_csv_rows(path))
    connection.execute(
        """
        INSERT INTO poi_source_file (layer_id, file_name, file_path, file_hash, imported_at_utc, row_count, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, 'success', ?)
        """,
        (PHARMACY_LAYER_ID, path.name, str(path), file_hash, timestamp, row_count, f"category={category}"),
    )


def _read_csv_rows(path: Path) -> list[dict[str, str | None]]:
    text = _decode_csv_text(path.read_bytes())
    rows_text, delimiter = _prepare_csv_text(text)
    if not rows_text.strip():
        return []
    reader = csv.DictReader(io.StringIO(rows_text), delimiter=delimiter)
    rows: list[dict[str, str | None]] = []
    for row in reader:
        normalized_row = _normalize_csv_row(row)
        if any(value is not None for value in normalized_row.values()):
            rows.append(normalized_row)
    return rows


def _normalize_csv_row(row: dict[str, str | None]) -> dict[str, str | None]:
    normalized_row: dict[str, str | None] = {}
    for key, value in row.items():
        cleaned_key = _clean_text(key)
        if cleaned_key is None:
            continue
        normalized_row[_normalize_key(cleaned_key)] = _clean_text(value)
    return normalized_row


def _normalize_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = []
    previous_was_separator = False
    for character in ascii_value.lower():
        if character.isalnum():
            cleaned.append(character)
            previous_was_separator = False
            continue
        if not previous_was_separator:
            cleaned.append("_")
            previous_was_separator = True
    result = "".join(cleaned).strip("_")
    return result.replace("__", "_")


def _classify_filename(file_name: str) -> str | None:
    normalized = _normalize_key(file_name)
    if "etablissement" in normalized:
        return "etablissements"
    if "pharmacien" in normalized:
        return "pharmaciens"
    if "activite" in normalized:
        return "activites"
    if "diplome" in normalized:
        return "diplomes"
    return None


def _select_preferred_file(paths: list[Path]) -> Path:
    ranked_paths = sorted(paths, key=_candidate_priority, reverse=True)
    if len(ranked_paths) > 1 and _candidate_rank_key(ranked_paths[0]) == _candidate_rank_key(ranked_paths[1]):
        raise ValueError(f"Unable to choose between competing pharmacy exports: {ranked_paths[0].name} and {ranked_paths[1].name}")
    return ranked_paths[0]


def _candidate_priority(path: Path) -> tuple[int, int, str]:
    rank_key = _candidate_rank_key(path)
    return (rank_key[0], rank_key[1], path.name)


def _candidate_rank_key(path: Path) -> tuple[int, int]:
    stem = _normalize_key(path.stem)
    timestamp_value = 0
    digits = "".join(character for character in stem if character.isdigit())
    if len(digits) >= 14:
        timestamp_value = int(digits[:14])
    return (timestamp_value, path.stat().st_mtime_ns)


def _pick_first(row: dict[str, str | None], *keys: str) -> str | None:
    canonicalized_row = {_canonical_lookup_key(row_key): value for row_key, value in row.items()}
    for key in keys:
        value = row.get(key)
        if value:
            return value.strip()
        value = canonicalized_row.get(_canonical_lookup_key(key))
        if value:
            return value.strip()
    return None


def _decode_csv_text(raw: bytes) -> str:
    last_error: UnicodeError | None = None
    for encoding in _candidate_encodings(raw):
        try:
            text = raw.decode(encoding)
        except UnicodeError as exc:
            last_error = exc
            continue
        cleaned = _clean_text(text)
        if cleaned:
            return cleaned

    if last_error is not None:
        raise last_error
    return ""


def _candidate_encodings(raw: bytes) -> list[str]:
    candidates: list[str] = []
    if raw.startswith(b"\xff\xfe"):
        candidates.append("utf-16")
    elif raw.startswith(b"\xfe\xff"):
        candidates.append("utf-16")
    elif _looks_like_utf16_le(raw):
        candidates.extend(["utf-16-le", "utf-16"])
    elif _looks_like_utf16_be(raw):
        candidates.extend(["utf-16-be", "utf-16"])

    for encoding in CSV_ENCODINGS:
        if encoding not in candidates:
            candidates.append(encoding)
    return candidates


def _looks_like_utf16_le(raw: bytes) -> bool:
    sample = raw[:256]
    return len(sample) >= 8 and sample[1::2].count(0) > max(4, len(sample[1::2]) // 3)


def _looks_like_utf16_be(raw: bytes) -> bool:
    sample = raw[:256]
    return len(sample) >= 8 and sample[::2].count(0) > max(4, len(sample[::2]) // 3)


def _prepare_csv_text(text: str) -> tuple[str, str]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return "", ";"

    delimiter: str | None = None
    first_line = lines[0].strip()
    if first_line.lower().startswith("sep="):
        delimiter = first_line[4:5] or ";"
        lines = lines[1:]

    sample = "\n".join(lines[:10])
    if delimiter is None:
        try:
            delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
        except csv.Error:
            delimiter = ";"

    return "\n".join(lines), delimiter


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.replace("\ufeff", "").replace("\x00", "").strip()
    return cleaned or None


def _canonical_lookup_key(value: str | None) -> str:
    if value is None:
        return ""
    return _normalize_key(value).replace("_", "")


def _parse_bool(value: str | None) -> bool:
    if value is None:
        return False
    return _canonical_text(value) in {"1", "oui", "yes", "true", "vrai", "principale", "principal"}


def _canonical_text(value: str | None) -> str:
    if not value:
        return ""
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_value.lower().split())


def _parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    normalized = value.replace(",", ".").strip()
    if not normalized:
        return None
    return float(normalized)


def _try_parse_float(value: str | None) -> float | None:
    try:
        return _parse_float(value)
    except ValueError:
        return None
