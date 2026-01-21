import { QueryClient } from '@tanstack/react-query';

/**
 * Default query client configuration for the application.
 * Configured for optimal caching and error handling.
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 30, // 30 minutes (was cacheTime)
      retry: 3,
      refetchOnWindowFocus: false,
    },
  },
});
