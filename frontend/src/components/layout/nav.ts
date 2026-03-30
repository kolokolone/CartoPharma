import type { LucideIcon } from 'lucide-react';
import { Home, Map, Settings } from 'lucide-react';

export type NavPlacement = 'main' | 'footer';

export type NavItemConfig = {
  label: string;
  href: string;
  icon: LucideIcon;
  placement: NavPlacement;
};

export const NAV_ITEMS: NavItemConfig[] = [
  {
    label: 'Accueil',
    href: '/',
    icon: Home,
    placement: 'main',
  },
  {
    label: 'Carte',
    href: '/map',
    icon: Map,
    placement: 'main',
  },
  {
    label: 'Paramètres',
    href: '/settings',
    icon: Settings,
    placement: 'footer',
  },
];

export const MAIN_NAV_ITEMS = NAV_ITEMS.filter((item) => item.placement === 'main');
export const FOOTER_NAV_ITEMS = NAV_ITEMS.filter((item) => item.placement === 'footer');
