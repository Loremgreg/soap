import { useNavigate } from '@tanstack/react-router';
import { useEffect, type ReactNode } from 'react';
import { useAuth } from '../hooks/useAuth';
import { Skeleton } from '@/components/ui/skeleton';

/**
 * Props for ProtectedRoute component.
 */
interface ProtectedRouteProps {
  /** Child components to render when authenticated */
  children: ReactNode;
  /** Redirect path for unauthenticated users (default: /login) */
  redirectTo?: string;
}

/**
 * Wrapper component that protects routes requiring authentication.
 *
 * Redirects to login page if user is not authenticated.
 * Shows loading skeleton while checking auth status.
 *
 * @param children - Components to render when authenticated
 * @param redirectTo - Where to redirect unauthenticated users
 */
export function ProtectedRoute({
  children,
  redirectTo = '/login',
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate({ to: redirectTo });
    }
  }, [isLoading, isAuthenticated, navigate, redirectTo]);

  // Show loading skeleton while checking auth
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="w-full max-w-md space-y-4">
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-8 w-3/4" />
          <Skeleton className="h-32 w-full" />
        </div>
      </div>
    );
  }

  // Don't render children if not authenticated (will redirect)
  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
