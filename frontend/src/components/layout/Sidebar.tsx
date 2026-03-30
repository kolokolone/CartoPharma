import { PanelLeftClose, PanelLeftOpen } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { FOOTER_NAV_ITEMS, MAIN_NAV_ITEMS, type NavItemConfig } from './nav';
import { NavItem } from './NavItem';

type SidebarProps = {
  pathname: string;
  onNavigate?: () => void;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
};

function isItemActive(pathname: string, item: NavItemConfig) {
  if (item.href === '/') return pathname === '/';
  return pathname === item.href || pathname.startsWith(`${item.href}/`);
}

export function Sidebar({ pathname, onNavigate, collapsed = false, onToggleCollapse }: SidebarProps) {
  if (collapsed && onToggleCollapse) {
    return (
      <div className="flex h-full flex-col bg-card">
        <div className="border-b border-border px-2 py-3">
          <div className="flex items-center justify-center">
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="h-9 w-9 shrink-0"
              onClick={onToggleCollapse}
              aria-label="Étendre la barre latérale"
              title="Étendre la barre latérale"
            >
              <PanelLeftOpen className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-2 py-4">
          <nav aria-label="Navigation principale" className="space-y-1">
            {MAIN_NAV_ITEMS.map((item) => (
              <NavItem key={item.href} item={item} isActive={isItemActive(pathname, item)} onNavigate={onNavigate} collapsed />
            ))}
          </nav>
        </div>

        <div className="border-t border-border px-2 py-4">
          <nav aria-label="Navigation secondaire" className="space-y-1">
            {FOOTER_NAV_ITEMS.map((item) => (
              <NavItem key={item.href} item={item} isActive={isItemActive(pathname, item)} onNavigate={onNavigate} collapsed />
            ))}
          </nav>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col bg-card">
      <div className="border-b border-border px-3 py-4">
        <div className="flex items-start justify-between gap-2">
          <div>
            <p className="text-lg font-semibold tracking-tight">CartoPharma</p>
            <p className="mt-1 text-xs text-muted-foreground">Cartographie santé & services (France)</p>
          </div>

          {onToggleCollapse ? (
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="h-8 w-8 shrink-0"
              onClick={onToggleCollapse}
              aria-label="Réduire la barre latérale"
              title="Réduire la barre latérale"
            >
              <PanelLeftClose className="h-4 w-4" />
            </Button>
          ) : null}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-4">
        <nav aria-label="Navigation principale" className="space-y-1">
          {MAIN_NAV_ITEMS.map((item) => (
            <NavItem key={item.href} item={item} isActive={isItemActive(pathname, item)} onNavigate={onNavigate} collapsed={collapsed} />
          ))}
        </nav>
      </div>

      <div className="border-t border-border px-3 py-4">
        <nav aria-label="Navigation secondaire" className="space-y-1">
          {FOOTER_NAV_ITEMS.map((item) => (
            <NavItem key={item.href} item={item} isActive={isItemActive(pathname, item)} onNavigate={onNavigate} collapsed={collapsed} />
          ))}
        </nav>
      </div>
    </div>
  );
}
