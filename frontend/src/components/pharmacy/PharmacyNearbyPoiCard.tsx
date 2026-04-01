import Link from 'next/link';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { PharmacyNearbyPoiResponse } from '@/types/api';

type PharmacyNearbyPoiCardProps = {
  data?: PharmacyNearbyPoiResponse;
  radiusM: number;
  onRadiusChange: (radiusM: number) => void;
  isLoading: boolean;
  isError: boolean;
};

export function PharmacyNearbyPoiCard({ data, radiusM, onRadiusChange, isLoading, isError }: PharmacyNearbyPoiCardProps) {
  const groups = (data?.items ?? []).reduce<Record<string, PharmacyNearbyPoiResponse['items']>>((accumulator, item) => {
    const current = accumulator[item.category] ?? [];
    current.push(item);
    accumulator[item.category] = current;
    return accumulator;
  }, {});

  return (
    <Card>
      <CardHeader className='px-4 py-3'>
        <div className='flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between'>
          <CardTitle className='text-base'>POI autour de la pharmacie</CardTitle>
          <label className='text-sm text-muted-foreground'>
            Rayon
            <select
              className='ml-2 h-9 rounded-md border border-input bg-background px-2 text-sm text-foreground'
              value={radiusM}
              onChange={(event) => onRadiusChange(Number(event.target.value))}
            >
              <option value={500}>500 m</option>
              <option value={1000}>1 km</option>
              <option value={2000}>2 km</option>
              <option value={5000}>5 km</option>
            </select>
          </label>
        </div>
      </CardHeader>
      <CardContent className='space-y-4 px-4 pb-4'>
        {isLoading ? <p className='text-sm text-muted-foreground'>Chargement des POI proches…</p> : null}
        {!isLoading && isError ? <p className='text-sm text-muted-foreground'>Impossible de charger les POI proches pour le moment.</p> : null}
        {!isLoading && !isError && (data?.items.length ?? 0) === 0 ? <p className='text-sm text-muted-foreground'>Aucun POI trouvé dans ce rayon.</p> : null}

        {!isLoading && !isError
          ? Object.entries(groups).map(([category, items]) => (
              <section key={category} className='space-y-2'>
                <h3 className='text-sm font-semibold text-foreground'>
                  {category} · {items.length}
                </h3>
                <div className='space-y-2'>
                  {items.map((item) => (
                    <Link key={item.id} href={item.target_href} className='block rounded-md border border-input px-3 py-2 hover:bg-accent/40'>
                      <div className='text-sm font-medium text-foreground'>{item.label}</div>
                      <div className='text-xs text-muted-foreground'>
                        {item.layer_label}
                        {item.secondary_label ? ` · ${item.secondary_label}` : ''}
                        {` · ${item.distance_m} m`}
                      </div>
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
