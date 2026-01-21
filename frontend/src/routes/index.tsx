import { createFileRoute } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

/**
 * Home page route.
 */
export const Route = createFileRoute('/')({
  component: HomePage,
});

function HomePage() {
  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">SOAP Notice</CardTitle>
          <CardDescription>
            Application de transcription audio pour physiothérapeutes
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <p className="text-center text-muted-foreground">
            Transformez vos enregistrements d'anamnèses en notes SOAP structurées.
          </p>
          <Button className="w-full">
            Commencer
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
