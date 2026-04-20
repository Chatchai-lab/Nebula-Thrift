import type { CostTrend, ServiceBreakdown } from './cost';
import type { ApiRecommendation, WasteReport } from './recommendation';
import type { ConnectionInfo } from './provider';

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface HealthResponse {
  status: 'ok' | 'degraded';
  timestamp: string;
  version: string;
}

export interface CostResponse {
  trends: CostTrend[];
  totalSpend: number;
  currency: string;
  periodStart: string;
  periodEnd: string;
}

export interface CostBreakdownResponse {
  breakdown: ServiceBreakdown[];
  totalSpend: number;
  currency: string;
}

export interface RecommendationsResponse {
  recommendations: ApiRecommendation[];
  totalSavingsPotential: number;
  currency: string;
}

export interface WasteReportsResponse {
  reports: WasteReport[];
}

export interface ConnectionStatusResponse extends ConnectionInfo {
  resourceCount: number;
}

// AWS Account Registration & Management
export interface AWSAccountCreate {
  name: string;
  region: string;
  access_key_id?: string;
  secret_access_key?: string;
  role_arn?: string;
}

export interface AWSAccount {
  account_id: string;
  name: string;
  region: string;
  created_at: string;
}

// Snapshot Cost Data Structure
export interface SnapshotCostData {
  period: { start: string; end: string };
  currency: string;
  total: number;
  by_service: { service: string; amount: number }[];
  daily: { date: string; total: number; by_service: Record<string, number> }[];
}

export interface SnapshotResponse {
  status: string;
  date: string;
  data: {
    date: string;
    fetched_at: string;
    days: number;
    cost_data: SnapshotCostData;
  };
}
