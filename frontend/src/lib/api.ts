import type {
  FavoriteStatusResponse,
  GeoPointCollectionResponse,
  LayerId,
  LayersCatalogResponse,
  MapBbox,
  PharmacyDetailResponse,
  PharmacyNearbyPoiResponse,
  ReindexPoiResponse,
  SearchResponse,
  SettingsPatch,
  SettingsResponse,
} from '@/types/api';

function resolveApiBaseUrl() {
  const explicitRaw = process.env.NEXT_PUBLIC_API_URL;
  const explicit = explicitRaw ? explicitRaw.trim() : '';

  if (process.env.NODE_ENV === 'production' && explicit.length > 0) {
    return explicit;
  }

  return '/api/v1';
}

const API_BASE_URL = resolveApiBaseUrl().replace(/\/+$/, '');

function buildUrl(endpoint: string) {
  const ep = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${API_BASE_URL}${ep}`;
}

class ApiError extends Error {
  public status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(buildUrl(endpoint), {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers ?? {}),
    },
  });

  if (!response.ok) {
    const data = (await response.json().catch(() => ({}))) as { detail?: string };
    throw new ApiError(data.detail ?? `API error ${response.status}`, response.status);
  }

  return response.json() as Promise<T>;
}

export const settingsApi = {
  get: async () => apiRequest<SettingsResponse>('/settings'),
  patch: async (payload: SettingsPatch) =>
    apiRequest<SettingsResponse>('/settings', {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),
};

export const layersApi = {
  list: async () => apiRequest<LayersCatalogResponse>('/layers'),
  points: async (layers: LayerId[], bbox?: MapBbox | null) => {
    const sp = new URLSearchParams();
    layers.forEach((layerId) => sp.append('layers', layerId));
    if (bbox) {
      sp.set('bbox', bbox.join(','));
    }
    const suffix = sp.toString();
    return apiRequest<GeoPointCollectionResponse>(`/layers/points${suffix ? `?${suffix}` : ''}`);
  },
};

export const indexingApi = {
  rebuildPoi: async () => apiRequest<ReindexPoiResponse>('/indexing/rebuild-poi', { method: 'POST' }),
};

export const searchApi = {
  search: async (query: string, kind: 'suggestions' | 'results', limit = 20) => {
    const sp = new URLSearchParams();
    sp.set('q', query);
    sp.set('kind', kind);
    sp.set('limit', String(limit));
    return apiRequest<SearchResponse>(`/search?${sp.toString()}`);
  },
};

export const pharmaciesApi = {
  detail: async (establishmentId: string) => apiRequest<PharmacyDetailResponse>(`/pharmacies/${establishmentId}`),
  nearbyPoi: async (establishmentId: string, radiusM: number) => {
    const sp = new URLSearchParams();
    sp.set('radius_m', String(radiusM));
    return apiRequest<PharmacyNearbyPoiResponse>(`/pharmacies/${establishmentId}/nearby-poi?${sp.toString()}`);
  },
  favoriteStatus: async (establishmentId: string) => apiRequest<FavoriteStatusResponse>(`/pharmacies/${establishmentId}/favorite`),
  putFavorite: async (establishmentId: string) =>
    apiRequest<FavoriteStatusResponse>(`/pharmacies/${establishmentId}/favorite`, {
      method: 'PUT',
    }),
  deleteFavorite: async (establishmentId: string) =>
    apiRequest<FavoriteStatusResponse>(`/pharmacies/${establishmentId}/favorite`, {
      method: 'DELETE',
    }),
};
