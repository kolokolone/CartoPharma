# AGENTS.md

## Scope
This file is the frontend-local guide for agents working in `frontend/`.
It supplements `../AGENTS.md`; when both apply, keep the more specific frontend rule.
Prefer repository evidence over generic Next.js or React advice.

## Stack
- Next.js 16 App Router with React 19
- TypeScript with `strict: true`
- Tailwind CSS v4, React Query, Leaflet/React Leaflet
- ESLint 9 flat config via `eslint-config-next/core-web-vitals`
- npm with `package-lock.json`

## Rule files and inherited guidance
- This frontend folder did not already contain its own `AGENTS.md`.
- Repo-wide guidance exists in `../AGENTS.md`.
- No `.cursorrules` file was found in `frontend/`.
- No `.cursor/rules/` directory was found in `frontend/`.
- No `.github/copilot-instructions.md` file was found in `frontend/`.
- `../docs/style-frontend-ui.md` is normative for shell, navigation, page metadata, and page composition.

## Important paths
- `package.json`: canonical scripts
- `tsconfig.json`: strict TS config and `@/* -> ./src/*`
- `next.config.ts` + `.env.example`: backend routing and env vars
- `src/app/`: layout, pages, route handlers, global CSS
- `src/components/`, `src/hooks/`, `src/lib/api.ts`, `src/types/api.ts`: UI, data hooks, API client, and transport types

## Commands
Run all frontend commands from `frontend/`.

```bash
npm ci
npm run dev
npm run lint
npm run typecheck
npm run build
npm start
```

## Tests and single-test guidance
There is currently **no frontend test runner configured**.
Verified facts:
- `package.json` has no `test` script
- no `vitest.config.*`, `jest.config.*`, `playwright.config.*`, or `cypress.config.*`
- no `*.test.*` or `*.spec.*` files under `src/`

Implications:
- do not claim frontend tests were run unless you first add a test runner
- there is currently no frontend single-test command
- the validation baseline is lint + typecheck + build

Useful targeted validation:

```bash
npx eslint src/path/to/file.tsx
npm run typecheck
npm run build
```

## Environment and runtime behavior
- `NEXT_PUBLIC_API_URL` is optional and used in `src/lib/api.ts`.
- `INTERNAL_API_URL` defaults to `http://127.0.0.1:8000` and is used in `next.config.ts` and `src/app/api/v1/indexing/rebuild-poi/route.ts`.
- Browser-side API calls default to `/api/v1` unless an explicit production URL is configured.
- Preserve trailing slash normalization behavior in API URL helpers.

## Imports and file boundaries
- Follow the local grouping pattern:
  1. framework/library imports
  2. blank line
  3. internal `@/...` imports
  4. blank line
  5. relative imports
- Use `import type` for type-only imports.
- Prefer the `@/...` alias over long relative traversals.
- Keep immediate-sibling relative imports when that is already the local pattern.

## Formatting
- Use single quotes.
- Keep semicolons.
- Keep trailing commas in multiline objects, arrays, and argument lists.
- No Prettier config is present, so match the surrounding file exactly.

## TypeScript conventions
- Preserve strict types; `allowJs` is disabled.
- Prefer explicit prop and object types for public interfaces.
- Prefer unions, tuples, and builtin generics (`string | null`, `Partial<...>`).
- Keep backend payload types in `src/types/api.ts` aligned with the backend contract.
- Preserve snake_case transport fields like `show_labels`, `visible_by_default`, and `pharmacy_establishment_id`.
- Avoid `any` and avoid broad weakening casts.
- If a cast is unavoidable, keep it narrow and close to the boundary.

## Naming conventions
- React components: `PascalCase`
- Component files: usually `PascalCase.tsx`
- Hooks: `useSomething` in `camelCase`
- Local functions and variables: `camelCase`
- Shared constants: `SCREAMING_SNAKE_CASE` only when they are true constants, e.g. `API_BASE_URL`, `NAV_ITEMS`
- App Router modules follow Next naming: `page.tsx`, `layout.tsx`, `route.ts`

## React and Next.js patterns
- Add `'use client';` only to files that actually need client hooks, state, browser APIs, or React Query.
- App Router page modules usually default-export the page component.
- Keep the root composition `Providers -> AppShell -> page content` from `src/app/layout.tsx`.
- Keep page titles/subtitles/container metadata in `src/components/layout/page-metadata.tsx`, not duplicated in pages.
- Keep global navigation in `src/components/layout/nav.ts`.
- Reuse `PageContainer`, `TopHeader`, `Sidebar`, and existing UI primitives before creating alternatives.
- Preserve the dynamic import boundary for Leaflet-heavy code (`CartoMap.tsx` -> `CartoMapLeaflet`).

## Data fetching and state
- Keep browser API access centralized in `src/lib/api.ts`.
- Wrap backend interactions in React Query hooks under `src/hooks/`.
- Define stable query keys as local constants when reused.
- Use `invalidateQueries` after successful mutations where the current code already follows that pattern.
- Preserve existing debounce and derived-state patterns unless there is a concrete bug.

## UI and styling rules
- Prefer tokens from `src/app/globals.css` (`background`, `foreground`, `card`, `border`, `muted`, `primary`, etc.).
- Use `cn()` from `src/lib/utils.ts` for class composition.
- Reuse primitives from `src/components/ui/` before adding new building blocks.
- Respect `../docs/style-frontend-ui.md`:
  - do not bypass `AppShell` for standard pages
  - do not duplicate the global header inside pages
  - do not hardcode global navigation in page files
  - keep `/map` on the wide container path
- Keep the UI sober, readable, and professional.

## Accessibility and error handling
- Preserve semantic landmarks like `header`, `main`, and dialog semantics.
- Keep `aria-label` usage for icon-only controls and mobile navigation.
- Maintain Escape-to-close behavior for overlays and drawers.
- Fail explicitly at boundaries; do not silently swallow fetch failures.
- Keep frontend API errors actionable via `ApiError` when possible.
- Never use empty catches.

## Editing guidance
- If you touch API payloads, update both `src/types/api.ts` and the consuming code.
- If you touch API base URL logic, inspect both `src/lib/api.ts` and `src/app/api/v1/indexing/rebuild-poi/route.ts`.
- If you touch shell, navigation, headers, or metadata, also review `../docs/style-frontend-ui.md`.
- If you touch shared variants or utility class composition, inspect `src/components/ui/*` and `src/lib/utils.ts` first.
- Do not edit generated output under `.next/`.

## Validation checklist
For frontend code changes, run:

```bash
npm run lint
npm run typecheck
npm run build
```

For targeted iteration, also run `npx eslint path/to/file.tsx` on the touched file.
Because no frontend tests exist yet, lint + typecheck + build are the current required validation baseline.

## Agent reminders
- Inspect neighboring files before editing and mirror their local conventions.
- Keep changes surgical; avoid broad refactors unless required.
- Do not invent repository rules that are not backed by the codebase.
- If a frontend test runner is added later, update this file with the exact suite and single-test commands.
