import axios from 'axios';
import type {
  HealthResponse,
  CostResponse,
  CostBreakdownResponse,
  RecommendationsResponse,
  ConnectionStatusResponse,
  AWSAccountCreate,
  AWSAccount,
  SnapshotResponse,
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

  // AWS Account Management
  registerAccount: (data: AWSAccountCreate) =>
    client.post<AWSAccount>('/api/accounts', data).then((r) => r.data),

  getAccount: (accountId: string) =>
    client.get<AWSAccount>(`/api/accounts/${accountId}`).then((r) => r.data),

  updateAccountCredentials: (accountId: string, accessKeyId: string, secretAccessKey: string) =>
    client
      .patch<{ status: string; message: string }>(`/api/accounts/${accountId}/credentials`, {
        access_key_id: accessKeyId,
        secret_access_key: secretAccessKey,
        name: '', // Backend only needs the credentials, name is not used
        region: '', // Same here
      })
      .then((r) => r.data),

  deleteAccount: (accountId: string) =>
    client.delete<{ status: string; message: string }>(`/api/accounts/${accountId}`).then((r) => r.data),

  // Snapshots
  getSnapshot: (accountId: string, days = 30) =>
    client
      .get<SnapshotResponse>('/api/snapshots/latest', { params: { account_id: accountId, days } })
      .then((r) => r.data),

  saveSnapshot: (accountId: string, days = 30) =>
    client
      .post<SnapshotResponse>('/api/snapshots/save', null, { params: { account_id: accountId, days } })
      .then((r) => r.data),
};
