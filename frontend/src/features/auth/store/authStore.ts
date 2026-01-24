import { create } from 'zustand';
import type { User } from '../api/auth';

/**
 * Auth state interface.
 */
interface AuthState {
  /** Current authenticated user */
  user: User | null;
  /** Whether auth check is in progress */
  isLoading: boolean;
  /** Whether user is authenticated */
  isAuthenticated: boolean;
  /** Set the current user */
  setUser: (user: User | null) => void;
  /** Set loading state */
  setLoading: (loading: boolean) => void;
  /** Clear auth state (logout) */
  clearAuth: () => void;
}

/**
 * Zustand store for authentication state.
 *
 * Manages user session state across the application.
 * Use with TanStack Query for data fetching.
 */
export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true, // Start as loading to check auth on mount
  isAuthenticated: false,

  setUser: (user) =>
    set({
      user,
      isAuthenticated: user !== null,
      isLoading: false,
    }),

  setLoading: (loading) =>
    set({
      isLoading: loading,
    }),

  clearAuth: () =>
    set({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    }),
}));
