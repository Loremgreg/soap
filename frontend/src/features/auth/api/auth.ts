import { get, post } from '@/lib/api';

/**
 * User response from the API.
 */
export interface User {
  id: string;
  email: string;
  name: string | null;
  avatarUrl: string | null;
  isAdmin: boolean;
  createdAt: string;
  updatedAt: string;
}

/**
 * Get the current authenticated user.
 *
 * @returns The current user or throws if not authenticated
 */
export async function getMe(): Promise<User> {
  return get<User>('/auth/me');
}

/**
 * Log out the current user.
 *
 * Clears the httpOnly cookie on the server.
 *
 * @returns Success message
 */
export async function logout(): Promise<{ message: string }> {
  return post<{ message: string }>('/auth/logout');
}
