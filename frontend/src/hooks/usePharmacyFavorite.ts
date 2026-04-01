import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { pharmaciesApi } from '@/lib/api';

export function usePharmacyFavorite(establishmentId: string) {
  const queryClient = useQueryClient();
  const favoriteKey = ['pharmacy', 'favorite', establishmentId];
  const detailKey = ['pharmacy', 'detail', establishmentId];

  const statusQuery = useQuery({
    queryKey: favoriteKey,
    queryFn: () => pharmaciesApi.favoriteStatus(establishmentId),
    enabled: establishmentId.trim().length > 0,
    staleTime: 15_000,
  });

  const toggleMutation = useMutation({
    mutationFn: (shouldBeFavorite: boolean) => {
      if (shouldBeFavorite) {
        return pharmaciesApi.putFavorite(establishmentId);
      }
      return pharmaciesApi.deleteFavorite(establishmentId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: favoriteKey });
      queryClient.invalidateQueries({ queryKey: detailKey });
    },
  });

  return {
    statusQuery,
    toggleMutation,
  };
}
