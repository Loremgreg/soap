import { useState, useCallback, useRef, useEffect } from 'react';
import type {
  RecordingState,
  UseRecordingResult,
  RecordingControls,
} from '../types/recording';

/** Default MIME type for audio recording */
const DEFAULT_MIME_TYPE = 'audio/webm;codecs=opus';

/** Chunk interval in milliseconds for real-time streaming */
const CHUNK_INTERVAL_MS = 250;

/**
 * Gets the best supported MIME type for audio recording.
 *
 * @returns Supported MIME type or empty string if none supported
 */
function getSupportedMimeType(): string {
  const types = [
    'audio/webm;codecs=opus',
    'audio/webm',
    'audio/ogg;codecs=opus',
    'audio/mp4',
  ];

  for (const type of types) {
    if (MediaRecorder.isTypeSupported(type)) {
      return type;
    }
  }

  // No preferred MIME type supported, browser will use default
  return '';
}

/**
 * Custom hook for managing audio recording using the MediaRecorder API.
 *
 * Features:
 * - Start, pause, resume, and stop recording
 * - Real-time audio chunks (250ms intervals) for streaming
 * - Online/offline detection
 * - Microphone permission handling
 * - Timer management
 *
 * @param maxDurationSeconds - Maximum recording duration in seconds (default: 600 = 10 min)
 * @param onWarning - Callback when approaching max duration (30s before)
 * @param onMaxDurationReached - Callback when max duration is reached
 *
 * @returns Recording state, duration, controls, and error information
 *
 * @example
 * ```tsx
 * const { state, duration, controls, error } = useRecording({
 *   maxDurationSeconds: 600,
 *   onWarning: () => toast('Recording will stop soon'),
 *   onMaxDurationReached: () => toast('Max duration reached'),
 * });
 *
 * // Start recording
 * await controls.start();
 *
 * // Stop and get audio blob
 * const audioBlob = await controls.stop();
 * ```
 */
export function useRecording(options?: {
  maxDurationSeconds?: number;
  onWarning?: () => void;
  onMaxDurationReached?: () => void;
}): UseRecordingResult {
  const {
    maxDurationSeconds = 600,
    onWarning,
    onMaxDurationReached,
  } = options ?? {};

  // State
  const [state, setState] = useState<RecordingState>('idle');
  const [duration, setDuration] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  // Refs
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const startTimeRef = useRef<number>(0);
  const pausedDurationRef = useRef<number>(0);
  const warningShownRef = useRef(false);
  const maxDurationReachedRef = useRef(false);

  // Online/offline detection
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  /**
   * Starts the timer interval.
   */
  const startTimer = useCallback(() => {
    startTimeRef.current = Date.now() - pausedDurationRef.current * 1000;
    warningShownRef.current = false;
    maxDurationReachedRef.current = false;

    timerRef.current = setInterval(() => {
      const elapsed = Math.floor(
        (Date.now() - startTimeRef.current) / 1000
      );
      setDuration(elapsed);

      // Warning at 30 seconds before max
      const warningThreshold = maxDurationSeconds - 30;
      if (elapsed >= warningThreshold && !warningShownRef.current) {
        warningShownRef.current = true;
        onWarning?.();
      }

      // Auto-stop at max duration - stop timer FIRST to prevent race condition
      if (elapsed >= maxDurationSeconds && !maxDurationReachedRef.current) {
        maxDurationReachedRef.current = true;
        // Clear interval immediately to prevent callback being called again
        if (timerRef.current) {
          clearInterval(timerRef.current);
          timerRef.current = null;
        }
        onMaxDurationReached?.();
      }
    }, 1000);
  }, [maxDurationSeconds, onWarning, onMaxDurationReached]);

  /**
   * Stops the timer interval.
   */
  const stopTimer = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  /**
   * Requests microphone permission and starts recording.
   */
  const start = useCallback(async (): Promise<void> => {
    setError(null);
    chunksRef.current = [];

    try {
      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      streamRef.current = stream;
      setHasPermission(true);

      // Get supported MIME type
      const mimeType = getSupportedMimeType();
      const options: MediaRecorderOptions = mimeType ? { mimeType } : {};

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, options);
      mediaRecorderRef.current = mediaRecorder;

      // Handle data available - collect chunks for streaming
      mediaRecorder.addEventListener('dataavailable', (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      });

      // Handle recording stop
      mediaRecorder.addEventListener('stop', () => {
        // Stream tracks will be stopped in the stop function
      });

      // Handle errors
      mediaRecorder.addEventListener('error', () => {
        setError('recording.error');
        setState('idle');
        stopTimer();
      });

      // Start recording with 250ms chunks for real-time streaming
      mediaRecorder.start(CHUNK_INTERVAL_MS);
      setState('recording');
      pausedDurationRef.current = 0;
      startTimer();
    } catch (err) {
      if (err instanceof DOMException) {
        if (err.name === 'NotAllowedError') {
          setHasPermission(false);
          setError('recording.permissionDenied');
        } else if (err.name === 'NotFoundError') {
          setError('recording.error');
        } else {
          setError('recording.error');
        }
      } else {
        setError('recording.error');
      }

      setState('idle');
    }
  }, [startTimer, stopTimer]);

  /**
   * Pauses the current recording.
   */
  const pause = useCallback((): void => {
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.pause();
      setState('paused');
      pausedDurationRef.current = duration;
      stopTimer();
    }
  }, [duration, stopTimer]);

  /**
   * Resumes a paused recording.
   */
  const resume = useCallback((): void => {
    if (mediaRecorderRef.current?.state === 'paused') {
      mediaRecorderRef.current.resume();
      setState('recording');
      startTimer();
    }
  }, [startTimer]);

  /**
   * Stops the recording and returns the audio blob.
   */
  const stop = useCallback(async (): Promise<Blob | null> => {
    return new Promise((resolve) => {
      stopTimer();

      if (!mediaRecorderRef.current || mediaRecorderRef.current.state === 'inactive') {
        setState('idle');
        resolve(null);
        return;
      }

      setState('processing');

      // Wait for the stop event to get all data
      mediaRecorderRef.current.addEventListener(
        'stop',
        () => {
          // Combine all chunks into a single blob
          const mimeType = mediaRecorderRef.current?.mimeType || DEFAULT_MIME_TYPE;
          const audioBlob = new Blob(chunksRef.current, { type: mimeType });

          // Stop all tracks
          streamRef.current?.getTracks().forEach((track) => track.stop());

          // Cleanup
          mediaRecorderRef.current = null;
          streamRef.current = null;

          setState('idle');
          setDuration(0);
          pausedDurationRef.current = 0;
          chunksRef.current = [];

          resolve(audioBlob);
        },
        { once: true }
      );

      mediaRecorderRef.current.stop();
    });
  }, [stopTimer]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopTimer();
      if (mediaRecorderRef.current?.state !== 'inactive') {
        mediaRecorderRef.current?.stop();
      }
      streamRef.current?.getTracks().forEach((track) => track.stop());
    };
  }, [stopTimer]);

  const controls: RecordingControls = {
    start,
    pause,
    resume,
    stop,
  };

  return {
    state,
    duration,
    error,
    hasPermission,
    isOnline,
    controls,
  };
}
