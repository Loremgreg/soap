import { useTranslation } from 'react-i18next';
import { Mic, Square, Play, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { RecordingState } from '../types/recording';

/**
 * Props for the RecordButton component.
 */
export interface RecordButtonProps {
  /** Current recording state */
  state: RecordingState;
  /** Callback when record/stop/resume is clicked */
  onClick: () => void;
  /** Whether the button is disabled */
  disabled?: boolean;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Large circular button for recording audio.
 * Displays different icons and styles based on recording state.
 *
 * States:
 * - idle: Mic icon, primary color, ready to record
 * - recording: Stop icon, red accent, pulse animation
 * - paused: Play icon, orange accent, ready to resume
 * - processing: Spinner icon, disabled state
 *
 * @param state - Current recording state
 * @param onClick - Callback when button is clicked
 * @param disabled - Whether the button is disabled
 * @param className - Additional CSS classes
 */
export function RecordButton({
  state,
  onClick,
  disabled = false,
  className,
}: RecordButtonProps) {
  const { t } = useTranslation('common');

  /**
   * Get the icon component based on current state.
   */
  const getIcon = () => {
    switch (state) {
      case 'recording':
        return <Square className="h-8 w-8 fill-current" />;
      case 'paused':
        return <Play className="h-8 w-8 fill-current" />;
      case 'processing':
        return <Loader2 className="h-8 w-8 animate-spin" />;
      case 'idle':
      default:
        return <Mic className="h-8 w-8" />;
    }
  };

  /**
   * Get the accessible label based on current state.
   */
  const getLabel = (): string => {
    switch (state) {
      case 'recording':
        return t('recording.stop');
      case 'paused':
        return t('recording.resume');
      case 'processing':
        return t('recording.processing');
      case 'idle':
      default:
        return t('recording.start');
    }
  };

  /**
   * Get button styles based on current state.
   */
  const getStateStyles = (): string => {
    switch (state) {
      case 'recording':
        return 'bg-red-500 hover:bg-red-600 text-white recording-pulse';
      case 'paused':
        return 'bg-orange-500 hover:bg-orange-600 text-white';
      case 'processing':
        return 'bg-gray-400 text-white cursor-not-allowed';
      case 'idle':
      default:
        return 'bg-primary hover:bg-primary/90 text-primary-foreground';
    }
  };

  const isDisabled = disabled || state === 'processing';

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={isDisabled}
      aria-label={getLabel()}
      className={cn(
        // Base styles - large circular button with min 80x80px
        'flex h-20 w-20 items-center justify-center rounded-full',
        // Touch target (44x44px minimum is exceeded)
        'min-h-[80px] min-w-[80px]',
        // Focus and transition
        'transition-all duration-200',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
        // Disabled state
        'disabled:pointer-events-none disabled:opacity-50',
        // Shadow for depth
        'shadow-lg hover:shadow-xl',
        // State-specific styles
        getStateStyles(),
        className
      )}
    >
      {getIcon()}
    </button>
  );
}
