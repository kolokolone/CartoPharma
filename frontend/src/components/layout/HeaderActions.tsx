'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';

export function HomeHeaderActions() {
  return (
    <Button asChild size="sm" variant="outline">
      <Link href="/map">Ouvrir la carte</Link>
    </Button>
  );
}

export function MapHeaderActions() {
  return (
    <Button asChild size="sm" variant="outline">
      <Link href="/settings">Options</Link>
    </Button>
  );
}
