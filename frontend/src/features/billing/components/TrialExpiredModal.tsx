/**
 * Modal component displayed when user's trial has expired.
 */

import { useTranslation } from 'react-i18next';
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
  const { t } = useTranslation('billing');

  return (
    <Dialog open={isOpen} onOpenChange={() => {}}>
      <DialogContent className="sm:max-w-md" onPointerDownOutside={(e) => e.preventDefault()}>
        <DialogHeader>
          <DialogTitle>{t('trialExpired.title')}</DialogTitle>
          <DialogDescription>
            {t('trialExpired.description')}
          </DialogDescription>
        </DialogHeader>
        <div className="py-4">
          <div className="rounded-lg bg-muted p-4 text-center">
            <p className="text-sm text-muted-foreground">
              {t('trialExpired.cta')}
            </p>
          </div>
        </div>
        <DialogFooter>
          <Button onClick={onUpgrade} className="w-full min-h-[44px]">
            {t('trialExpired.viewPlans')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
