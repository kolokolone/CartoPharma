import type { ComponentType } from 'react';

import { HomeHeaderActions, MapHeaderActions } from './HeaderActions';
import type { ContainerVariant } from './PageContainer';

type PageMetadata = {
  title: string;
  subtitle?: string;
  container: ContainerVariant;
  HeaderActions?: ComponentType;
  showToday?: boolean;
};

const STATIC_PAGE_METADATA: Record<string, PageMetadata> = {
  '/': {
    title: 'Accueil',
    subtitle: 'Pilotage territorial des services de santé de proximité',
    container: 'default',
    HeaderActions: HomeHeaderActions,
    showToday: true,
  },
  '/map': {
    title: 'Carte',
    subtitle: 'Vue France par couches (fondation V1)',
    container: 'wide',
    HeaderActions: MapHeaderActions,
    showToday: true,
  },
  '/search': {
    title: 'Recherche',
    subtitle: 'Trouver rapidement une pharmacie, une ville ou une couche',
    container: 'default',
  },
  '/settings': {
    title: 'Paramètres',
    subtitle: 'Préférences d’affichage et comportement de carte',
    container: 'default',
  },
};

const FALLBACK_PAGE_METADATA: PageMetadata = {
  title: 'CartoPharma',
  subtitle: 'Application cartographique santé',
  container: 'default',
};

function normalizePathname(pathname: string) {
  if (pathname.length > 1 && pathname.endsWith('/')) {
    return pathname.slice(0, -1);
  }
  return pathname;
}

export function resolvePageMetadata(pathname: string): PageMetadata {
  const normalizedPathname = normalizePathname(pathname);
  if (normalizedPathname.startsWith('/pharmacie/')) {
    return {
      title: 'Fiche pharmacie',
      subtitle: 'Identité, équipe, proximité et actions rapides',
      container: 'default',
    };
  }
  return STATIC_PAGE_METADATA[normalizedPathname] ?? FALLBACK_PAGE_METADATA;
}
