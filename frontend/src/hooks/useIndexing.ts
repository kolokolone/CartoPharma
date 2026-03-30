import { useMutation, useQueryClient } from '@tanstack/react-query';

import { indexingApi } from '@/lib/api';


export function useRebuildPoi() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: indexingApi.rebuildPoi,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['layers'] });
    },
  });
}
