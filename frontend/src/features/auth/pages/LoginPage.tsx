import { useEffect } from 'react';
import { useNavigate, useSearch } from '@tanstack/react-router';
import { useTranslation } from 'react-i18next';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '../hooks/useAuth';
import { GoogleLoginButton } from '../components/GoogleLoginButton';
import { LanguageSelector } from '@/components/LanguageSelector';
import type { LoginSearchParams } from '@/routes/login';

/**
 * Login page component.
 *
 * Displays a centered card with Google OAuth login button.
 * Mobile-first design following AC1 requirements.
 * Handles OAuth error messages via query params.
 */
export function LoginPage() {
  const { t } = useTranslation('auth');
  const { t: tCommon } = useTranslation('common');
  const { toast } = useToast();
  const navigate = useNavigate();
  const { isAuthenticated, isLoading } = useAuth();

  // Get error from query params (if OAuth failed) - type-safe via TanStack Router
  const { error, error_description: errorDescription } =
    useSearch({ from: '/login' }) as LoginSearchParams;

  // Show error toast if OAuth failed
  useEffect(() => {
    if (error) {
      const errorMessages: Record<string, string> = {
        OAUTH_FAILED: t('errors.oauthFailed'),
        OAUTH_CANCELLED: t('errors.oauthCancelled'),
        EMAIL_NOT_VERIFIED: t('errors.emailNotVerified'),
      };

      toast({
        variant: 'destructive',
        title: tCommon('error'),
        description: errorMessages[error] || errorDescription || error,
      });

      // Clear error from URL using TanStack Router
      navigate({ to: '/login', search: {}, replace: true });
    }
  }, [error, errorDescription, toast, navigate, t, tCommon]);

  // Redirect to home if already authenticated
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      navigate({ to: '/' });
    }
  }, [isLoading, isAuthenticated, navigate]);

  return (
    <div className="flex min-h-screen items-center justify-center p-4 bg-gradient-to-b from-background to-muted/30">
      {/* Language Selector in top right */}
      <div className="absolute top-4 right-4">
        <LanguageSelector />
      </div>

      <Card className="w-full max-w-md">
        <CardHeader className="text-center space-y-2">
          <div className="mx-auto mb-4">
            {/* App Logo/Icon */}
            <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
              <span className="text-3xl">🩺</span>
            </div>
          </div>
          <CardTitle className="text-2xl font-bold">{t('login.title')}</CardTitle>
          <CardDescription className="text-base">
            {t('login.subtitle')}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <GoogleLoginButton />

          <p className="text-center text-xs text-muted-foreground">
            {t('login.termsNotice')}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
