import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import { getMe, logout as logoutApi, type User } from '../api/auth';
import { useAuthStore } from '../store/authStore';

/**
 * Auth query key for TanStack Query.
 */
export const authQueryKey = ['auth', 'me'] as const;

/**
 * Hook for managing authentication state.
 *
 * Combines Zustand store for local state with TanStack Query
 * for server state management.
 *
 * @returns Auth state and methods
 */
export function useAuth() {
  const queryClient = useQueryClient();
  const { user, isLoading, isAuthenticated, setUser, setLoading, clearAuth } =
    useAuthStore();

  // Query current user on mount
  const {
    data: userData,
    isLoading: isQueryLoading,
    error,
    refetch,
  } = useQuery<User, Error>({
    queryKey: authQueryKey,
    queryFn: getMe,
    retry: false, // Don't retry on 401
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Sync query result with store
  useEffect(() => {
    if (userData) {
      setUser(userData);
    } else if (error) {
      // Clear auth on error (401, etc.)
      clearAuth();
    }
  }, [userData, error, setUser, clearAuth]);

  // Sync loading state
  useEffect(() => {
    setLoading(isQueryLoading);
  }, [isQueryLoading, setLoading]);

  // Logout mutation
  const logoutMutation = useMutation({
    mutationFn: logoutApi,
    onSuccess: () => {
      // Clear local state
      clearAuth();
      // Invalidate queries
      queryClient.removeQueries({ queryKey: authQueryKey });
    },
  });

  /**
   * Log out the current user.
   */
  const logout = async () => {
    await logoutMutation.mutateAsync();
  };

  /**
   * Refresh auth state from server.
   */
  const refresh = async () => {
    await refetch();
  };

  return {
    user,
    isLoading: isLoading || isQueryLoading,
    isAuthenticated,
    error,
    logout,
    refresh,
    isLoggingOut: logoutMutation.isPending,
  };
}
