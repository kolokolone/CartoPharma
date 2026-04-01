export type LayerId = string;

export type MapBbox = [number, number, number, number];

export type SettingsResponse = {
  country_scope: 'FRANCE';
  theme: 'light' | 'dark' | 'system';
  show_labels: boolean;
  compact_controls: boolean;
};

export type SettingsPatch = Partial<{
  theme: 'light' | 'dark' | 'system';
  show_labels: boolean;
  compact_controls: boolean;
}>;

export type LayerDefinition = {
  id: LayerId;
  label: string;
  category: string;
  color: string;
  priority: number;
  visible_by_default: boolean;
  source_status?: string | null;
  updated_at_utc?: string | null;
};

export type LayersCatalogResponse = {
  country_scope: 'FRANCE';
  layers: LayerDefinition[];
};

export type GeoPointFeature = {
  type: 'Feature';
  geometry: {
    type: 'Point';
    coordinates: [number, number];
  };
  properties: {
    id: string;
    layer: LayerId;
    name: string;
    city: string;
    layer_label?: string | null;
    layer_color?: string | null;
    display_name?: string | null;
    address_line_1?: string | null;
    address_line_2?: string | null;
    postal_code?: string | null;
    department_code?: string | null;
    region?: string | null;
    country_code?: string | null;
    phone?: string | null;
    website?: string | null;
    opening_hours?: string | null;
    source_name?: string | null;
    source_record_id?: string | null;
    geocode_status?: string | null;
    geocode_score?: number | null;
    geocode_provider?: string | null;
    finess?: string | null;
    rpps?: string | null;
    adeli?: string | null;
    siret?: string | null;
    pharmacy_establishment_id?: string | null;
    pharmacist_count?: number | null;
    pharmacy_type?: string | null;
    last_updated_at?: string | null;
  };
};

export type GeoPointCollectionResponse = {
  type: 'FeatureCollection';
  features: GeoPointFeature[];
};

export type ReindexPoiResponse = {
  status: 'success';
  database: string;
  files_detected: number;
  generic_files_processed: number;
  pharmacy_files_detected: number;
  used_specialized_pharmacy_directory: boolean;
  generic_rows_imported: number;
  pharmacies_imported: number;
  pharmacists_imported: number;
  activities_imported: number;
  degrees_imported: number;
  rows_rejected: number;
  poi_rows_rebuilt: number;
  geocoded_resolved: number;
  geocoded_pending: number;
  duration_ms: number;
};

export type PharmacyActivityResponse = {
  function_label?: string | null;
  registration_date?: string | null;
  section_code?: string | null;
  is_primary_activity: boolean;
};

export type PharmacyDegreeResponse = {
  degree_label?: string | null;
  degree_date?: string | null;
  university?: string | null;
  region?: string | null;
};

export type PharmacistDetailResponse = {
  rpps: string;
  title?: string | null;
  last_name?: string | null;
  first_name?: string | null;
  first_registration_date?: string | null;
  activities: PharmacyActivityResponse[];
  degrees: PharmacyDegreeResponse[];
};

export type PharmacyDetailResponse = {
  establishment_id: string;
  establishment_type?: string | null;
  display_name: string;
  legal_name?: string | null;
  address_line_1?: string | null;
  postal_code?: string | null;
  city?: string | null;
  department?: string | null;
  region?: string | null;
  phone?: string | null;
  fax?: string | null;
  website?: string | null;
  opening_hours?: string | null;
  siret?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  last_updated_at?: string | null;
  is_favorite: boolean;
  pharmacist_count: number;
  pharmacists: PharmacistDetailResponse[];
};

export type FavoriteStatusResponse = {
  establishment_id: string;
  is_favorite: boolean;
};

export type PharmacyNearbyPoiItemResponse = {
  id: string;
  label: string;
  secondary_label?: string | null;
  layer_id: string;
  layer_label: string;
  category: string;
  city?: string | null;
  distance_m: number;
  latitude: number;
  longitude: number;
  target_href: string;
  pharmacy_establishment_id?: string | null;
};

export type PharmacyNearbyPoiResponse = {
  establishment_id: string;
  radius_m: number;
  total_count: number;
  items: PharmacyNearbyPoiItemResponse[];
};

export type SearchResultType = 'pharmacy' | 'poi' | 'city' | 'layer';

export type SearchResultResponse = {
  id: string;
  result_type: SearchResultType;
  label: string;
  secondary_label?: string | null;
  target_href: string;
  pharmacy_establishment_id?: string | null;
  layer_id?: string | null;
  layer_label?: string | null;
  city?: string | null;
};

export type SearchResponse = {
  query: string;
  kind: 'suggestions' | 'results';
  total_count: number;
  results: SearchResultResponse[];
};
