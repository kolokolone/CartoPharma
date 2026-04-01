# AGENTS.md
Backend-local guide for coding agents working in `Cartopharma/backend/`.
This supplements the parent repo `../AGENTS.md` with Python/FastAPI-specific instructions.
Prefer patterns observed in this folder over generic framework defaults.

## Scope
- Applies to everything under `backend/`.
- Run commands from `backend/` unless a note says otherwise.
- This backend is a small FastAPI app using SQLite plus CSV-driven import/rebuild flows.

## Existing rules and instruction files
- Parent repo rule file exists: `../AGENTS.md`.
- No `.cursorrules` file was found in the repo.
- No `.cursor/rules/` directory was found in the repo.
- No `.github/copilot-instructions.md` file was found in the repo.
- No prior `backend/AGENTS.md` existed.

## Repository map
- `app/main.py`: FastAPI app, startup, CORS, request logging middleware.
- `app/api/router.py`: mounts versioned routes under `/api/v1`.
- `app/api/routes/`: thin route handlers for health, settings, layers, indexing, and pharmacies.
- `app/core/config.py`: env vars, runtime paths, API metadata, geocoding settings.
- `app/db/`: SQLite initialization and repository functions.
- `app/models/schemas.py`: Pydantic request/response models.
- `app/services/`: CSV import, pharmacy directory import, geocoding, POI projection logic.
- `scripts/`: CLI helpers for rebuild/import/geocoding.
- `tests/test_poi_pipeline.py`: current backend test module.

## Dependencies and tooling reality
Install deps with:
```bash
pip install -r requirements.txt
```
Current runtime dependencies are `fastapi`, `uvicorn[standard]`, `pydantic`, and `requests`.
There is no backend-local `pyproject.toml`, `setup.cfg`, `pytest.ini`, `tox.ini`, `ruff.toml`, `mypy.ini`, or Black config.
Do not claim Ruff/Black/mypy/pytest commands already exist here unless you add their config in the same change.

## Build, run, and test commands
Start the API:
```bash
python -m uvicorn app.main:app --reload
```
Syntax/smoke check:
```bash
python -m compileall app scripts tests
```
Run the full backend tests:
```bash
python -m unittest tests.test_poi_pipeline
```
Run a single test class:
```bash
python -m unittest tests.test_poi_pipeline.PoiPipelineTests
```
Run a single test method:
```bash
python -m unittest tests.test_poi_pipeline.PoiPipelineTests.test_routes_expose_enriched_pharmacy_payloads
```
Useful maintenance scripts:
```bash
python scripts/build_poi_database.py
python scripts/import_poi_csv.py
python scripts/geocode_poi.py
```
Recommended post-change validation:
```bash
python -m compileall app scripts tests
python -m unittest tests.test_poi_pipeline
```

## Lint / format / typecheck guidance
- No dedicated lint command is configured in this folder.
- No formatter command is configured in this folder.
- No static typechecker command is configured in this folder.
- Tests use `unittest`, not `pytest`.

## Environment and runtime assumptions
Relevant env vars from `app/core/config.py`:
- `CARTOPHARMA_DATA_DIR`
- `CARTOPHARMA_DATABASE_URL`
- `CARTOPHARMA_POI_DATABASE_URL`
- `CARTOPHARMA_CORS_ORIGINS`
- `CARTOPHARMA_ENABLE_BATCH_GEOCODING`
- `CARTOPHARMA_GEOCODING_API_URL`
- `CARTOPHARMA_GEOCODING_BATCH_SIZE`
Observed defaults and conventions:
- Runtime data defaults to the repo-level `data/` directory.
- Logs are written to `data/logs/`.
- Generic CSV imports come from `data/csv/`.
- Pharmacy directory imports expect `data/csv/pharmacies/`.
- Tests often override `CARTOPHARMA_DATA_DIR` with a temporary directory.

## Code style conventions observed in the backend
### Imports and modules
- Most modules start with `from __future__ import annotations`.
- Import order is standard library, third-party, then local `app.*` imports.
- Use blank lines between import groups.
- Prefer absolute imports like `from app.services...` over relative imports.

### Typing and models
- Use builtin generics and modern unions: `list[str]`, `dict[str, str | None]`, `Path | None`.
- Prefer explicit return annotations on public functions and route handlers.
- Small immutable summaries use `@dataclass(frozen=True)`.
- API contracts live in `app/models/schemas.py` as Pydantic `BaseModel` classes.
- Use `Field(...)` for constraints and `default_factory=list` for mutable defaults.
- For patch semantics, follow the existing `model_dump(exclude_unset=True)` plus `model_copy(update=...)` pattern.

### Naming and payload shapes
- Use `snake_case` for functions, variables, modules, and helpers.
- Use `PascalCase` for classes and Pydantic models.
- Use `UPPER_SNAKE_CASE` for constants.
- Keep API and DB field names in `snake_case`; do not auto-convert to camelCase.
- Preserve domain terms already used by the codebase such as `pharmacy_establishment_id`, `pharmacist_count`, and `pharmacy_type`.

### FastAPI patterns
- Route files define `router = APIRouter(...)` near the top.
- Routes stay thin: validate/parse inputs, call a service or repository, return typed models.
- Heavy sync work from an async route is wrapped with `run_in_threadpool` (`app/api/routes/indexing.py`).
- Keep `response_model=...` declarations in sync with actual payloads.
- Versioned routes are composed through `app/api/router.py` under `/api/v1`.

### SQLite and repository patterns
- Go through `connect()` or `connect_poi()` helpers; they set `sqlite3.Row` row factories.
- Use `with connect() as connection:` or `with closing(connect_poi(...)) as connection:`.
- SQL is usually written as multiline triple-quoted strings with uppercase SQL keywords.
- Commit explicitly after writes.
- Convert SQLite integer flags at the boundary with `bool(...)` or `int(...)`.
- Keep schema evolution inside initializer functions like `init_database()` / `init_poi_database()`.

### Services, errors, and logging
- Business logic belongs in `app/services/`, not inside route handlers.
- Private helper functions are consistently prefixed with `_`.
- Keep pharmacy-specific import logic in `pharmacy_directory_import.py`, separate from generic CSV import code.
- Raise `HTTPException` for route-layer validation and request failures.
- Chain meaningful parsing/concurrency errors with `raise ... from exc`.
- Do not silently swallow exceptions.
- The importer is allowed to record bad rows into `poi_import_error` instead of aborting the whole import.
- Request logging in `app/main.py` is structured and includes `request_id`; preserve that pattern.

## Testing conventions
- Tests use `unittest.TestCase` classes and `test_...` method names.
- Async route handlers are tested with `asyncio.run(...)`.
- Filesystem-heavy tests use `TemporaryDirectory` plus `addCleanup(...)`.
- External HTTP calls are mocked with `unittest.mock.patch` and `Mock`.
- If you change CSV import, geocoding, startup, or DB initialization behavior, run the full test module.

## Workflow expectations for future agents
- Read neighboring route, service, and repository files before editing.
- Keep changes surgical; this backend is intentionally small and direct.
- If you change API payloads, update `app/models/schemas.py` first, then adjust services/repositories.
- If you touch routes or import logic, verify whether `tests/test_poi_pipeline.py` needs updates.
- Do not edit `__pycache__/` contents or commit generated runtime files from `../data/`.
- If backend tooling changes materially, update this file in the same change.
