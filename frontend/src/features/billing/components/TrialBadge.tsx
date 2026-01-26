/**
 * Badge component displaying trial period text.
 */

import { useTranslation } from 'react-i18next';
import { Badge } from '@/components/ui/badge';

interface TrialBadgeProps {
  className?: string;
}

/**
 * Displays the free trial badge with a green/teal accent.
 *
 * @param className - Additional CSS classes
 */
export function TrialBadge({ className }: TrialBadgeProps) {
  const { t } = useTranslation('billing');

  return (
    <Badge
      variant="secondary"
      className={`bg-emerald-100 text-emerald-700 hover:bg-emerald-100 border-emerald-200 ${className ?? ''}`}
    >
      {t('trial.badge')}
    </Badge>
  );
}
