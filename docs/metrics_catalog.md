# CartoPharma - Catalogue API / donnees

## Backend

### `GET /`
- `message`
- `version`
- `status`

### `GET /health`
- `status`
- `scope`
- `database`

### `GET /api/v1/settings`
- `country_scope`
- `theme`
- `show_labels`
- `compact_controls`

### `PATCH /api/v1/settings`
- meme schema de retour que `GET /api/v1/settings`

### `GET /api/v1/layers`
- `country_scope`
- `layers[]`
  - `id`
  - `label`
  - `category`
  - `color`
  - `priority`
  - `visible_by_default`

### `GET /api/v1/layers/points`
- `type`
- `features[]`
  - `geometry.coordinates`
  - `properties.id`
  - `properties.layer`
  - `properties.name`
  - `properties.city`
