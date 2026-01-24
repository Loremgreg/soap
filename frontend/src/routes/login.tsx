import { createFileRoute } from '@tanstack/react-router';
import { z } from 'zod';
import { LoginPage } from '@/features/auth/pages/LoginPage';

/**
 * Search params schema for login page.
 * Validates OAuth error query parameters.
 */
const loginSearchSchema = z.object({
  error: z.string().optional(),
  error_description: z.string().optional(),
});

export type LoginSearchParams = z.infer<typeof loginSearchSchema>;

/**
 * Login page route.
 *
 * Displays the login page with Google OAuth button.
 * Handles OAuth error query params (error, error_description).
 */
export const Route = createFileRoute('/login')({
  component: LoginPage,
  validateSearch: loginSearchSchema,
});
