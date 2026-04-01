import Link from 'next/link';
import { ArrowRight, Layers, MapPinned, Search, Settings } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function HomePage() {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="px-4 py-3">
          <CardTitle className="text-base">Fondation CartoPharma</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 px-4 pb-4">
          <p className="text-sm text-muted-foreground">
            Cette première version pose une base propre et extensible pour la cartographie des pharmacies, des professionnels
            de santé, des transports et des services utiles en France.
          </p>
          <div className="flex flex-wrap gap-2">
            <Button asChild size="sm">
              <Link href="/map">
                Ouvrir la carte
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild size="sm" variant="outline">
              <Link href="/search">Lancer une recherche</Link>
            </Button>
            <Button asChild size="sm" variant="outline">
              <Link href="/settings">Configurer l’affichage</Link>
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="px-4 py-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <MapPinned className="h-4 w-4" />
              Carte interactive
            </CardTitle>
          </CardHeader>
          <CardContent className="px-4 pb-4 text-sm text-muted-foreground">
            Carte Leaflet prête pour les couches métiers et les futures données en temps réel.
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="px-4 py-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Layers className="h-4 w-4" />
              Architecture couches
            </CardTitle>
          </CardHeader>
          <CardContent className="px-4 pb-4 text-sm text-muted-foreground">
            Registre de couches prêt pour la priorisation pharmacies et l’activation/désactivation par catégorie.
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="px-4 py-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Search className="h-4 w-4" />
              Recherche transverse
            </CardTitle>
          </CardHeader>
          <CardContent className="px-4 pb-4 text-sm text-muted-foreground">
            Point d’entrée rapide vers les fiches pharmacie, les villes et les couches utiles.
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="px-4 py-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Settings className="h-4 w-4" />
              Paramètres
            </CardTitle>
          </CardHeader>
          <CardContent className="px-4 pb-4 text-sm text-muted-foreground">
            Préférences visuelles et options de carte déjà branchées sur l’API backend FastAPI.
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
