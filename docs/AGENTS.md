# AGENTS.md
## Scope
This file is the docs-local guide for agents working in `Cartopharma/docs/`.
It supplements `../AGENTS.md`; when both apply, keep the more specific docs rule.
Prefer repository evidence over generic framework or documentation advice.

## Inherited rules and local sources
- Parent repo guide: `../AGENTS.md`
- Frontend guide: `../frontend/AGENTS.md`
- Backend guide: `../backend/AGENTS.md`
- UI source of truth: `style-frontend-ui.md`
- README contract: `readme-doc.md`
- Docs follow-up checklist: `documentation_update_runbook.md`
- No `.cursorrules`, `.cursor/rules/`, or `.github/copilot-instructions.md` were found

## What belongs in `docs/`
Keep runbooks, implementation notes, UI references, and agent guidance here.
Do not use `docs/` for generated output, copied source snapshots, or speculative features presented as shipped.

## Verify these files before documenting anything
- `../README.md`, `../.github/workflows/ci-cd.yml`, `../backend/requirements.txt`
- `../frontend/package.json`, `../frontend/eslint.config.mjs`, `../frontend/tsconfig.json`, `../frontend/next.config.ts`
- `style-frontend-ui.md`

## Working directories
- Backend commands run from `../backend/`
- Frontend commands run from `../frontend/`
- Docker commands run from repo root `../`
- Docs are edited from `docs/`, but every factual claim must be checked against the owning file

## Build, lint, typecheck, and test commands
### Frontend (`../frontend/`)
```bash
npm ci
npm run dev
npm run lint
npm run typecheck
npm run build
npm start
```
- `lint` = `eslint .`
- `typecheck` = `tsc --noEmit`
- `build` = `next build`

### Frontend single-test reality
There is currently no frontend test runner configured.
Observed facts:
- `../frontend/package.json` has no `test` script
- no `vitest`, `jest`, `playwright`, or `cypress` config was found
- no `*.test.*` or `*.spec.*` files were found under `../frontend/src/`

So there is no frontend single-test command today. Use targeted lint plus full typecheck/build instead:
```bash
npx eslint src/path/to/file.tsx
npm run typecheck
npm run build
```

### Backend (`../backend/`)
```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
python -m compileall app scripts tests
python -m unittest tests.test_poi_pipeline
```

Single backend test commands:
```bash
python -m unittest tests.test_poi_pipeline.PoiPipelineTests
python -m unittest tests.test_poi_pipeline.PoiPipelineTests.test_routes_expose_enriched_pharmacy_payloads
```

Useful backend maintenance scripts:
```bash
python scripts/build_poi_database.py
python scripts/import_poi_csv.py
python scripts/geocode_poi.py
```

### CI-equivalent validation from repo root
```bash
pip install -r backend/requirements.txt
python -m compileall backend/app
cd frontend && npm ci
cd frontend && npm run lint
cd frontend && npm run typecheck
cd frontend && npm run build
docker build -t cartopharma:ci .
```
If your tool supports per-command working directories, prefer separate commands over chained `cd` sequences.

## Launch helpers
- Windows: `../run_win.bat`, `../run_win.bat --smoke`, `../start_backend.bat`, `../start_frontend.bat`
- Linux/macOS: `../run_linux.sh --dev`, `../run_linux.sh --docker`

## Code style conventions to preserve
### Shared rules
- Keep backend and frontend transport payloads in `snake_case`
- Preserve domain names already used in the codebase, including `pharmacy_establishment_id`, `pharmacist_count`, and `pharmacy_type`
- Prefer explicit failures over silent fallback logic
- Never hide parsing, fetch, or request failures with empty catches
- Match the surrounding file before introducing a new pattern

