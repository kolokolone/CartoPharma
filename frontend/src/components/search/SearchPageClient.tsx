'use client';

import * as React from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

import { SearchBar } from '@/components/search/SearchBar';
import { SearchResultsList } from '@/components/search/SearchResultsList';
import { SearchSuggestions } from '@/components/search/SearchSuggestions';
import { useSearch } from '@/hooks/useSearch';

export function SearchPageClient() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const currentQuery = searchParams.get('q') ?? '';
  const [inputValue, setInputValue] = React.useState(currentQuery);
  const [debouncedValue, setDebouncedValue] = React.useState(currentQuery);

  React.useEffect(() => {
    setInputValue(currentQuery);
  }, [currentQuery]);

  React.useEffect(() => {
    const timeout = window.setTimeout(() => setDebouncedValue(inputValue.trim()), 250);
    return () => window.clearTimeout(timeout);
  }, [inputValue]);

  const suggestionsQuery = useSearch({
    query: debouncedValue,
    kind: 'suggestions',
    limit: 8,
  });
  const resultsQuery = useSearch({
    query: currentQuery,
    kind: 'results',
    limit: 30,
  });

  const handleSubmit = React.useCallback(() => {
    const nextQuery = inputValue.trim();
    if (nextQuery.length < 2) {
      router.push('/search');
      return;
    }
    router.push(`/search?q=${encodeURIComponent(nextQuery)}`);
  }, [inputValue, router]);

  return (
    <div className='space-y-4'>
      <SearchBar value={inputValue} onChange={setInputValue} onSubmit={handleSubmit} isSubmitting={resultsQuery.isFetching} />
      <SearchSuggestions
        query={debouncedValue}
        isLoading={suggestionsQuery.isLoading || suggestionsQuery.isFetching}
        results={suggestionsQuery.data?.results ?? []}
      />
      <SearchResultsList query={currentQuery} isLoading={resultsQuery.isLoading || resultsQuery.isFetching} response={resultsQuery.data} />
    </div>
  );
}
