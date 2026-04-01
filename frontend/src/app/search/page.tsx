import { Suspense } from 'react';

import { SearchPageClient } from '@/components/search/SearchPageClient';

export default function SearchPage() {
  return (
    <Suspense fallback={<p className='text-sm text-muted-foreground'>Chargement de la recherche…</p>}>
      <SearchPageClient />
    </Suspense>
  );
}
