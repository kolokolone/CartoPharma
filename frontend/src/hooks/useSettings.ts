import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { settingsApi } from '@/lib/api';
import type { SettingsPatch } from '@/types/api';

const settingsKey = ['settings'];

export function useSettings() {
  return useQuery({
    queryKey: settingsKey,
    queryFn: settingsApi.get,
    staleTime: 60_000,
  });
}

export function usePatchSettings() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: SettingsPatch) => settingsApi.patch(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: settingsKey });
    },
  });
}
