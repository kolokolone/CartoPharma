'use client';

import * as React from 'react';
import { useParams } from 'next/navigation';

import { PharmacyIdentityCard } from '@/components/pharmacy/PharmacyIdentityCard';
import { PharmacyNearbyPoiCard } from '@/components/pharmacy/PharmacyNearbyPoiCard';
import { PharmacyTeamTable } from '@/components/pharmacy/PharmacyTeamTable';
import { CartoMap } from '@/components/map/CartoMap';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { usePharmacyDetail } from '@/hooks/usePharmacyDetail';
import { usePharmacyFavorite } from '@/hooks/usePharmacyFavorite';
import { usePharmacyNearbyPoi } from '@/hooks/usePharmacyNearbyPoi';
import type { GeoPointFeature } from '@/types/api';

const DEFAULT_RADIUS_M = 1000;

export default function PharmacyDetailPage() {
  const params = useParams<{ id: string }>();
  const establishmentId = typeof params.id === 'string' ? params.id : '';
  const [radiusM, setRadiusM] = React.useState(DEFAULT_RADIUS_M);

  const detailQuery = usePharmacyDetail(establishmentId);
  const nearbyQuery = usePharmacyNearbyPoi(establishmentId, radiusM);
  const { statusQuery, toggleMutation } = usePharmacyFavorite(establishmentId);

  const detail = detailQuery.data;
  const isFavorite = statusQuery.data?.is_favorite ?? detail?.is_favorite ?? false;
  const canRenderMap = detail?.latitude != null && detail.longitude != null;
  const mapPoints = React.useMemo(() => {
    if (!detail || detail.latitude == null || detail.longitude == null) {
      return [];
    }

    const feature: GeoPointFeature = {
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: [detail.longitude, detail.latitude],
      },
      properties: {
        id: detail.establishment_id,
        layer: 'pharmacies',
        layer_label: 'Pharmacies',
        layer_color: '#15803d',
        name: detail.display_name,
        display_name: detail.display_name,
        city: detail.city || '',
        address_line_1: detail.address_line_1,
        postal_code: detail.postal_code,
        phone: detail.phone,
        website: detail.website,
        opening_hours: detail.opening_hours,
        siret: detail.siret,
        pharmacy_establishment_id: detail.establishment_id,
        pharmacist_count: detail.pharmacist_count,
        pharmacy_type: detail.establishment_type,
      },
    };

    return [feature];
  }, [detail]);

  const handleToggleFavorite = React.useCallback(() => {
    toggleMutation.mutate(!isFavorite);
  }, [isFavorite, toggleMutation]);

  if (detailQuery.isLoading) {
    return <p className='text-sm text-muted-foreground'>Chargement de la fiche pharmacie…</p>;
  }

  if (detailQuery.isError || !detail) {
    return <p className='text-sm text-muted-foreground'>Impossible de charger cette fiche pharmacie.</p>;
  }

  return (
    <div className='space-y-4'>
      <PharmacyIdentityCard
        detail={detail}
        isFavorite={isFavorite}
        isFavoritePending={toggleMutation.isPending}
        onToggleFavorite={handleToggleFavorite}
      />

      <Card>
        <CardHeader className='px-4 py-3'>
          <CardTitle className='text-base'>Mini-carte</CardTitle>
        </CardHeader>
        <CardContent className='px-4 pb-4'>
          {canRenderMap ? (
            <CartoMap
              points={mapPoints}
              activeLayers={['pharmacies']}
              height='320px'
              initialCenter={[detail.latitude as number, detail.longitude as number]}
              initialZoom={15}
              interactive={false}
              highlightedPointId={detail.establishment_id}
            />
          ) : (
            <p className='text-sm text-muted-foreground'>Coordonnées indisponibles pour afficher la mini-carte.</p>
          )}
        </CardContent>
      </Card>

      <PharmacyTeamTable pharmacists={detail.pharmacists} />

      <PharmacyNearbyPoiCard
        data={nearbyQuery.data}
        radiusM={radiusM}
        onRadiusChange={setRadiusM}
        isLoading={nearbyQuery.isLoading || nearbyQuery.isFetching}
        isError={nearbyQuery.isError}
      />
    </div>
  );
}
