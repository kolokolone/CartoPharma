'use client';

import { Search } from 'lucide-react';

import { Button } from '@/components/ui/button';

type SearchBarProps = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  isSubmitting?: boolean;
};

export function SearchBar({ value, onChange, onSubmit, isSubmitting = false }: SearchBarProps) {
  return (
    <form
      className='flex flex-col gap-3 sm:flex-row'
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
    >
      <label className='sr-only' htmlFor='search-input'>
        Recherche
      </label>
      <div className='relative flex-1'>
        <Search className='pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground' />
        <input
          id='search-input'
          type='search'
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder='Pharmacie, ville, couche, identifiant…'
          className='h-11 w-full rounded-md border border-input bg-background pl-10 pr-3 text-sm outline-none ring-offset-background placeholder:text-muted-foreground focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2'
        />
      </div>
      <Button type='submit' className='sm:min-w-32' disabled={isSubmitting}>
        {isSubmitting ? 'Recherche…' : 'Rechercher'}
      </Button>
    </form>
  );
}
