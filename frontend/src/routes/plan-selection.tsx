import { createFileRoute } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { ProtectedRoute } from '@/features/auth/components/ProtectedRoute';
import { useAuth } from '@/features/auth';

/**
 * Plan selection page route.
 *
 * Shown to new users after OAuth signup to select their subscription plan.
 */
export const Route = createFileRoute('/plan-selection')({
  component: PlanSelectionPage,
});

function PlanSelectionPage() {
  const { user } = useAuth();

  return (
    <ProtectedRoute>
      <div className="flex min-h-screen items-center justify-center p-4">
        <Card className="w-full max-w-2xl">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">
              Bienvenue{user?.name ? `, ${user.name}` : ''} !
            </CardTitle>
            <CardDescription>
              Choisissez votre formule pour commencer à utiliser SOAP Notice.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-center text-muted-foreground">
              Les plans de souscription seront disponibles prochainement.
            </p>
            <div className="flex justify-center">
              <Button asChild>
                <a href="/">Continuer avec l'essai gratuit</a>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </ProtectedRoute>
  );
}
