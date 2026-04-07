export interface CostTrend {
  month: string;
  compute: number;
  storage: number;
  database: number;
  network: number;
  total: number;
}

export interface ServiceBreakdown {
  name: string;
  value: number;
  color: string;
}

export interface CostData {
  trends: CostTrend[];
  totalMonthlyCost: number;
  breakdown: ServiceBreakdown[];
}
