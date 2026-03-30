import type {
  GeoPointCollectionResponse,
  LayerId,
  LayersCatalogResponse,
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
  points: async (layers: LayerId[]) => {
    const sp = new URLSearchParams();
    layers.forEach((layerId) => sp.append('layers', layerId));
    const suffix = sp.toString();
    return apiRequest<GeoPointCollectionResponse>(`/layers/points${suffix ? `?${suffix}` : ''}`);
  },
};
