import { useEffect, useState } from 'react';
import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { useTranslation } from 'react-i18next';
import { Mic } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ProtectedRoute } from '@/features/auth/components/ProtectedRoute';
import { useAuth } from '@/features/auth';
import { useSubscription, TrialExpiredModal } from '@/features/billing';
import { AppShell, PageContainer } from '@/components/layout';

/**
 * Home page route.
 *
 * Protected route that requires authentication.
 * Redirects to /login if not authenticated.
 * Redirects to /plan-selection if no subscription.
 * Shows trial expired modal if trial has ended.
 */
export const Route = createFileRoute('/')({
  component: HomePage,
});

function HomePage() {
  const { t } = useTranslation('home');
  const { t: tCommon } = useTranslation('common');
  const navigate = useNavigate();
  const { user, hasSubscription } = useAuth();
  const { data: subscription, isLoading: isLoadingSubscription } = useSubscription();
  const [showExpiredModal, setShowExpiredModal] = useState(false);

  // Redirect to plan selection if no subscription
  useEffect(() => {
    if (!isLoadingSubscription && !hasSubscription && !subscription) {
      navigate({ to: '/plan-selection' });
    }
  }, [hasSubscription, subscription, isLoadingSubscription, navigate]);

  // Show expired trial modal
  useEffect(() => {
    if (subscription?.isTrialExpired) {
      setShowExpiredModal(true);
    }
  }, [subscription?.isTrialExpired]);

  /**
   * Handles upgrade click from expired modal.
   */
  const handleUpgrade = () => {
    setShowExpiredModal(false);
    navigate({ to: '/plan-selection' });
  };

  // Show loading while checking subscription
  if (isLoadingSubscription) {
    return (
      <ProtectedRoute>
        <AppShell>
          <PageContainer className="flex min-h-[60vh] items-center justify-center">
            <div className="animate-pulse text-muted-foreground">{tCommon('loading')}</div>
          </PageContainer>
        </AppShell>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <AppShell>
        <PageContainer className="flex flex-col items-center justify-center py-8">
          {/* Welcome message */}
          <div className="mb-8 text-center">
            <h2 className="text-xl font-medium text-muted-foreground">
              {user?.name
                ? t('welcomeUser', { name: user.name })
                : t('subtitle')}
            </h2>
          </div>

          {/* Record Button - Large centered button */}
          <div className="flex flex-col items-center gap-4">
            <Button
              size="lg"
              className="h-20 w-20 rounded-full"
              disabled={subscription?.canRecord === false}
            >
              <Mic className="h-8 w-8" />
            </Button>
            <p className="text-sm text-muted-foreground">
              {subscription?.canRecord === false
                ? t('quotaExhausted')
                : t('startRecording')}
            </p>
          </div>

          {/* Description */}
          <p className="mt-8 max-w-xs text-center text-sm text-muted-foreground">
            {t('description')}
          </p>
        </PageContainer>
      </AppShell>

      {/* Trial Expired Modal */}
      <TrialExpiredModal
        isOpen={showExpiredModal}
        onUpgrade={handleUpgrade}
      />
    </ProtectedRoute>
  );
}
