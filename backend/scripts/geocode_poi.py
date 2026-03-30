from __future__ import annotations

import json
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.poi_database import init_poi_database
from app.services.poi_geocoding import synchronize_geocode_statuses


def main() -> int:
    init_poi_database()
    report = synchronize_geocode_statuses()
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
