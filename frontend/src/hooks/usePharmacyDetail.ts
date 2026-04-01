import { useQuery } from '@tanstack/react-query';

import { pharmaciesApi } from '@/lib/api';

export function usePharmacyDetail(establishmentId: string) {
  return useQuery({
    queryKey: ['pharmacy', 'detail', establishmentId],
    queryFn: () => pharmaciesApi.detail(establishmentId),
    enabled: establishmentId.trim().length > 0,
    staleTime: 60_000,
  });
}
