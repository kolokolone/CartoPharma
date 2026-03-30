export type LayerId = 'pharmacies' | 'health_professionals' | 'public_transport' | 'shops' | 'points_of_interest';

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
  };
};

export type GeoPointCollectionResponse = {
  type: 'FeatureCollection';
  features: GeoPointFeature[];
};
