'use client';

import * as React from 'react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useRebuildPoi } from '@/hooks/useIndexing';
import { usePatchSettings, useSettings } from '@/hooks/useSettings';
import { APP_VERSION } from '@/lib/app-version';
import type { ReindexPoiResponse } from '@/types/api';

export default function SettingsPage() {
  const settingsQuery = useSettings();
  const patchSettingsMutation = usePatchSettings();
  const rebuildPoiMutation = useRebuildPoi();

  const [theme, setTheme] = React.useState<'light' | 'dark' | 'system'>('light');
  const [showLabels, setShowLabels] = React.useState(true);
  const [compactControls, setCompactControls] = React.useState(false);
  const [feedback, setFeedback] = React.useState<string | null>(null);
  const [reindexFeedback, setReindexFeedback] = React.useState<string | null>(null);
  const [reindexReport, setReindexReport] = React.useState<ReindexPoiResponse | null>(null);

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

  const handleReindex = async () => {
    setReindexFeedback(null);
    try {
      const report = await rebuildPoiMutation.mutateAsync();
      setReindexReport(report);
      setReindexFeedback('Réindexation terminée avec succès.');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Impossible de relancer la réindexation pour le moment.';
      setReindexFeedback(message);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-4 px-1">
        <div className="text-sm text-muted-foreground">
          Version <span className="font-medium text-foreground">{APP_VERSION}</span>
        </div>
      </div>

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

      <Card>
        <CardHeader className="px-4 py-3">
          <CardTitle className="text-base">Réindexation des données</CardTitle>
          <CardDescription>
            Reconstruit la base `poi.sqlite` à partir des CSV disponibles et recharge la projection pharmacie enrichie.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 px-4 pb-4">
          <div className="flex flex-wrap items-center gap-3">
            <Button size="sm" onClick={handleReindex} disabled={rebuildPoiMutation.isPending}>
              {rebuildPoiMutation.isPending ? 'Réindexation en cours…' : 'Réindexer les données'}
            </Button>
            {reindexFeedback ? <span className="text-sm text-muted-foreground">{reindexFeedback}</span> : null}
          </div>

          {reindexReport ? (
            <div className="grid grid-cols-1 gap-3 rounded-md border border-input p-3 text-sm md:grid-cols-2">
              <div>
                <div className="font-medium text-foreground">Import métier</div>
                <ul className="mt-1 space-y-1 text-muted-foreground">
                  <li>{reindexReport.pharmacy_files_detected} fichier(s) pharmacie détecté(s)</li>
                  <li>{reindexReport.pharmacies_imported} pharmacie(s) projetée(s)</li>
                  <li>{reindexReport.pharmacists_imported} pharmacien(s) importé(s)</li>
                  <li>{reindexReport.activities_imported} activité(s) importée(s)</li>
                  <li>{reindexReport.degrees_imported} diplôme(s) importé(s)</li>
                </ul>
              </div>
              <div>
                <div className="font-medium text-foreground">Projection cartographique</div>
                <ul className="mt-1 space-y-1 text-muted-foreground">
                  <li>{reindexReport.generic_files_processed} fichier(s) CSV générique(s) traité(s)</li>
                  <li>{reindexReport.poi_rows_rebuilt} point(s) indexé(s)</li>
                  <li>{reindexReport.geocoded_resolved} géocodé(s) · {reindexReport.geocoded_pending} en attente</li>
                  <li>{reindexReport.rows_rejected} ligne(s) rejetée(s)</li>
                  <li>{Math.round(reindexReport.duration_ms / 100) / 10}s d’exécution</li>
                </ul>
              </div>
            </div>
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
}
