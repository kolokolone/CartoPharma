'use client';

import * as React from 'react';
import { CircleMarker, MapContainer, Popup, TileLayer } from 'react-leaflet';

import type { GeoPointFeature, LayerId } from '@/types/api';

const FRANCE_CENTER: [number, number] = [46.603354, 1.888334];

const LAYER_COLORS: Record<LayerId, string> = {
  pharmacies: '#1d4ed8',
  health_professionals: '#0f766e',
  public_transport: '#7c3aed',
  shops: '#c2410c',
  points_of_interest: '#be123c',
};

type CartoMapLeafletProps = {
  points: GeoPointFeature[];
  activeLayers: LayerId[];
  height?: string;
};

export function CartoMapLeaflet({ points, activeLayers, height = '560px' }: CartoMapLeafletProps) {
  const filteredPoints = React.useMemo(
    () => points.filter((feature) => activeLayers.includes(feature.properties.layer)),
    [activeLayers, points]
  );

  return (
    <div className="overflow-hidden rounded-lg border" style={{ height }}>
      <MapContainer center={FRANCE_CENTER} zoom={6} scrollWheelZoom style={{ height: '100%', width: '100%' }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {filteredPoints.map((feature) => {
          const [lon, lat] = feature.geometry.coordinates;
          const layer = feature.properties.layer;
          const color = LAYER_COLORS[layer];

          return (
            <CircleMarker
              key={feature.properties.id}
              center={[lat, lon]}
              radius={7}
              pathOptions={{
                color,
                fillColor: color,
                fillOpacity: 0.8,
                weight: 1,
              }}
            >
              <Popup>
                <div className="text-sm">
                  <div className="font-semibold">{feature.properties.name}</div>
                  <div className="text-muted-foreground">{feature.properties.city}</div>
                  <div className="mt-1 text-xs uppercase tracking-wide" style={{ color }}>
                    {feature.properties.layer.replace('_', ' ')}
                  </div>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>
    </div>
  );
}
