'use client';

import dynamic from 'next/dynamic';

import type { GeoPointFeature, LayerId, MapBbox } from '@/types/api';

type CartoMapProps = {
  points: GeoPointFeature[];
  activeLayers: LayerId[];
  height?: string;
  onBboxChange?: (bbox: MapBbox) => void;
};

const CartoMapLeaflet = dynamic(() => import('@/components/map/CartoMapLeaflet').then((m) => m.CartoMapLeaflet), {
  ssr: false,
  loading: () => <div className="rounded-lg border bg-muted" style={{ height: '560px' }} />,
});

export function CartoMap(props: CartoMapProps) {
  return <CartoMapLeaflet {...props} />;
}
