import { useQuery } from '@tanstack/react-query';

import { layersApi } from '@/lib/api';
import type { LayerId, MapBbox } from '@/types/api';

const layersCatalogKey = ['layers', 'catalog'];

export function useLayersCatalog() {
  return useQuery({
    queryKey: layersCatalogKey,
    queryFn: layersApi.list,
    staleTime: 5 * 60_000,
  });
}

type UseLayerPointsOptions = {
  layers: LayerId[];
  bbox?: MapBbox | null;
};

export function useLayerPoints({ layers, bbox }: UseLayerPointsOptions) {
  return useQuery({
    queryKey: ['layers', 'points', ...layers, ...(bbox ?? [])],
    queryFn: () => layersApi.points(layers, bbox),
    enabled: layers.length > 0,
    staleTime: 60_000,
  });
}
