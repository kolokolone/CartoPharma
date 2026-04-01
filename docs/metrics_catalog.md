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

### `POST /api/v1/indexing/rebuild-poi`
- `status`
- `database`
- `files_detected`
- `generic_files_processed`
- `pharmacy_files_detected`
- `used_specialized_pharmacy_directory`
- `generic_rows_imported`
- `pharmacies_imported`
- `pharmacists_imported`
- `activities_imported`
- `degrees_imported`
- `rows_rejected`
- `poi_rows_rebuilt`
- `geocoded_resolved`
- `geocoded_pending`
- `duration_ms`

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
  - `properties.layer_label`
  - `properties.layer_color`
  - `properties.display_name`
  - `properties.address_line_1`
  - `properties.postal_code`
  - `properties.phone`
  - `properties.website`
  - `properties.siret`
  - `properties.pharmacy_establishment_id`
  - `properties.pharmacist_count`
  - `properties.pharmacy_type`

### `GET /api/v1/pharmacies/{establishment_id}`
- `establishment_id`
- `establishment_type`
- `display_name`
- `legal_name`
- `address_line_1`
- `postal_code`
- `city`
- `department`
- `region`
- `phone`
- `fax`
- `website`
- `opening_hours`
- `siret`
- `latitude`
- `longitude`
- `last_updated_at`
- `is_favorite`
- `pharmacist_count`
- `pharmacists[]`
  - `rpps`
  - `title`
  - `last_name`
  - `first_name`
  - `first_registration_date`
  - `activities[]`
  - `degrees[]`

### `GET /api/v1/pharmacies/{establishment_id}/nearby-poi`
- `establishment_id`
- `radius_m`
- `total_count`
- `items[]`
  - `id`
  - `label`
  - `secondary_label`
  - `layer_id`
  - `layer_label`
  - `category`
  - `city`
  - `distance_m`
  - `latitude`
  - `longitude`
  - `target_href`
  - `pharmacy_establishment_id`

### `GET /api/v1/pharmacies/{establishment_id}/favorite`
### `PUT /api/v1/pharmacies/{establishment_id}/favorite`
### `DELETE /api/v1/pharmacies/{establishment_id}/favorite`
- `establishment_id`
- `is_favorite`

### `GET /api/v1/search`
- `query`
- `kind`
- `total_count`
- `results[]`
  - `id`
  - `result_type`
  - `label`
  - `secondary_label`
  - `target_href`
  - `pharmacy_establishment_id`
  - `layer_id`
  - `layer_label`
  - `city`
