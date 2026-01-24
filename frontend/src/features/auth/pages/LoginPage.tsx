import { useEffect } from 'react';
import { useNavigate, useSearch } from '@tanstack/react-router';
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
import type { LoginSearchParams } from '@/routes/login';

/**
 * Login page component.
 *
 * Displays a centered card with Google OAuth login button.
 * Mobile-first design following AC1 requirements.
 * Handles OAuth error messages via query params.
 */
export function LoginPage() {
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
        OAUTH_FAILED: "L'authentification Google a échoué. Veuillez réessayer.",
        OAUTH_CANCELLED: 'Authentification annulée.',
        EMAIL_NOT_VERIFIED: "Votre adresse email n'est pas vérifiée par Google. Veuillez vérifier votre email.",
      };

      toast({
        variant: 'destructive',
        title: 'Erreur de connexion',
        description: errorMessages[error] || errorDescription || error,
      });

      // Clear error from URL using TanStack Router
      navigate({ to: '/login', search: {}, replace: true });
    }
  }, [error, errorDescription, toast, navigate]);

  // Redirect to home if already authenticated
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      navigate({ to: '/' });
    }
  }, [isLoading, isAuthenticated, navigate]);

  return (
    <div className="flex min-h-screen items-center justify-center p-4 bg-gradient-to-b from-background to-muted/30">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center space-y-2">
          <div className="mx-auto mb-4">
            {/* App Logo/Icon */}
            <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
              <span className="text-3xl">🩺</span>
            </div>
          </div>
          <CardTitle className="text-2xl font-bold">SOAP Notice</CardTitle>
          <CardDescription className="text-base">
            Application de transcription audio pour physiothérapeutes
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <p className="text-center text-muted-foreground text-sm">
            Connectez-vous pour accéder à vos notes et enregistrements.
          </p>

          <GoogleLoginButton />

          <p className="text-center text-xs text-muted-foreground">
            En vous connectant, vous acceptez nos{' '}
            <a href="/terms" className="underline hover:text-primary">
              conditions d'utilisation
            </a>{' '}
            et notre{' '}
            <a href="/privacy" className="underline hover:text-primary">
              politique de confidentialité
            </a>
            .
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
