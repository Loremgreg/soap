import { cn } from '@/lib/utils';

/**
 * Skeleton component for loading states.
 *
 * @param className - Additional CSS classes
 */
function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn('animate-pulse rounded-md bg-primary/10', className)}
      {...props}
    />
  );
}

export { Skeleton };
