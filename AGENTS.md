# AGENTS.md

## Purpose
This file gives coding agents the repo-specific rules for working safely in CartoPharma.
Prefer observed repository patterns over generic framework defaults.

## Repository shape
- `backend/`: FastAPI application, SQLite access, import/rebuild services, backend scripts.
- `backend/tests/`: Python `unittest` coverage for the POI pipeline.
- `frontend/`: Next.js App Router app with TypeScript, React Query, Leaflet, Tailwind CSS v4.
- `data/`: runtime SQLite databases, logs, CSV inputs, generated artifacts.
- `docs/`: internal runbooks and style references.
- `.github/workflows/ci-cd.yml`: canonical CI validation commands.

## Existing agent/editor rules
- No root `AGENTS.md` existed before this file.
- No `.cursorrules` file was found.
- No `.cursor/rules/` directory was found.
- No `.github/copilot-instructions.md` file was found.
- `docs/style-frontend-ui.md` is the strongest local UI instruction source; follow it for shell, navigation, and page composition.
- `docs/` directory for overall instructions of the codebase

## Environment and working directories
- Python dependencies: `backend/requirements.txt`.
- Frontend dependencies and scripts: `frontend/package.json`.
- TypeScript is strict and uses the `@/* -> frontend/src/*` alias.
- Runtime data defaults to `data/` unless overridden by env vars.
- Run backend Python commands from `backend/`, frontend npm commands from `frontend/`, Docker commands from repo root.

## Build, lint, typecheck, and test commands

### Frontend (`frontend/`)
```bash
npm ci
npm run lint
npm run typecheck
npm run build
npm run dev
```
- `lint` runs `eslint .`.
- `typecheck` runs `tsc --noEmit`.
- `build` runs `next build`.
- No frontend unit-test runner is currently configured in `package.json`.

### Backend
CI validates the backend from repo root with:
```bash
pip install -r backend/requirements.txt
python -m compileall backend/app
```
From `backend/`, run the test suite with:
```bash
python -m unittest tests.test_poi_pipeline
```
Run a single backend test class:
```bash
python -m unittest tests.test_poi_pipeline.PoiPipelineTests
```
Run a single backend test method:
```bash
python -m unittest tests.test_poi_pipeline.PoiPipelineTests.test_routes_expose_enriched_pharmacy_payloads
```
Start the backend locally from `backend/`:
```bash
python -m uvicorn app.main:app --reload
```

### Full CI-equivalent validation
From repo root:
```bash
pip install -r backend/requirements.txt
python -m compileall backend/app
cd frontend && npm ci
cd frontend && npm run lint
cd frontend && npm run typecheck
cd frontend && npm run build
docker build -t cartopharma:ci .
```
For agents that support per-command working directories, prefer separate commands instead of chained `cd` sequences.

## Fast local smoke commands
- Windows full stack: `run_win.bat`
- Windows prerequisites smoke test: `run_win.bat --smoke`
- Backend only: `start_backend.bat`
- Frontend only: `start_frontend.bat`
- Linux/macOS dev mode: `./run_linux.sh --dev`
- Linux/macOS Docker mode: `./run_linux.sh --docker`

## Backend code style
- Use Python 3.12-compatible syntax and keep `from __future__ import annotations` where already present.
- Group imports as standard library, third-party, then local `app.*`, with blank lines between groups.
- Use `snake_case` for functions, variables, modules, and non-class constants.
- Use `PascalCase` for Pydantic models, exceptions, and classes.
- Prefer explicit return annotations on public functions and route handlers.
- Prefer `str | None`, `list[str]`, and other builtin generics over `Optional`/`List`.
- Use `Literal[...]` and `Field(...)` when API constraints are known.
- Keep API models in the `backend/app/models/schemas.py` style: typed fields, sensible defaults, minimal untyped payloads.
- Keep routes thin; move business logic into services/repositories.
- Raise `HTTPException` for request-validation failures close to the route layer.
- Chain exceptions when converting parse errors (`raise ... from exc`) as in `_parse_bbox`.
- Do not swallow exceptions silently; either log them or re-raise with context.
- Follow the structured logging pattern from `backend/app/main.py`, including `request_id` when available.
- Preserve SQLite- and CSV-driven behavior; many flows depend on runtime files and rebuild steps.

## Backend testing conventions
- Tests use `unittest`, not `pytest`.
- Test files live under `backend/tests/`.
- Test classes use `PascalCase` and inherit from `unittest.TestCase`.
- Test methods start with `test_` and describe behavior in full phrases.
- Filesystem tests usually create temporary runtime dirs and set `CARTOPHARMA_DATA_DIR`.
- Mock external HTTP calls with `unittest.mock.patch` and `Mock`.

## Frontend code style
- Use TypeScript throughout `frontend/src/`.
- Group imports as framework/React, third-party, internal `@/...`, then relative imports.
- Use `import type` for type-only imports when possible.
- Prefer single quotes and semicolons, matching the repo.
- Use `PascalCase` for React components and component filenames.
- Use `camelCase` for helpers, variables, and hook internals; hook names must start with `use`.
- Prefer small explicit prop types such as `type AppShellProps = { ... }`.
- Prefer narrow string unions and tuple types for domain data.
- Avoid `any`, loose casts, and weakening strict-mode types.
- Keep API access centralized in `frontend/src/lib/api.ts`.
- Keep React Query usage in hooks (`frontend/src/hooks/*`) when possible.
- Use `cn()` from `frontend/src/lib/utils.ts` for class composition.
- Reuse existing UI primitives in `frontend/src/components/ui/` before adding new ones.
- Preserve existing accessibility patterns such as `aria-label`, `aria-current`, dialog semantics, and Escape handling.

## Frontend UI rules from local docs
These come from `docs/style-frontend-ui.md` and should be treated as normative:
- Standard app pages must stay inside `AppShell` via `frontend/src/app/layout.tsx`.
- Do not recreate a page-local global header or root container.
- Global navigation source of truth is `frontend/src/components/layout/nav.ts`.
- Page title/subtitle/container metadata source of truth is `frontend/src/components/layout/page-metadata.tsx`.
- `/map` uses a `wide` container.
- Shared page spacing should come from `PageContainer`.
- Prefer design tokens from `frontend/src/app/globals.css` over hardcoded colors.
- Keep the UI sober, readable, and professional.

## Naming and data-shape conventions
- Backend and frontend API payloads intentionally use snake_case; do not auto-convert them to camelCase unless the whole path is updated consistently.
- Keep version strings aligned across backend and frontend metadata when releasing.
- Preserve pharmacy vocabulary already used in the models: `pharmacy_establishment_id`, `pharmacist_count`, `pharmacy_type`.

## Error handling expectations
- Prefer explicit, typed failures over silent fallback logic.
- Validate external input at boundaries.
- Return useful HTTP 422 messages for malformed request parameters.
- Keep frontend API errors actionable; the existing pattern uses a dedicated `ApiError` with HTTP status.
- Never hide fetch or parsing failures with empty catches.

## Agent workflow expectations
- Before editing, inspect neighboring files and match their local style.
- If touching frontend shell/navigation/header behavior, also read `docs/style-frontend-ui.md`.
- If changing API payloads, update backend schemas and frontend `src/types/api.ts` together.
- If changing route behavior, run the relevant `unittest` target in `backend/tests/test_poi_pipeline.py`.
- If changing frontend TypeScript or components, run `npm run lint`, `npm run typecheck`, and `npm run build` from `frontend/`.
- Prefer minimal, surgical changes over broad refactors.
- Do not edit generated/runtime directories such as `frontend/.next/` or files under `data/logs/`.
