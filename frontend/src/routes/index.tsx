import { useEffect, useState, useCallback } from 'react';
import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { useTranslation } from 'react-i18next';
import { WifiOff } from 'lucide-react';
import { ProtectedRoute } from '@/features/auth/components/ProtectedRoute';
import { useAuth } from '@/features/auth';
import { useSubscription, TrialExpiredModal } from '@/features/billing';
import { AppShell, PageContainer } from '@/components/layout';
import { RecordButton, Timer, useRecording, useWakeLock, createRecording } from '@/features/recording';
import { useToast } from '@/hooks/use-toast';

/**
 * Home page route.
 *
 * Protected route that requires authentication.
 * Redirects to /login if not authenticated.
 * Redirects to /plan-selection if no subscription.
 * Shows trial expired modal if trial has ended.
 */
export const Route = createFileRoute('/')({
  component: HomePage,
});

/**
 * Home page component with recording functionality.
 *
 * Features:
 * - Large RecordButton for start/pause/stop
 * - Timer display during recording
 * - Wake Lock integration to prevent screen lock
 * - Quota checking before recording
 * - Connection loss warnings
 */
function HomePage() {
  const { t } = useTranslation('common');
  const { t: tHome } = useTranslation('home');
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user, hasSubscription } = useAuth();
  const { data: subscription, isLoading: isLoadingSubscription } = useSubscription();
  const [showExpiredModal, setShowExpiredModal] = useState(false);

  // Wake Lock hook
  const wakeLock = useWakeLock();

  // Default max recording duration (10 minutes)
  // TODO: Get from plan details when API supports it
  const maxRecordingMinutes = 10;

  // Recording hook with callbacks
  const recording = useRecording({
    maxDurationSeconds: maxRecordingMinutes * 60,
    onWarning: () => {
      toast({
        title: t('recording.warningMaxDuration'),
        variant: 'default',
      });
    },
    onMaxDurationReached: () => {
      handleStopRecording();
      toast({
        title: t('recording.limitReached'),
        variant: 'destructive',
      });
    },
  });

  // Redirect to plan selection if no subscription
  useEffect(() => {
    if (!isLoadingSubscription && !hasSubscription && !subscription) {
      navigate({ to: '/plan-selection' });
    }
  }, [hasSubscription, subscription, isLoadingSubscription, navigate]);

  // Show expired trial modal
  useEffect(() => {
    if (subscription?.isTrialExpired) {
      setShowExpiredModal(true);
    }
  }, [subscription?.isTrialExpired]);

  // Show wake lock unavailable warning once
  useEffect(() => {
    if (!wakeLock.isSupported && recording.state === 'idle') {
      // Only show once per session
      const warned = sessionStorage.getItem('wakeLockWarned');
      if (!warned) {
        toast({
          title: t('recording.wakeLockUnavailable'),
          variant: 'default',
        });
        sessionStorage.setItem('wakeLockWarned', 'true');
      }
    }
  }, [wakeLock.isSupported, recording.state, t, toast]);

  // Show connection lost warning
  useEffect(() => {
    if (!recording.isOnline && recording.state === 'recording') {
      toast({
        title: t('recording.connectionLost'),
        variant: 'default',
      });
    }
  }, [recording.isOnline, recording.state, t, toast]);

  // Show permission denied error
  useEffect(() => {
    if (recording.error) {
      toast({
        title: t(recording.error),
        description:
          recording.error === 'recording.permissionDenied'
            ? t('recording.permissionInstructions')
            : undefined,
        variant: 'destructive',
      });
    }
  }, [recording.error, t, toast]);

  /**
   * Handles starting a new recording.
   */
  const handleStartRecording = useCallback(async () => {
    // Request wake lock
    if (wakeLock.isSupported) {
      await wakeLock.request();
    }
    // Start recording
    await recording.controls.start();
  }, [wakeLock, recording.controls]);

  /**
   * Handles stopping the recording.
   */
  const handleStopRecording = useCallback(async () => {
    const audioBlob = await recording.controls.stop();

    // Release wake lock
    if (wakeLock.isSupported) {
      await wakeLock.release();
    }

    if (audioBlob) {
      try {
        toast({
          title: t('recording.processing'),
          variant: 'default',
        });

        // Send to backend for transcription via Deepgram
        const result = await createRecording(audioBlob, recording.duration);

        // Show success with transcript preview
        if (result.status === 'completed' && result.transcriptText) {
          const preview = result.transcriptText.substring(0, 100);
          toast({
            title: t('recording.success'),
            description: preview + (result.transcriptText.length > 100 ? '...' : ''),
            variant: 'default',
          });
        } else if (result.status === 'failed') {
          toast({
            title: t('recording.error'),
            description: t('recording.transcriptionFailed'),
            variant: 'destructive',
          });
        }
      } catch (error) {
        toast({
          title: t('recording.error'),
          description: error instanceof Error ? error.message : t('recording.uploadFailed'),
          variant: 'destructive',
        });
      }
    }
  }, [recording.controls, recording.duration, wakeLock, t, toast]);

  /**
   * Handles the record button click based on current state.
   */
  const handleRecordButtonClick = useCallback(async () => {
    switch (recording.state) {
      case 'idle':
        await handleStartRecording();
        break;
      case 'recording':
        await handleStopRecording();
        break;
      case 'paused':
        recording.controls.resume();
        break;
      default:
        break;
    }
  }, [recording.state, recording.controls, handleStartRecording, handleStopRecording]);

  /**
   * Handles upgrade click from expired modal.
   */
  const handleUpgrade = () => {
    setShowExpiredModal(false);
    navigate({ to: '/plan-selection' });
  };

  // Show loading while checking subscription
  if (isLoadingSubscription) {
    return (
      <ProtectedRoute>
        <AppShell>
          <PageContainer className="flex min-h-[60vh] items-center justify-center">
            <div className="animate-pulse text-muted-foreground">{t('loading')}</div>
          </PageContainer>
        </AppShell>
      </ProtectedRoute>
    );
  }

  // Determine if recording is allowed
  const canRecord = subscription?.canRecord !== false;
  const isRecordingActive = recording.state === 'recording' || recording.state === 'paused';
  const isWarning = recording.duration >= maxRecordingMinutes * 60 - 30;

  return (
    <ProtectedRoute>
      <AppShell>
        <PageContainer className="flex flex-col items-center justify-center py-8">
          {/* Welcome message - hide during recording */}
          {!isRecordingActive && (
            <div className="mb-8 text-center">
              <h2 className="text-xl font-medium text-muted-foreground">
                {user?.name
                  ? tHome('welcomeUser', { name: user.name })
                  : tHome('subtitle')}
              </h2>
            </div>
          )}

          {/* Connection status indicator */}
          {!recording.isOnline && isRecordingActive && (
            <div className="mb-4 flex items-center gap-2 text-orange-500">
              <WifiOff className="h-5 w-5" />
              <span className="text-sm">{t('recording.connectionLost')}</span>
            </div>
          )}

          {/* Timer - visible when recording */}
          {isRecordingActive && (
            <div className="mb-6">
              <Timer duration={recording.duration} isWarning={isWarning} />
            </div>
          )}

          {/* Record Button */}
          <div className="flex flex-col items-center gap-4">
            <RecordButton
              state={recording.state}
              onClick={handleRecordButtonClick}
              disabled={!canRecord}
            />
            <p className="text-sm text-muted-foreground">
              {recording.state === 'recording' && t('recording.recording')}
              {recording.state === 'paused' && t('recording.pause')}
              {recording.state === 'processing' && t('recording.processing')}
              {recording.state === 'idle' &&
                (canRecord ? tHome('startRecording') : tHome('quotaExhausted'))}
            </p>
          </div>

          {/* Pause button - visible during recording */}
          {recording.state === 'recording' && (
            <button
              type="button"
              onClick={() => recording.controls.pause()}
              className="mt-4 text-sm text-muted-foreground hover:text-foreground underline"
            >
              {t('recording.pause')}
            </button>
          )}

          {/* Description - hide during recording */}
          {!isRecordingActive && (
            <p className="mt-8 max-w-xs text-center text-sm text-muted-foreground">
              {tHome('description')}
            </p>
          )}
        </PageContainer>
      </AppShell>

      {/* Trial Expired Modal */}
      <TrialExpiredModal
        isOpen={showExpiredModal}
        onUpgrade={handleUpgrade}
      />
    </ProtectedRoute>
  );
}
