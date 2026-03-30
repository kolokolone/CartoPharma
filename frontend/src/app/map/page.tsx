'use client';

import * as React from 'react';

import { CartoMap } from '@/components/map/CartoMap';
import { LayerTogglePanel } from '@/components/map/LayerTogglePanel';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useLayersCatalog, useLayerPoints } from '@/hooks/useLayers';
import type { LayerId } from '@/types/api';

export default function MapPage() {
  const catalogQuery = useLayersCatalog();

  const [activeLayers, setActiveLayers] = React.useState<LayerId[]>([]);

  React.useEffect(() => {
    if (!catalogQuery.data) return;
    setActiveLayers(catalogQuery.data.layers.filter((layer) => layer.visible_by_default).map((layer) => layer.id));
  }, [catalogQuery.data]);

  const pointsQuery = useLayerPoints(activeLayers);

  const handleToggleLayer = (layerId: LayerId) => {
    setActiveLayers((previous) => {
      if (previous.includes(layerId)) {
        return previous.filter((id) => id !== layerId);
      }
      return [...previous, layerId];
    });
  };

  const layerCount = activeLayers.length;
  const pointsCount = pointsQuery.data?.features.length ?? 0;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[320px_minmax(0,1fr)]">
        <div className="space-y-4">
          <LayerTogglePanel layers={catalogQuery.data?.layers ?? []} active={activeLayers} onToggle={handleToggleLayer} />

          <Card>
            <CardHeader className="px-4 py-3">
              <CardTitle className="text-base">État de la carte</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 px-4 pb-4 text-sm text-muted-foreground">
              <p>{layerCount} couche(s) active(s).</p>
              <p>{pointsCount} point(s) affiché(s).</p>
              <p>France uniquement. Données mockées pour la phase fondation.</p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader className="px-4 py-3">
            <CardTitle className="text-base">Carte interactive</CardTitle>
          </CardHeader>
          <CardContent className="px-4 pb-4">
            <CartoMap points={pointsQuery.data?.features ?? []} activeLayers={activeLayers} height="620px" />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
