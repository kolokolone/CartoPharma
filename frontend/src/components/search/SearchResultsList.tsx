'use client';

import Link from 'next/link';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { SearchResponse, SearchResultResponse, SearchResultType } from '@/types/api';

const RESULT_TYPE_LABELS: Record<SearchResultType, string> = {
  pharmacy: 'Pharmacies',
  poi: 'Autres POI',
  city: 'Villes',
  layer: 'Couches',
};

type SearchResultsListProps = {
  query: string;
  isLoading: boolean;
  response?: SearchResponse;
};

export function SearchResultsList({ query, isLoading, response }: SearchResultsListProps) {
  const groups = groupResults(response?.results ?? []);
  const orderedGroups = (['pharmacy', 'poi', 'city', 'layer'] as SearchResultType[])
    .filter((group) => (groups[group] ?? []).length > 0)
    .map((group) => [group, groups[group]] as const);

  return (
    <Card>
      <CardHeader className='px-4 py-3'>
        <CardTitle className='text-base'>Résultats</CardTitle>
      </CardHeader>
      <CardContent className='space-y-4 px-4 pb-4'>
        {query.trim().length < 2 ? <p className='text-sm text-muted-foreground'>Saisissez au moins deux caractères pour lancer la recherche.</p> : null}
        {query.trim().length >= 2 && isLoading ? <p className='text-sm text-muted-foreground'>Chargement des résultats…</p> : null}
        {query.trim().length >= 2 && !isLoading && (response?.results.length ?? 0) === 0 ? (
          <p className='text-sm text-muted-foreground'>Aucun résultat pour “{query}”.</p>
        ) : null}

        {query.trim().length >= 2 && !isLoading
          ? orderedGroups.map(([group, results]) => (
              <section key={group} className='space-y-2'>
                <h2 className='text-sm font-semibold text-foreground'>{RESULT_TYPE_LABELS[group]}</h2>
                <div className='space-y-2'>
                  {results.map((result) => (
                    <Link
                      key={result.id}
                      href={result.target_href}
                      className='block rounded-md border border-input px-3 py-3 hover:bg-accent/40'
                    >
                      <div className='text-sm font-medium text-foreground'>{renderHighlightedText(result.label, query)}</div>
                      {result.secondary_label ? (
                        <div className='mt-1 text-xs text-muted-foreground'>{renderHighlightedText(result.secondary_label, query)}</div>
                      ) : null}
                    </Link>
                  ))}
                </div>
              </section>
            ))
          : null}
      </CardContent>
    </Card>
  );
}

function groupResults(results: SearchResultResponse[]) {
  return results.reduce<Record<string, SearchResultResponse[]>>((accumulator, result) => {
    const current = accumulator[result.result_type] ?? [];
    current.push(result);
    accumulator[result.result_type] = current;
    return accumulator;
  }, {});
}

function renderHighlightedText(value: string, query: string) {
  const trimmedQuery = query.trim();
  if (!trimmedQuery) {
    return value;
  }

  const parts = value.split(new RegExp(`(${escapeRegExp(trimmedQuery)})`, 'gi'));
  return parts.map((part, index) => {
    if (part.toLowerCase() === trimmedQuery.toLowerCase()) {
      return (
        <mark key={`${part}-${index}`} className='rounded bg-accent px-0.5 text-foreground'>
          {part}
        </mark>
      );
    }
    return <span key={`${part}-${index}`}>{part}</span>;
  });
}

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
