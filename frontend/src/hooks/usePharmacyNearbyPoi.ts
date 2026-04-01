import { useQuery } from '@tanstack/react-query';

import { pharmaciesApi } from '@/lib/api';

export function usePharmacyNearbyPoi(establishmentId: string, radiusM: number) {
  return useQuery({
    queryKey: ['pharmacy', 'nearby-poi', establishmentId, radiusM],
    queryFn: () => pharmaciesApi.nearbyPoi(establishmentId, radiusM),
    enabled: establishmentId.trim().length > 0,
    staleTime: 30_000,
  });
}
