import {
  costTrends,
  recommendations,
  totalMonthlyCost,
  totalResources,
  totalSavingsPotential,
} from '../data/mockData';
import type { CostTrend } from '../types/cost';
import type { Recommendation } from '../types/recommendation';

export interface CloudData {
  costTrends: CostTrend[];
  recommendations: Recommendation[];
  totalMonthlyCost: number;
  totalResources: number;
  totalSavingsPotential: number;
  isDemo: boolean;
  isLoading: boolean;
}

/**
 * Returns cloud cost data.
 * Currently always returns mock data (isDemo: true).
 * Once authentication is added, this hook will switch to the real API
 * when a provider is connected — swap the return value with an API call via
 * src/services/api.ts and a TanStack Query useQuery().
 */
export function useCloudData(): CloudData {
  return {
    costTrends,
    recommendations,
    totalMonthlyCost,
    totalResources,
    totalSavingsPotential,
    isDemo: true,
    isLoading: false,
  };
}
