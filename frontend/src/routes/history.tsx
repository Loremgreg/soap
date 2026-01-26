import { createFileRoute } from '@tanstack/react-router';
import { useTranslation } from 'react-i18next';
import { Clock } from 'lucide-react';
import { ProtectedRoute } from '@/features/auth/components/ProtectedRoute';
import { AppShell, PageContainer } from '@/components/layout';

/**
 * History page route.
 *
 * Protected route that displays the user's note history.
 * Currently shows a placeholder - will be implemented in Epic 5.
 */
export const Route = createFileRoute('/history')({
  component: HistoryPage,
});

function HistoryPage() {
  const { t } = useTranslation('common');

  return (
    <ProtectedRoute>
      <AppShell>
        <PageContainer className="py-6">
          <h1 className="mb-6 text-2xl font-semibold">{t('history.title')}</h1>

          {/* Empty state placeholder */}
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <div className="mb-4 rounded-full bg-muted p-4">
              <Clock className="h-8 w-8 text-muted-foreground" />
            </div>
            <p className="mb-2 text-lg font-medium text-muted-foreground">
              {t('history.empty')}
            </p>
            <p className="text-sm text-muted-foreground">
              {t('history.emptyAction')}
            </p>
          </div>
        </PageContainer>
      </AppShell>
    </ProtectedRoute>
  );
}
