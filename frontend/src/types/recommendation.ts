export type Priority = 'high' | 'medium' | 'low';

export type RecommendationCategory =
  | 'rightsizing'
  | 'unused'
  | 'reserved-instances'
  | 'storage'
  | 'network';

export type RecommendationStatus = 'open' | 'implemented' | 'dismissed';

// Frontend/UI type — used in mock data and component props
export interface Recommendation {
  id: string;
  title: string;
  description: string;
  provider: 'AWS';
  resourceName: string;
  currentCost: number;
  estimatedSavings: number;
  savingsPercent: number;
  priority: Priority;
  category: RecommendationCategory;
  aiConfidence: number;
}

// Backend API format — matches the Pydantic schema
export interface ApiRecommendation {
  id: string;
  resource_id: string;
  resource_type: string;
  issue: string;
  recommendation: string;
  priority: Priority;
  estimated_saving: number;
  effort: Priority;
  action_steps: string[];
  status: RecommendationStatus;
}

export interface WasteReport {
  resource_id: string;
  resource_type: string;
  rule: string;
  severity: Priority;
  detail: string;
  estimated_saving_usd: number;
}
