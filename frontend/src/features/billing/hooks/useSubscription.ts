/**
 * TanStack Query hooks for subscription management.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import { useTranslation } from 'react-i18next';
import { createTrialSubscription, getMySubscription } from '../api/subscriptions';
import type { CreateTrialRequest, Subscription } from '../types';
import { useToast } from '@/hooks/use-toast';
import { ApiRequestError } from '@/lib/api';

/**
 * Query key for subscription cache.
 */
export const subscriptionQueryKey = ['subscription', 'me'] as const;

/**
 * Fetches the current user's subscription.
 *
 * Uses TanStack Query for caching.
 * Refetches on window focus to keep status up-to-date.
 *
 * @returns Query result with subscription data, loading state, and error
 */
export function useSubscription() {
  return useQuery<Subscription, Error>({
    queryKey: subscriptionQueryKey,
    queryFn: getMySubscription,
    retry: (failureCount, error) => {
      // Don't retry on 404 (no subscription exists - expected for new users)
      if (error instanceof ApiRequestError && error.status === 404) {
        return false;
      }
      // Retry up to 3 times for other errors (500, network, etc.)
      return failureCount < 3;
    },
    staleTime: 60 * 1000, // 1 minute
  });
}

/**
 * Mutation hook for creating a trial subscription.
 *
 * On success:
 * - Invalidates subscription query cache
 * - Shows success toast
 * - Redirects to home page
 *
 * On error:
 * - Shows error toast with message
 *
 * @returns Mutation function and state
 */
export function useCreateTrialSubscription() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { t } = useTranslation('billing');
  const { t: tCommon } = useTranslation('common');

  return useMutation<Subscription, Error, CreateTrialRequest>({
    mutationFn: createTrialSubscription,
    onSuccess: () => {
      // Invalidate subscription cache
      queryClient.invalidateQueries({ queryKey: subscriptionQueryKey });

      // Show success toast
      toast({
        title: t('trial.activated'),
        description: t('trial.activatedDescription'),
      });

      // Redirect to home
      navigate({ to: '/' });
    },
    onError: (error) => {
      toast({
        variant: 'destructive',
        title: tCommon('error'),
        description: error.message || t('trial.activationError'),
      });
    },
  });
}
