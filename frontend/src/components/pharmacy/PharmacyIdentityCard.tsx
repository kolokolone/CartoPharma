import Link from 'next/link';

import { PharmacyFavoriteButton } from '@/components/pharmacy/PharmacyFavoriteButton';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { PharmacyDetailResponse } from '@/types/api';

type PharmacyIdentityCardProps = {
  detail: PharmacyDetailResponse;
  isFavorite: boolean;
  isFavoritePending: boolean;
  onToggleFavorite: () => void;
};

export function PharmacyIdentityCard({ detail, isFavorite, isFavoritePending, onToggleFavorite }: PharmacyIdentityCardProps) {
  const safeWebsite = getSafeWebsiteUrl(detail.website);
  const pappersHref = detail.siret ? `https://www.pappers.fr/recherche?q=${detail.siret}` : null;

  return (
    <Card>
      <CardHeader className='px-4 py-3'>
        <div className='flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between'>
          <div className='space-y-1'>
            <CardTitle className='text-base'>{detail.display_name}</CardTitle>
            <p className='text-sm text-muted-foreground'>{detail.legal_name || '/'}</p>
          </div>
          <PharmacyFavoriteButton isFavorite={isFavorite} isPending={isFavoritePending} onToggle={onToggleFavorite} />
        </div>
      </CardHeader>
      <CardContent className='space-y-4 px-4 pb-4'>
        <div className='grid grid-cols-1 gap-3 text-sm md:grid-cols-2'>
          <MetaRow label='Adresse' value={joinLines(detail.address_line_1, joinLines(detail.postal_code, detail.city, ' '))} />
          <MetaRow label='Type' value={detail.establishment_type || '/'} />
          <MetaRow label='Téléphone' value={detail.phone || '/'} />
          <MetaRow label='Fax' value={detail.fax || '/'} />
          <MetaRow label='Horaires' value={detail.opening_hours || '/'} />
          <MetaRow label='SIRET' value={detail.siret || '/'} />
          <MetaRow label='Région' value={joinLines(detail.department, detail.region, ' · ') || '/'} />
          <MetaRow label='Pharmaciens' value={String(detail.pharmacist_count)} />
        </div>

        <div className='flex flex-wrap gap-2'>
          <Link href='/search' className='text-sm text-primary underline-offset-2 hover:underline'>
            Retour à la recherche
          </Link>
          <Link href='/map' className='text-sm text-primary underline-offset-2 hover:underline'>
            Retour à la carte
          </Link>
          {safeWebsite ? (
            <a href={safeWebsite} target='_blank' rel='noreferrer' className='text-sm text-primary underline-offset-2 hover:underline'>
              Site web
            </a>
          ) : null}
          {pappersHref ? (
            <a href={pappersHref} target='_blank' rel='noreferrer' className='text-sm text-primary underline-offset-2 hover:underline'>
              Voir sur Pappers
            </a>
          ) : null}
        </div>
      </CardContent>
    </Card>
  );
}

function MetaRow({ label, value }: { label: string; value: string }) {
  return (
    <div className='rounded-md border border-input px-3 py-2'>
      <div className='text-xs font-medium uppercase tracking-wide text-muted-foreground'>{label}</div>
      <div className='mt-1 text-sm text-foreground'>{value}</div>
    </div>
  );
}

function joinLines(first?: string | null, second?: string | null, separator = ' ') {
  const values = [first, second].filter((value): value is string => Boolean(value));
  return values.join(separator);
}

function getSafeWebsiteUrl(value?: string | null) {
  if (!value) {
    return null;
  }

  const candidate = /^https?:\/\//i.test(value) ? value : `https://${value}`;

  try {
    const url = new URL(candidate);
    if (url.protocol !== 'http:' && url.protocol !== 'https:') {
      return null;
    }
    return url.toString();
  } catch {
    return null;
  }
}