### Backend conventions observed
- Use Python 3.12-compatible syntax and keep `from __future__ import annotations` where already present
- Group imports as standard library, third-party, then local `app.*`; prefer absolute imports like `from app.services...`
- Use `snake_case` for functions/modules/variables and `PascalCase` for classes, exceptions, dataclasses, and Pydantic models
- Use builtin generics and modern unions like `list[str]` and `Path | None`
- Keep public functions and route handlers explicitly typed, and keep routes thin with business logic in `app/services/`
- Keep API contracts in `app/models/schemas.py`; follow existing patterns such as `Field(...)`, `model_dump(exclude_unset=True)`, and `model_copy(update=...)`
- Keep SQL in multiline strings with uppercase keywords, commit SQLite writes explicitly, and use `run_in_threadpool` for heavy sync work triggered by async routes
- When converting lower-level failures, use `raise ... from exc`, and preserve request logging with `request_id` from `app/main.py`

### Backend testing conventions observed
- Tests use `unittest`, not `pytest`
- Current test module: `../backend/tests/test_poi_pipeline.py`
- Test classes inherit from `unittest.TestCase`
- Test methods start with `test_` and describe behavior clearly
- Filesystem-heavy tests use `TemporaryDirectory` and temporary `CARTOPHARMA_DATA_DIR`
- Mock external calls with `unittest.mock.patch` and `Mock`

### Frontend conventions observed
- Use TypeScript throughout `../frontend/src/`; `strict` is enabled and `allowJs` is false
- Prefer `import type` for type-only imports
- Group imports as framework/library, internal `@/...`, then relative imports
- Prefer the `@/* -> ./src/*` alias over long relative traversals
- Use single quotes, semicolons, and trailing commas in multiline structures
- Use `PascalCase` for React components and most component filenames; use `camelCase` for helpers, locals, and hook internals, and keep hook names prefixed with `use`
- Add `'use client';` only where client features are actually needed
- Keep API access centralized in `../frontend/src/lib/api.ts`, keep backend-facing payload types aligned in `../frontend/src/types/api.ts`, and use React Query hooks in `../frontend/src/hooks/` for backend interaction
- Reuse `cn()` from `../frontend/src/lib/utils.ts` and primitives from `../frontend/src/components/ui/`
- Preserve accessibility patterns like `aria-label`, semantic `header/main/nav`, and Escape-to-close overlays

### Frontend UI rules inherited from `style-frontend-ui.md`
- Standard app pages stay inside `AppShell`
- Do not recreate a page-local global header or root container
- Global navigation lives in `../frontend/src/components/layout/nav.ts`; page title/subtitle/container metadata lives in `../frontend/src/components/layout/page-metadata.tsx`
- `/map` uses the `wide` container path, shared page spacing comes from `PageContainer`, and tokens from `../frontend/src/app/globals.css` should beat hardcoded colors
- Keep the UI sober, readable, and professional

## Docs writing rules
- Write for the repository as it exists at the current commit, not from memory or generated artifacts
- Keep `../README.md` factual, short, operational, and synchronized with real files
- Do not document `.next/`, `node_modules/`, `.venv/`, `__pycache__/`, or other local caches as normal project structure
- Separate public README content from detailed runbooks that belong in `docs/`
- Use calm, direct language; avoid marketing tone; prefer concise lists over dense paragraphs
- Use one `#` title per file, stable `##` sections, and typed code fences like `bash`, `powershell`, and `json`
- Remove duplicated statements instead of repeating them across docs

## Docs workflow expectations
- Before editing docs, inspect the real code/config file that supports each claim
- If launch instructions change, update `../README.md` using `readme-doc.md`
- If API shape or data structures change, review `metrics_catalog.md`; if frontend shell/navigation/header rules are touched, re-check `style-frontend-ui.md`
- Keep docs aligned with the current version string (`0.1.5` at the time of this file)
- Do not edit generated/runtime directories such as `../frontend/.next/` or `../data/logs/`; keep docs changes surgical and evidence-based

## Validation checklist for docs changes
- Re-read each command against `package.json`, `requirements.txt`, scripts, or workflow files
- Ensure file paths mentioned in docs actually exist
- Ensure README claims do not exceed what the current codebase implements
- If documenting frontend behavior, verify the route/component still exists
- If documenting backend behavior, verify the route/test/script still exists

## Agent reminder
Safest order: inspect code/config -> update docs -> re-check commands and paths -> keep parent and sibling AGENTS files consistent.
