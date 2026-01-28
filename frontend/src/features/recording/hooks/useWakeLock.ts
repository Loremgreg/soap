import { useState, useCallback, useRef, useEffect } from 'react';
import type { UseWakeLockResult } from '../types/recording';

/**
 * Custom hook for managing the Screen Wake Lock API.
 * Prevents the screen from dimming or locking during recording.
 *
 * @returns Wake lock state and control functions
 *
 * @example
 * ```tsx
 * const { isActive, isSupported, request, release } = useWakeLock();
 *
 * // Request when recording starts
 * await request();
 *
 * // Release when recording stops
 * await release();
 * ```
 */
export function useWakeLock(): UseWakeLockResult {
  const [isActive, setIsActive] = useState(false);
  const [isSupported] = useState(() => 'wakeLock' in navigator);
  const wakeLockRef = useRef<WakeLockSentinel | null>(null);
  const releaseHandlerRef = useRef<(() => void) | null>(null);

  /**
   * Cleanup the release event listener.
   */
  const cleanupReleaseHandler = useCallback(() => {
    if (wakeLockRef.current && releaseHandlerRef.current) {
      wakeLockRef.current.removeEventListener('release', releaseHandlerRef.current);
      releaseHandlerRef.current = null;
    }
  }, []);

  /**
   * Request a wake lock to prevent screen from sleeping.
   */
  const request = useCallback(async (): Promise<void> => {
    if (!isSupported) {
      return;
    }

    try {
      // Clean up any existing listener before requesting new lock
      cleanupReleaseHandler();

      wakeLockRef.current = await navigator.wakeLock.request('screen');
      setIsActive(true);

      // Handle wake lock being released by the system
      releaseHandlerRef.current = () => {
        setIsActive(false);
      };
      wakeLockRef.current.addEventListener('release', releaseHandlerRef.current);
    } catch {
      setIsActive(false);
    }
  }, [isSupported, cleanupReleaseHandler]);

  /**
   * Release the current wake lock.
   */
  const release = useCallback(async (): Promise<void> => {
    if (wakeLockRef.current) {
      try {
        cleanupReleaseHandler();
        await wakeLockRef.current.release();
        wakeLockRef.current = null;
        setIsActive(false);
      } catch {
        // Ignore release errors - lock may already be released
      }
    }
  }, [cleanupReleaseHandler]);

  // Re-acquire wake lock when page becomes visible again
  useEffect(() => {
    const handleVisibilityChange = async () => {
      if (
        document.visibilityState === 'visible' &&
        isSupported &&
        isActive &&
        !wakeLockRef.current
      ) {
        // Re-acquire wake lock
        try {
          wakeLockRef.current = await navigator.wakeLock.request('screen');
          releaseHandlerRef.current = () => {
            setIsActive(false);
          };
          wakeLockRef.current.addEventListener('release', releaseHandlerRef.current);
        } catch {
          // Failed to re-acquire - user will be warned via UI
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [isSupported, isActive]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cleanupReleaseHandler();
      if (wakeLockRef.current) {
        wakeLockRef.current.release().catch(() => {
          // Ignore cleanup errors
        });
      }
    };
  }, [cleanupReleaseHandler]);

  return {
    isActive,
    isSupported,
    request,
    release,
  };
}
