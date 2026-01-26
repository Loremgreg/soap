import { createFileRoute } from '@tanstack/react-router';
import { useTranslation } from 'react-i18next';
import { ProtectedRoute } from '@/features/auth/components/ProtectedRoute';
import { AppShell, PageContainer } from '@/components/layout';
import { LanguageSelector } from '@/components/LanguageSelector';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

/**
 * Settings page route.
 *
 * Protected route that displays user settings.
 * Includes language selection and other preferences.
 */
export const Route = createFileRoute('/settings')({
  component: SettingsPage,
});

function SettingsPage() {
  const { t } = useTranslation('common');

  return (
    <ProtectedRoute>
      <AppShell>
        <PageContainer className="py-6">
          <h1 className="mb-6 text-2xl font-semibold">{t('settings.title')}</h1>

          {/* Language Settings Card */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">{t('settings.languageSection')}</CardTitle>
            </CardHeader>
            <CardContent>
              <LanguageSelector />
            </CardContent>
          </Card>
        </PageContainer>
      </AppShell>
    </ProtectedRoute>
  );
}
