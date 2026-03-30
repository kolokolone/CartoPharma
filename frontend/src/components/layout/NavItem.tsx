import Link from 'next/link';

import { cn } from '@/lib/utils';
import type { NavItemConfig } from './nav';

type NavItemProps = {
  item: NavItemConfig;
  isActive: boolean;
  onNavigate?: () => void;
  collapsed?: boolean;
};

export function NavItem({ item, isActive, onNavigate, collapsed = false }: NavItemProps) {
  const Icon = item.icon;

  return (
    <Link
      href={item.href}
      className={cn(
        'group relative flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
        collapsed && 'justify-center px-2',
        isActive ? 'bg-accent text-accent-foreground' : 'text-foreground hover:bg-accent/70'
      )}
      aria-current={isActive ? 'page' : undefined}
      onClick={onNavigate}
      aria-label={collapsed ? item.label : undefined}
      title={collapsed ? item.label : undefined}
    >
      <span
        className={cn(
          'absolute left-0 top-1/2 h-6 w-1 -translate-y-1/2 rounded-r bg-transparent transition-colors',
          isActive ? 'bg-primary' : 'group-hover:bg-primary/40'
        )}
      />
      <Icon className="h-4 w-4 shrink-0" />
      {!collapsed ? <span className="truncate">{item.label}</span> : null}
    </Link>
  );
}
