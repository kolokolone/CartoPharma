'use client';

import { Heart } from 'lucide-react';

import { Button } from '@/components/ui/button';

type PharmacyFavoriteButtonProps = {
  isFavorite: boolean;
  isPending: boolean;
  onToggle: () => void;
};

export function PharmacyFavoriteButton({ isFavorite, isPending, onToggle }: PharmacyFavoriteButtonProps) {
  return (
    <Button type='button' variant={isFavorite ? 'default' : 'outline'} size='sm' onClick={onToggle} disabled={isPending}>
      <Heart className='mr-2 h-4 w-4' fill={isFavorite ? 'currentColor' : 'none'} />
      {isPending ? 'Mise à jour…' : isFavorite ? 'Retirer des favoris' : 'Ajouter aux favoris'}
    </Button>
  );
}
