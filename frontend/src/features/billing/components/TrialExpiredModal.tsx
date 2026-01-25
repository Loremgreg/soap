/**
 * Modal component displayed when user's trial has expired.
 */

import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

interface TrialExpiredModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Callback when user clicks upgrade button */
  onUpgrade: () => void;
}

/**
 * Displays a modal prompting user to subscribe after trial expiration.
 *
 * @param isOpen - Whether the modal is open
 * @param onUpgrade - Callback when user clicks upgrade button
 */
export function TrialExpiredModal({ isOpen, onUpgrade }: TrialExpiredModalProps) {
  return (
    <Dialog open={isOpen} onOpenChange={() => {}}>
      <DialogContent className="sm:max-w-md" onPointerDownOutside={(e) => e.preventDefault()}>
        <DialogHeader>
          <DialogTitle>Votre période d'essai est terminée</DialogTitle>
          <DialogDescription>
            Votre essai gratuit de 7 jours est arrivé à son terme. Pour continuer
            à utiliser SOAP Notice et générer des notes, veuillez souscrire à un
            abonnement.
          </DialogDescription>
        </DialogHeader>
        <div className="py-4">
          <div className="rounded-lg bg-muted p-4 text-center">
            <p className="text-sm text-muted-foreground">
              Choisissez le plan qui vous convient et continuez à gagner du temps
              sur vos comptes-rendus.
            </p>
          </div>
        </div>
        <DialogFooter>
          <Button onClick={onUpgrade} className="w-full min-h-[44px]">
            Voir les plans
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
