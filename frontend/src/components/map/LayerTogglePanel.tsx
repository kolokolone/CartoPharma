'use client';

import type { LayerDefinition, LayerId } from '@/types/api';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

type LayerTogglePanelProps = {
  layers: LayerDefinition[];
  active: LayerId[];
  onToggle: (layerId: LayerId) => void;
};

export function LayerTogglePanel({ layers, active, onToggle }: LayerTogglePanelProps) {
  return (
    <Card>
      <CardHeader className="py-3 px-4">
        <CardTitle className="text-base">Couches cartographiques</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 px-4 pb-4">
        {layers.map((layer) => {
          const checked = active.includes(layer.id);
          return (
            <label key={layer.id} className="flex cursor-pointer items-start gap-3 rounded-md border border-input p-3 hover:bg-accent/40">
              <input
                type="checkbox"
                className="mt-1 h-4 w-4 accent-primary"
                checked={checked}
                onChange={() => onToggle(layer.id)}
              />
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ backgroundColor: layer.color }} />
                  <span className="font-medium leading-tight">{layer.label}</span>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">
                  {layer.category} · priorité {layer.priority}
                </p>
              </div>
            </label>
          );
        })}
      </CardContent>
    </Card>
  );
}
