const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Error response format from the API.
 */
export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

/**
 * Custom error class for API errors.
 */
export class ApiRequestError extends Error {
  code: string;
  details?: Record<string, unknown>;
  status: number;

  constructor(error: ApiError['error'], status: number) {
    super(error.message);
    this.name = 'ApiRequestError';
    this.code = error.code;
    this.details = error.details;
    this.status = status;
  }
}

/**
 * Makes an authenticated API request.
 *
 * @param endpoint - API endpoint (without base URL)
 * @param options - Fetch options
 * @returns Response data
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}/api/v1${endpoint}`;

  const response = await fetch(url, {
    ...options,
    credentials: 'include', // Include httpOnly cookies
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorData = (await response.json()) as ApiError;
    throw new ApiRequestError(errorData.error, response.status);
  }

  return response.json() as Promise<T>;
}

/**
 * GET request helper.
 *
 * @param endpoint - API endpoint
 * @returns Response data
 */
export function get<T>(endpoint: string): Promise<T> {
  return apiRequest<T>(endpoint, { method: 'GET' });
}

/**
 * POST request helper.
 *
 * @param endpoint - API endpoint
 * @param data - Request body
 * @returns Response data
 */
export function post<T>(endpoint: string, data?: unknown): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * PUT request helper.
 *
 * @param endpoint - API endpoint
 * @param data - Request body
 * @returns Response data
 */
export function put<T>(endpoint: string, data?: unknown): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * DELETE request helper.
 *
 * @param endpoint - API endpoint
 * @returns Response data
 */
export function del<T>(endpoint: string): Promise<T> {
  return apiRequest<T>(endpoint, { method: 'DELETE' });
}
