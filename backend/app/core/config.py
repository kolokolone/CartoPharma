from __future__ import annotations

import os
from pathlib import Path


APP_NAME = "CartoPharma API"
APP_VERSION = "0.1.4"


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def get_data_dir() -> Path:
    raw = os.getenv("CARTOPHARMA_DATA_DIR")
    if raw:
        return Path(raw)
    return get_project_root() / "data"


def get_database_path() -> Path:
    raw = os.getenv("CARTOPHARMA_DATABASE_URL", "").strip()
    if raw.startswith("sqlite:///"):
        return Path(raw.replace("sqlite:///", "", 1))
    return get_data_dir() / "cartopharma.sqlite"


def get_poi_database_path() -> Path:
    raw = os.getenv("CARTOPHARMA_POI_DATABASE_URL", "").strip()
    if raw.startswith("sqlite:///"):
        return Path(raw.replace("sqlite:///", "", 1))
    return get_data_dir() / "poi.sqlite"


def get_csv_dir() -> Path:
    return get_data_dir() / "csv"


def get_logs_dir() -> Path:
    return get_data_dir() / "logs"


def ensure_runtime_dirs() -> None:
    for path in [
        get_data_dir(),
        get_csv_dir(),
        get_data_dir() / "layers",
        get_data_dir() / "tmp",
        get_logs_dir(),
    ]:
        path.mkdir(parents=True, exist_ok=True)


def get_cors_origins() -> list[str]:
    raw = os.getenv("CARTOPHARMA_CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def is_batch_geocoding_enabled() -> bool:
    raw = os.getenv("CARTOPHARMA_ENABLE_BATCH_GEOCODING", "1").strip().lower()
    return raw not in {"0", "false", "no", "off"}


def get_geocoding_api_base_url() -> str:
    raw = os.getenv("CARTOPHARMA_GEOCODING_API_URL", "https://data.geopf.fr/geocodage").strip()
    return raw.rstrip("/")


def get_geocoding_batch_size() -> int:
    raw = os.getenv("CARTOPHARMA_GEOCODING_BATCH_SIZE", "5000").strip()
    try:
        value = int(raw)
    except ValueError:
        return 5000
    return max(1, min(value, 200_000))
