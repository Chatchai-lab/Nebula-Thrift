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
