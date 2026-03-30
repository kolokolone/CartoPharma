from __future__ import annotations

import json
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.poi_database import init_poi_database
from app.services.poi_import import import_csv_directory


def main() -> int:
    init_poi_database()
    summary = import_csv_directory()
    print(json.dumps(summary.__dict__, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
