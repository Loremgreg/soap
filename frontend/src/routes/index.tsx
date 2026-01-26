import { useEffect, useState } from 'react';
import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ProtectedRoute } from '@/features/auth/components/ProtectedRoute';
import { useAuth } from '@/features/auth';
import { useSubscription, TrialExpiredModal } from '@/features/billing';
import { LanguageSelector } from '@/components/LanguageSelector';

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
  const { user, hasSubscription, logout, isLoggingOut } = useAuth();
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
        <div className="flex min-h-screen items-center justify-center">
          <div className="animate-pulse text-muted-foreground">{tCommon('loading')}</div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Language Selector in top right */}
        <div className="absolute top-4 right-4">
          <LanguageSelector />
        </div>

        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">{t('title')}</CardTitle>
            <CardDescription>
              {user?.name
                ? t('welcomeUser', { name: user.name })
                : t('subtitle')}
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            {/* Quota Display */}
            {subscription && (
              <div className="flex items-center justify-center gap-2">
                <Badge variant={subscription.quotaRemaining > 0 ? 'secondary' : 'destructive'}>
                  {t('visitsRemaining', {
                    remaining: subscription.quotaRemaining,
                    total: subscription.quotaTotal,
                  })}
                </Badge>
                {subscription.status === 'trial' && (
                  <Badge variant="outline" className="text-emerald-600 border-emerald-300">
                    {t('trialBadge')}
                  </Badge>
                )}
              </div>
            )}

            <p className="text-center text-muted-foreground">
              {t('description')}
            </p>

            <Button
              className="w-full min-h-[44px]"
              disabled={subscription?.canRecord === false}
            >
              {subscription?.canRecord === false
                ? t('quotaExhausted')
                : t('startRecording')}
            </Button>

            <Button
              variant="outline"
              className="w-full"
              onClick={logout}
              disabled={isLoggingOut}
            >
              {isLoggingOut ? tCommon('loggingOut') : tCommon('logout')}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Trial Expired Modal */}
      <TrialExpiredModal
        isOpen={showExpiredModal}
        onUpgrade={handleUpgrade}
      />
    </ProtectedRoute>
  );
}
