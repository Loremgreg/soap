/**
 * Recording feature type definitions.
 */

/**
 * Possible states of the recording interface.
 */
export type RecordingState = 'idle' | 'recording' | 'paused' | 'processing';

/**
 * Audio chunk collected during recording.
 */
export interface AudioChunk {
  /** The audio data blob */
  data: Blob;
  /** Timestamp when the chunk was recorded */
  timestamp: number;
}

/**
 * Recording controls returned by the useRecording hook.
 */
export interface RecordingControls {
  /** Start a new recording */
  start: () => Promise<void>;
  /** Pause the current recording */
  pause: () => void;
  /** Resume a paused recording */
  resume: () => void;
  /** Stop the recording and return the audio blob */
  stop: () => Promise<Blob | null>;
}

/**
 * Recording hook state and controls.
 */
export interface UseRecordingResult {
  /** Current recording state */
  state: RecordingState;
  /** Duration in seconds */
  duration: number;
  /** Error message if any */
  error: string | null;
  /** Whether microphone permission is granted */
  hasPermission: boolean | null;
  /** Whether the device is online */
  isOnline: boolean;
  /** Recording control functions */
  controls: RecordingControls;
}

/**
 * Wake lock hook result.
 */
export interface UseWakeLockResult {
  /** Whether wake lock is active */
  isActive: boolean;
  /** Whether the API is supported */
  isSupported: boolean;
  /** Request wake lock */
  request: () => Promise<void>;
  /** Release wake lock */
  release: () => Promise<void>;
}
