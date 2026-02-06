/**
 * API service for recording operations.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Recording status enum.
 */
export type RecordingStatus = 'uploaded' | 'processing' | 'transcribing' | 'completed' | 'failed';

/**
 * Response from the create recording endpoint.
 */
export interface RecordingResponse {
  id: string;
  status: RecordingStatus;
  durationSeconds: number;
  languageDetected: string | null;
  transcriptText: string | null;
  createdAt: string;
}

/**
 * Creates a new recording by uploading audio for transcription.
 *
 * @param audioBlob - The audio blob to upload
 * @param duration - Duration of the recording in seconds
 * @param languageDetected - Optional detected language code
 * @returns The created recording with transcript
 */
export async function createRecording(
  audioBlob: Blob,
  duration: number,
  languageDetected?: string
): Promise<RecordingResponse> {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.webm');
  formData.append('duration', duration.toString());
  if (languageDetected) {
    formData.append('language_detected', languageDetected);
  }

  const url = `${API_BASE_URL}/api/v1/recordings`;

  const response = await fetch(url, {
    method: 'POST',
    credentials: 'include', // Include httpOnly cookies
    body: formData,
    // Do NOT set Content-Type header - browser will set it with boundary for multipart
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error?.message || 'Failed to upload recording');
  }

  return response.json();
}
