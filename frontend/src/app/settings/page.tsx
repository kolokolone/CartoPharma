'use client';

import * as React from 'react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { usePatchSettings, useSettings } from '@/hooks/useSettings';

export default function SettingsPage() {
  const settingsQuery = useSettings();
  const patchSettingsMutation = usePatchSettings();

  const [theme, setTheme] = React.useState<'light' | 'dark' | 'system'>('light');
  const [showLabels, setShowLabels] = React.useState(true);
  const [compactControls, setCompactControls] = React.useState(false);
  const [feedback, setFeedback] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!settingsQuery.data) return;
    setTheme(settingsQuery.data.theme);
    setShowLabels(settingsQuery.data.show_labels);
    setCompactControls(settingsQuery.data.compact_controls);
  }, [settingsQuery.data]);

  const handleSave = async () => {
    setFeedback(null);
    try {
      await patchSettingsMutation.mutateAsync({
        theme,
        show_labels: showLabels,
        compact_controls: compactControls,
      });
      setFeedback('Paramètres enregistrés.');
    } catch {
      setFeedback('Impossible d’enregistrer pour le moment.');
    }
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="px-4 py-3">
          <CardTitle className="text-base">Préférences d’interface</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 px-4 pb-4">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <label className="text-sm">
              <div className="text-muted-foreground">Thème</div>
              <select
                className="mt-1 h-10 w-full rounded-md border border-input bg-background px-3"
                value={theme}
                onChange={(event) => setTheme(event.target.value as 'light' | 'dark' | 'system')}
              >
                <option value="light">Clair</option>
                <option value="dark">Sombre</option>
                <option value="system">Système</option>
              </select>
            </label>
          </div>

          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            <label className="flex items-center gap-3 rounded-md border border-input px-3 py-2 text-sm">
              <input
                type="checkbox"
                className="h-4 w-4 accent-primary"
                checked={showLabels}
                onChange={(event) => setShowLabels(event.target.checked)}
              />
              Afficher les labels de points sur la carte
            </label>

            <label className="flex items-center gap-3 rounded-md border border-input px-3 py-2 text-sm">
              <input
                type="checkbox"
                className="h-4 w-4 accent-primary"
                checked={compactControls}
                onChange={(event) => setCompactControls(event.target.checked)}
              />
              Activer le mode contrôles compacts
            </label>
          </div>

          <div className="flex items-center gap-3">
            <Button size="sm" onClick={handleSave} disabled={patchSettingsMutation.isPending || settingsQuery.isLoading}>
              Enregistrer
            </Button>
            {feedback ? <span className="text-sm text-muted-foreground">{feedback}</span> : null}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
