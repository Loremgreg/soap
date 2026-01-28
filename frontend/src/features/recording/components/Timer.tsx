import { cn } from '@/lib/utils';

/**
 * Props for the Timer component.
 */
export interface TimerProps {
  /** Duration in seconds */
  duration: number;
  /** Whether to show warning style (last 30 seconds) */
  isWarning?: boolean;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Formats seconds into a time string.
 * Returns MM:SS for durations under 1 hour, HH:MM:SS otherwise.
 *
 * @param seconds - Total seconds to format
 * @returns Formatted time string
 */
export function formatTime(seconds: number): string {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  const pad = (n: number): string => n.toString().padStart(2, '0');

  if (hrs > 0) {
    return `${pad(hrs)}:${pad(mins)}:${pad(secs)}`;
  }
  return `${pad(mins)}:${pad(secs)}`;
}

/**
 * Displays the recording duration in a large, readable format.
 * Shows warning colors when approaching max duration.
 *
 * @param duration - Duration in seconds
 * @param isWarning - Whether to show warning style
 * @param className - Additional CSS classes
 */
export function Timer({ duration, isWarning = false, className }: TimerProps) {
  return (
    <div
      className={cn(
        // Large typography for mobile readability
        'text-3xl font-mono font-bold tabular-nums md:text-4xl',
        // Color based on warning state
        isWarning ? 'text-orange-500' : 'text-muted-foreground',
        // Transition for smooth color change
        'transition-colors duration-300',
        className
      )}
      role="timer"
      aria-live="polite"
      aria-atomic="true"
    >
      {formatTime(duration)}
    </div>
  );
}
