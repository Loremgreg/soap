import { Link, useLocation } from '@tanstack/react-router';
import { useTranslation } from 'react-i18next';
import { Mic, Clock, Settings } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Navigation item configuration.
 */
interface NavItem {
  to: string;
  labelKey: string;
  icon: React.ComponentType<{ className?: string }>;
}

/**
 * Navigation items for the bottom nav bar.
 */
const navItems: NavItem[] = [
  { to: '/', labelKey: 'nav.home', icon: Mic },
  { to: '/history', labelKey: 'nav.history', icon: Clock },
  { to: '/settings', labelKey: 'nav.settings', icon: Settings },
];

/**
 * Bottom navigation component with Home, History, and Settings tabs.
 *
 * Features:
 * - Fixed to bottom of screen
 * - 3 navigation items with icons and labels
 * - Active state highlighting
 * - Minimum 44x44px touch targets
 * - Safe area inset for notched devices
 *
 * @returns Bottom navigation bar component
 */
export function BottomNav() {
  const { t } = useTranslation('common');
  const location = useLocation();

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-50 border-t bg-background"
      style={{ paddingBottom: 'env(safe-area-inset-bottom, 0px)' }}
    >
      <div className="mx-auto flex h-14 max-w-lg items-center justify-around">
        {navItems.map((item) => {
          const isActive = location.pathname === item.to;
          const Icon = item.icon;

          return (
            <Link
              key={item.to}
              to={item.to}
              className={cn(
                'flex min-h-[44px] min-w-[44px] flex-1 flex-col items-center justify-center gap-1 transition-colors',
                isActive
                  ? 'text-primary'
                  : 'text-muted-foreground hover:text-foreground'
              )}
            >
              <Icon className="h-5 w-5" />
              <span className="text-xs font-medium">{t(item.labelKey)}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
