import { useTranslation } from 'react-i18next';
import { useSubscription } from '../hooks/useSubscription';
import { cn } from '@/lib/utils';
import { Skeleton } from '@/components/ui/skeleton';

/**
 * Determines the color variant based on remaining quota.
 *
 * @param remaining - Number of visits remaining
 * @returns CSS class for the color variant
 */
function getQuotaColorClass(remaining: number): string {
  if (remaining === 0) {
    return 'text-muted-foreground bg-muted';
  }
  if (remaining < 5) {
    return 'text-red-700 bg-red-100 dark:text-red-400 dark:bg-red-950';
  }
  if (remaining <= 10) {
    return 'text-orange-700 bg-orange-100 dark:text-orange-400 dark:bg-orange-950';
  }
  return 'text-emerald-700 bg-emerald-100 dark:text-emerald-400 dark:bg-emerald-950';
}

/**
 * Compact quota display widget for the header.
 *
 * Features:
 * - Shows "X/Y visites" format
 * - Color-coded states: green (>10), orange (5-10), red (<5), gray (0)
 * - Loading skeleton state
 * - Handles missing subscription gracefully
 *
 * @returns QuotaWidget component
 */
export function QuotaWidget() {
  const { t } = useTranslation('common');
  const { data: subscription, isLoading } = useSubscription();

  // Loading state
  if (isLoading) {
    return <Skeleton className="h-6 w-20 rounded-full" />;
  }

  // No subscription - don't show anything
  if (!subscription) {
    return null;
  }

  const { quotaRemaining, quotaTotal } = subscription;
  const isExhausted = quotaRemaining === 0;
  const colorClass = getQuotaColorClass(quotaRemaining);

  return (
    <div
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        colorClass
      )}
    >
      {isExhausted
        ? t('quota.exhausted')
        : t('quota.remaining', { remaining: quotaRemaining, total: quotaTotal })}
    </div>
  );
}
