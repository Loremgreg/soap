/**
 * Types for billing and subscription features.
 */

/**
 * Subscription status values.
 */
export type SubscriptionStatus = 'trial' | 'active' | 'cancelled' | 'expired';

/**
 * Plan data from API.
 */
export interface Plan {
  id: string;
  name: string;
  displayName: string;
  priceMonthly: number;
  quotaMonthly: number;
  maxRecordingMinutes: number;
  maxNotesRetention: number;
  isActive: boolean;
}

/**
 * Minimal plan summary for subscription responses.
 */
export interface PlanSummary {
  name: string;
  displayName: string;
  quotaMonthly: number;
}

/**
 * Subscription data from API.
 */
export interface Subscription {
  id: string;
  userId: string;
  planId: string;
  plan: PlanSummary | null;
  status: SubscriptionStatus;
  quotaRemaining: number;
  quotaTotal: number;
  trialEndsAt: string | null;
  currentPeriodStart: string | null;
  currentPeriodEnd: string | null;
  stripeCustomerId: string | null;
  stripeSubscriptionId: string | null;
  createdAt: string;
  updatedAt: string;
  isTrialExpired: boolean;
  canRecord: boolean;
}

/**
 * Request body for creating a trial subscription.
 */
export interface CreateTrialRequest {
  planId: string;
}
