/**
 * Badge component displaying "Essai gratuit 7 jours" for trial period.
 */

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
  return (
    <Badge
      variant="secondary"
      className={`bg-emerald-100 text-emerald-700 hover:bg-emerald-100 border-emerald-200 ${className ?? ''}`}
    >
      Essai gratuit 7 jours
    </Badge>
  );
}
