import { useState, useEffect } from 'react';
import { useAccount } from './useAccount';
import { api } from '../services/api';
import {
  costTrends,
  recommendations,
  totalMonthlyCost,
  totalResources,
  totalSavingsPotential,
} from '../data/mockData';
import type { CostTrend } from '../types/cost';
import type { Recommendation } from '../types/recommendation';
import type { SnapshotCostData } from '../types/api';

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
 * Maps backend snapshot cost data to frontend CostTrend format.
 * The snapshot contains by_service and daily breakdown; we create a single
 * trend entry representing the snapshot period.
 */
function mapSnapshotToCloudData(data: SnapshotCostData): Omit<CloudData, 'isDemo' | 'isLoading'> {
  // Extract top 4 services by name matching
  const services = data.by_service.slice(0, 4);
  const [compute, storage, database, network] = [
    services.find(s => /EC2|Compute/i.test(s.service))?.amount ?? 0,
    services.find(s => /S3|Storage/i.test(s.service))?.amount ?? 0,
    services.find(s => /RDS|Database/i.test(s.service))?.amount ?? 0,
    services.find(s => /Transfer|Network|CloudFront/i.test(s.service))?.amount ?? 0,
  ];

  // Create a single month entry from the snapshot
  const monthLabel = new Date(data.period.end).toLocaleDateString('en', { month: 'short' });

  const syntheticTrend: CostTrend = {
    month: monthLabel,
    compute,
    storage,
    database,
    network,
    total: data.total,
  };

  // Note: recommendations are not included in the snapshot endpoint
  // They would come from a separate backend endpoint in the future
  return {
    costTrends: [syntheticTrend],
    recommendations: [],
    totalMonthlyCost: data.total,
    totalResources: data.by_service.length,
    totalSavingsPotential: 0,
  };
}

/**
 * Returns cloud cost data.
 * - If not connected: returns mock data (isDemo: true)
 * - If connected: fetches real data from backend (isDemo: false)
 */
export function useCloudData(): CloudData {
  const { isConnected, accountId } = useAccount();
  const [realData, setRealData] = useState<Omit<CloudData, 'isDemo' | 'isLoading'> | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!isConnected || !accountId) {
      setRealData(null);
      return;
    }

    const fetchSnapshot = async () => {
      setIsLoading(true);
      try {
        const snapshot = await api.getSnapshot(accountId);
        setRealData(mapSnapshotToCloudData(snapshot.data.cost_data));
      } catch (err) {
        // On error (e.g., no snapshot saved yet), log and fall back gracefully
        console.warn('Failed to fetch snapshot:', err);
        setRealData(null);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSnapshot();
  }, [isConnected, accountId]);

  // If not connected or data fetch failed, return mock data
  if (!isConnected || realData === null) {
    return {
      costTrends,
      recommendations,
      totalMonthlyCost,
      totalResources,
      totalSavingsPotential,
      isDemo: true,
      isLoading,
    };
  }

  // Return real data
  return {
    ...realData,
    isDemo: false,
    isLoading,
  };
}
