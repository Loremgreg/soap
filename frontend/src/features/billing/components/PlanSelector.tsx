/**
 * Container component for plan selection with loading and error states.
 */

import { Skeleton } from '@/components/ui/skeleton';
import type { Plan } from '../types';
import { PlanCard } from './PlanCard';

interface PlanSelectorProps {
  /** List of available plans */
  plans: Plan[];
  /** Currently selected plan ID */
  selectedPlanId: string | null;
  /** Callback when a plan is selected */
  onSelectPlan: (planId: string) => void;
  /** Loading state for plans fetch */
  isLoading: boolean;
  /** Loading state for trial activation */
  isActivating: boolean;
  /** Error message if fetch failed */
  error: string | null;
}

/**
 * Loading skeleton for plan cards.
 */
function PlanCardSkeleton() {
  return (
    <div className="rounded-xl border bg-card p-6 space-y-4">
      <div className="flex justify-center">
        <Skeleton className="h-5 w-32" />
      </div>
      <Skeleton className="h-8 w-24 mx-auto" />
      <Skeleton className="h-10 w-32 mx-auto" />
      <div className="space-y-2">
        <Skeleton className="h-4 w-28 mx-auto" />
        <Skeleton className="h-4 w-36 mx-auto" />
        <Skeleton className="h-4 w-32 mx-auto" />
      </div>
      <Skeleton className="h-11 w-full mt-4" />
    </div>
  );
}

/**
 * Displays the plan selection grid with loading, error, and empty states.
 *
 * @param plans - List of available plans
 * @param selectedPlanId - Currently selected plan ID
 * @param onSelectPlan - Callback when a plan is selected
 * @param isLoading - Loading state for plans fetch
 * @param isActivating - Loading state for trial activation
 * @param error - Error message if fetch failed
 */
export function PlanSelector({
  plans,
  selectedPlanId,
  onSelectPlan,
  isLoading,
  isActivating,
  error,
}: PlanSelectorProps) {
  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-destructive font-medium">
          Une erreur est survenue lors du chargement des plans.
        </p>
        <p className="text-muted-foreground mt-2">{error}</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="grid gap-6 md:grid-cols-2 max-w-3xl mx-auto">
        <PlanCardSkeleton />
        <PlanCardSkeleton />
      </div>
    );
  }

  if (plans.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">
          Aucun plan disponible pour le moment.
        </p>
      </div>
    );
  }

  return (
    <div className="grid gap-6 md:grid-cols-2 max-w-3xl mx-auto">
      {plans.map((plan) => (
        <PlanCard
          key={plan.id}
          plan={plan}
          isSelected={selectedPlanId === plan.id}
          onSelect={onSelectPlan}
          isLoading={isActivating && selectedPlanId === plan.id}
        />
      ))}
    </div>
  );
}
