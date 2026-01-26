import { useTranslation } from 'react-i18next';
import { QuotaWidget } from '@/features/billing/components/QuotaWidget';

/**
 * App header component with title and QuotaWidget.
 *
 * Features:
 * - Sticky position at top
 * - App title on the left
 * - QuotaWidget on the right
 * - Consistent height (56px)
 *
 * @returns Header component
 */
export function Header() {
  const { t } = useTranslation('common');

  return (
    <header className="sticky top-0 z-40 border-b bg-background">
      <div className="mx-auto flex h-14 max-w-lg items-center justify-between px-4">
        <h1 className="text-lg font-semibold">{t('appName')}</h1>
        <QuotaWidget />
      </div>
    </header>
  );
}
