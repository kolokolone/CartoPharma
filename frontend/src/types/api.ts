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
    last_updated_at?: string | null;
  };
};

export type GeoPointCollectionResponse = {
  type: 'FeatureCollection';
  features: GeoPointFeature[];
};
