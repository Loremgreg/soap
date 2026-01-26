import { cn } from '@/lib/utils';

/**
 * Props for PageContainer component.
 */
interface PageContainerProps {
  children: React.ReactNode;
  className?: string;
}

/**
 * Content wrapper component with proper padding for header and bottom nav.
 *
 * Features:
 * - Adds padding-bottom for bottom nav (56px + safe area)
 * - Centers content with max-width
 * - Provides consistent horizontal padding
 *
 * @param props - Component props
 * @param props.children - Page content
 * @param props.className - Additional CSS classes
 * @returns Page container component
 */
export function PageContainer({ children, className }: PageContainerProps) {
  return (
    <main
      className={cn('mx-auto max-w-lg px-4 pb-20', className)}
      style={{ paddingBottom: 'calc(56px + env(safe-area-inset-bottom, 0px) + 1rem)' }}
    >
      {children}
    </main>
  );
}
