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
 * Home page route.
 *
 * Protected route that requires authentication.
 * Redirects to /login if not authenticated.
 */
export const Route = createFileRoute('/')({
  component: HomePage,
});

function HomePage() {
  const { user, logout, isLoggingOut } = useAuth();

  return (
    <ProtectedRoute>
      <div className="flex min-h-screen items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">SOAP Notice</CardTitle>
            <CardDescription>
              {user?.name
                ? `Bienvenue, ${user.name}!`
                : 'Application de transcription audio pour physiothérapeutes'}
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <p className="text-center text-muted-foreground">
              Transformez vos enregistrements d'anamnèses en notes SOAP
              structurées.
            </p>
            <Button className="w-full">Commencer un enregistrement</Button>
            <Button
              variant="outline"
              className="w-full"
              onClick={logout}
              disabled={isLoggingOut}
            >
              {isLoggingOut ? 'Déconnexion...' : 'Se déconnecter'}
            </Button>
          </CardContent>
        </Card>
      </div>
    </ProtectedRoute>
  );
}
