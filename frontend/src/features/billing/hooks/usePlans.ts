/**
 * TanStack Query hook for fetching subscription plans.
 */

import { useQuery } from '@tanstack/react-query';
import { getPlans } from '../api/plans';
import type { Plan } from '../types';

/**
 * Query key for plans cache.
 */
export const plansQueryKey = ['plans'] as const;

/**
 * Fetches all active subscription plans.
 *
 * Uses TanStack Query for caching and automatic refetching.
 * Plans are cached for 5 minutes as they rarely change.
 *
 * @returns Query result with plans data, loading state, and error
 */
export function usePlans() {
  return useQuery<Plan[], Error>({
    queryKey: plansQueryKey,
    queryFn: getPlans,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
}
