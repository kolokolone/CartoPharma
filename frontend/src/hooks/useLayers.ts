import { useQuery } from '@tanstack/react-query';

import { layersApi } from '@/lib/api';
import type { LayerId } from '@/types/api';

const layersCatalogKey = ['layers', 'catalog'];

export function useLayersCatalog() {
  return useQuery({
    queryKey: layersCatalogKey,
    queryFn: layersApi.list,
    staleTime: 5 * 60_000,
  });
}

export function useLayerPoints(activeLayers: LayerId[]) {
  return useQuery({
    queryKey: ['layers', 'points', ...activeLayers],
    queryFn: () => layersApi.points(activeLayers),
    staleTime: 60_000,
  });
}
