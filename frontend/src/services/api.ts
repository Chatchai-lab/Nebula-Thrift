import axios from 'axios';
import type {
  HealthResponse,
  CostResponse,
  CostBreakdownResponse,
  RecommendationsResponse,
  ConnectionStatusResponse,
} from '../types/api';

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  timeout: 10_000,
  headers: { 'Content-Type': 'application/json' },
});

export const api = {
  health: () =>
    client.get<HealthResponse>('/api/health').then((r) => r.data),

  getCosts: (days = 30) =>
    client.get<CostResponse>('/api/costs', { params: { days } }).then((r) => r.data),

  getCostBreakdown: () =>
    client.get<CostBreakdownResponse>('/api/costs/breakdown').then((r) => r.data),

  getRecommendations: () =>
    client.get<RecommendationsResponse>('/api/recommendations').then((r) => r.data),

  markImplemented: (id: string) =>
    client.patch(`/api/recommendations/${id}`, { status: 'implemented' }).then((r) => r.data),

  getConnectionStatus: () =>
    client.get<ConnectionStatusResponse>('/api/connection').then((r) => r.data),
};
