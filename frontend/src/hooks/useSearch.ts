import { useQuery } from '@tanstack/react-query';

import { searchApi } from '@/lib/api';

type UseSearchOptions = {
  query: string;
  kind: 'suggestions' | 'results';
  limit?: number;
  enabled?: boolean;
};

export function useSearch({ query, kind, limit = 20, enabled = true }: UseSearchOptions) {
  return useQuery({
    queryKey: ['search', kind, query, limit],
    queryFn: () => searchApi.search(query, kind, limit),
    enabled: enabled && query.trim().length >= 2,
    staleTime: 30_000,
  });
}
