/**
 * Subscriptions API client functions.
 */

import { get, post } from '@/lib/api';
import type { CreateTrialRequest, Subscription } from '../types';

/**
 * Fetches the current user's subscription.
 *
 * @returns Promise resolving to subscription details
 */
export async function getMySubscription(): Promise<Subscription> {
  return get<Subscription>('/subscriptions/me');
}

/**
 * Creates a trial subscription for the current user.
 *
 * @param data - Plan ID for the trial
 * @returns Promise resolving to created subscription
 */
export async function createTrialSubscription(
  data: CreateTrialRequest
): Promise<Subscription> {
  return post<Subscription>('/subscriptions/trial', data);
}
