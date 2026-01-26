/**
 * Card component displaying a subscription plan with its details.
 */

import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { formatPrice } from '@/lib/formatters';
import type { Plan } from '../types';
import { TrialBadge } from './TrialBadge';

interface PlanCardProps {
  /** Plan data from API */
  plan: Plan;
  /** Whether this plan is currently selected */
  isSelected: boolean;
  /** Callback when plan is selected */
  onSelect: (planId: string) => void;
  /** Loading state during trial activation */
  isLoading: boolean;
}

/**
 * Displays a single subscription plan with its details.
 *
 * Features:
 * - Plan name and price prominently displayed
 * - Quota information (visits/month)
 * - Trial badge
 * - Start trial button with loading state
 * - Selected state visual highlight
 * - Mobile-optimized with min 44x44px touch targets
 *
 * @param plan - Plan data from API
 * @param isSelected - Whether this plan is currently selected
 * @param onSelect - Callback when plan is selected
 * @param isLoading - Loading state during trial activation
 */
export function PlanCard({
  plan,
  isSelected,
  onSelect,
  isLoading,
}: PlanCardProps) {
  const { t, i18n } = useTranslation('billing');

  return (
    <Card
      className={`relative transition-all ${
        isSelected
          ? 'ring-2 ring-primary shadow-lg'
          : 'hover:shadow-md'
      }`}
    >
      <CardHeader className="text-center pb-2">
        <div className="flex justify-center mb-2">
          <TrialBadge />
        </div>
        <CardTitle className="text-2xl">{plan.displayName}</CardTitle>
        <CardDescription className="text-3xl font-bold text-foreground mt-2">
          {formatPrice(plan.priceMonthly, i18n.language)}{t('plan.perMonth')}
        </CardDescription>
      </CardHeader>
      <CardContent className="text-center">
        <div className="space-y-2 text-muted-foreground">
          <p className="text-lg font-medium text-foreground">
            {t('plan.visitsPerMonth', { count: plan.quotaMonthly })}
          </p>
          <p>{t('plan.recordingUpTo', { minutes: plan.maxRecordingMinutes })}</p>
          <p>{t('plan.notesRetention', { count: plan.maxNotesRetention })}</p>
        </div>
      </CardContent>
      <CardFooter className="pt-4">
        <Button
          className="w-full min-h-[44px] text-base font-semibold"
          onClick={() => onSelect(plan.id)}
          disabled={isLoading}
          variant={isSelected ? 'default' : 'outline'}
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
              {t('trial.activating')}
            </span>
          ) : (
            t('trial.startTrial')
          )}
        </Button>
      </CardFooter>
    </Card>
  );
}
