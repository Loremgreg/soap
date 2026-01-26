import { useState } from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { useTranslation } from 'react-i18next';
import { ProtectedRoute } from '@/features/auth/components/ProtectedRoute';
import { useAuth } from '@/features/auth';
import {
  PlanSelector,
  usePlans,
  useCreateTrialSubscription,
} from '@/features/billing';
import { LanguageSelector } from '@/components/LanguageSelector';

/**
 * Plan selection page route.
 *
 * Shown to new users after OAuth signup to select their subscription plan.
 * Displays two plan options (Starter and Pro) with trial activation.
 */
export const Route = createFileRoute('/plan-selection')({
  component: PlanSelectionPage,
});

function PlanSelectionPage() {
  const { t } = useTranslation('billing');
  const { user } = useAuth();
  const { data: plans = [], isLoading, error } = usePlans();
  const createTrial = useCreateTrialSubscription();
  const [selectedPlanId, setSelectedPlanId] = useState<string | null>(null);

  /**
   * Handles plan selection and trial activation.
   *
   * @param planId - UUID of the selected plan
   */
  const handleSelectPlan = (planId: string) => {
    setSelectedPlanId(planId);
    createTrial.mutate({ planId });
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-b from-background to-muted/30 px-4 py-8 md:py-16">
        {/* Language Selector in top right */}
        <div className="absolute top-4 right-4">
          <LanguageSelector />
        </div>

        <div className="mx-auto max-w-4xl">
          {/* Header */}
          <div className="text-center mb-8 md:mb-12">
            <h1 className="text-3xl md:text-4xl font-bold tracking-tight mb-3">
              {t('planSelection.welcome', { name: user?.name ? t('planSelection.welcomeWithName', { name: user.name }) : '' })}
            </h1>
            <p className="text-lg text-muted-foreground max-w-xl mx-auto">
              {t('planSelection.subtitle')}
            </p>
          </div>

          {/* Plans Grid */}
          <PlanSelector
            plans={plans}
            selectedPlanId={selectedPlanId}
            onSelectPlan={handleSelectPlan}
            isLoading={isLoading}
            isActivating={createTrial.isPending}
            error={error?.message ?? null}
          />

          {/* Footer Note */}
          <div className="mt-8 text-center text-sm text-muted-foreground">
            <p>
              {t('planSelection.noCreditCard')}
            </p>
            <p className="mt-1">
              {t('planSelection.cancelAnytime')}
            </p>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
