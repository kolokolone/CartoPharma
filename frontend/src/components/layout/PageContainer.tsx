import { cn } from '@/lib/utils';

export type ContainerVariant = 'default' | 'wide';

const VARIANT_CLASSES: Record<ContainerVariant, string> = {
  default: 'max-w-6xl',
  wide: 'max-w-[88rem]',
};

type PageContainerProps = {
  children: React.ReactNode;
  variant: ContainerVariant;
};

export function PageContainer({ children, variant }: PageContainerProps) {
  return <div className={cn('mx-auto w-full px-4 py-6 sm:px-6 lg:px-8', VARIANT_CLASSES[variant])}>{children}</div>;
}
