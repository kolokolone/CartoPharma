'use client';

import * as React from 'react';
import type { LatLngBounds } from 'leaflet';
import { CircleMarker, MapContainer, Popup, TileLayer, Tooltip, useMap, useMapEvents } from 'react-leaflet';

import { PoiFeaturePopup } from '@/components/map/PoiFeaturePopup';

import type { GeoPointFeature, LayerId, MapBbox } from '@/types/api';

const FRANCE_CENTER: [number, number] = [46.603354, 1.888334];

const LAYER_COLORS: Record<string, string> = {
  pharmacies: '#15803d',
  health_professionals: '#0f766e',
  public_transport: '#7c3aed',
  shops: '#c2410c',
  points_of_interest: '#be123c',
};

type CartoMapLeafletProps = {
  points: GeoPointFeature[];
  activeLayers: LayerId[];
  height?: string;
  onBboxChange?: (bbox: MapBbox) => void;
  initialCenter?: [number, number];
  initialZoom?: number;
  interactive?: boolean;
  highlightedPointId?: string;
};

function boundsToBbox(bounds: LatLngBounds): MapBbox {
  const southWest = bounds.getSouthWest();
  const northEast = bounds.getNorthEast();
  return [southWest.lng, southWest.lat, northEast.lng, northEast.lat];
}

function MapViewportReporter({ onBboxChange }: { onBboxChange?: (bbox: MapBbox) => void }) {
  const map = useMap();

  const reportBounds = React.useCallback(() => {
    if (!onBboxChange) {
      return;
    }
    onBboxChange(boundsToBbox(map.getBounds()));
  }, [map, onBboxChange]);

  React.useEffect(() => {
    reportBounds();
  }, [reportBounds]);

  useMapEvents({
    moveend: reportBounds,
    zoomend: reportBounds,
  });

  return null;
}

function MapViewController({ center, zoom }: { center?: [number, number]; zoom?: number }) {
  const map = useMap();

  React.useEffect(() => {
    if (!center) {
      return;
    }
    map.setView(center, zoom ?? map.getZoom());
  }, [center, map, zoom]);

  return null;
}

export function CartoMapLeaflet({
  points,
  activeLayers,
  height = '560px',
  onBboxChange,
  initialCenter,
  initialZoom,
  interactive = true,
  highlightedPointId,
}: CartoMapLeafletProps) {
  const filteredPoints = React.useMemo(
    () => points.filter((feature) => activeLayers.includes(feature.properties.layer)),
    [activeLayers, points]
  );

  return (
    <div className="overflow-hidden rounded-lg border" style={{ height }}>
      <MapContainer
        center={initialCenter ?? FRANCE_CENTER}
        zoom={initialZoom ?? 6}
        scrollWheelZoom={interactive}
        dragging={interactive}
        doubleClickZoom={interactive}
        boxZoom={interactive}
        keyboard={interactive}
        touchZoom={interactive}
        zoomControl={interactive}
        style={{ height: '100%', width: '100%' }}
      >
        <MapViewController center={initialCenter} zoom={initialZoom} />
        {interactive ? <MapViewportReporter onBboxChange={onBboxChange} /> : null}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {filteredPoints.map((feature) => {
          const [lon, lat] = feature.geometry.coordinates;
          const layer = feature.properties.layer;
          const color = feature.properties.layer_color ?? LAYER_COLORS[layer] ?? '#334155';
          const title = feature.properties.display_name ?? feature.properties.name;

          return (
            <CircleMarker
              key={feature.properties.id}
              center={[lat, lon]}
              radius={feature.properties.id === highlightedPointId ? 9 : 7}
              pathOptions={{
                color,
                fillColor: color,
                fillOpacity: feature.properties.id === highlightedPointId ? 0.95 : 0.8,
                weight: feature.properties.id === highlightedPointId ? 2 : 1,
              }}
            >
              <Tooltip direction="top" offset={[0, -10]} opacity={1}>
                <div className="min-w-[140px] text-xs">
                  <div className="font-semibold text-foreground">{title}</div>
                  <div className="text-muted-foreground">{feature.properties.city}</div>
                </div>
              </Tooltip>
              <Popup>
                <PoiFeaturePopup feature={feature} />
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>
    </div>
  );
}
