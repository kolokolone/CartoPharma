'use client';

import Link from 'next/link';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { SearchResultResponse } from '@/types/api';

type SearchSuggestionsProps = {
  query: string;
  isLoading: boolean;
  results: SearchResultResponse[];
};

export function SearchSuggestions({ query, isLoading, results }: SearchSuggestionsProps) {
  if (query.trim().length < 2) {
    return null;
  }

  return (
    <Card>
      <CardHeader className='px-4 py-3'>
        <CardTitle className='text-base'>Suggestions</CardTitle>
      </CardHeader>
      <CardContent className='px-4 pb-4'>
        {isLoading ? <p className='text-sm text-muted-foreground'>Recherche en cours…</p> : null}
        {!isLoading && results.length === 0 ? <p className='text-sm text-muted-foreground'>Aucune suggestion pour le moment.</p> : null}
        {!isLoading ? (
          <div className='space-y-2'>
            {results.map((result) => (
              <Link
                key={result.id}
                href={result.target_href}
                className='block rounded-md border border-input px-3 py-2 hover:bg-accent/40'
              >
                <div className='text-sm font-medium text-foreground'>{result.label}</div>
                <div className='text-xs text-muted-foreground'>
                  {result.result_type}
                  {result.secondary_label ? ` · ${result.secondary_label}` : ''}
                </div>
              </Link>
            ))}
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
