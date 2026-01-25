/**
 * Plans API client functions.
 */

import { get } from '@/lib/api';
import type { Plan } from '../types';

/**
 * Fetches all active subscription plans.
 *
 * @returns Promise resolving to list of plans ordered by price ascending
 */
export async function getPlans(): Promise<Plan[]> {
  return get<Plan[]>('/plans');
}

/**
 * Fetches a specific plan by ID.
 *
 * @param planId - UUID of the plan to fetch
 * @returns Promise resolving to plan details
 */
export async function getPlanById(planId: string): Promise<Plan> {
  return get<Plan>(`/plans/${planId}`);
}
