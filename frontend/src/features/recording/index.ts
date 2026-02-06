/**
 * Recording feature barrel export.
 *
 * This feature provides audio recording functionality including:
 * - RecordButton component with visual states
 * - Timer component for duration display
 * - useRecording hook for MediaRecorder management
 * - useWakeLock hook for screen wake lock
 * - API for recording upload and transcription
 */
export * from './components';
export * from './hooks';
export * from './types/recording';
export * from './api';
