export type CloudProviderName = 'AWS' | 'Azure' | 'GCP';

export type ConnectionStatus = 'connected' | 'disconnected' | 'validating' | 'error';

export interface ProviderConfig {
  provider: CloudProviderName;
  region: string;
  accountId?: string;
}

export interface AWSProviderConfig extends ProviderConfig {
  provider: 'AWS';
  roleArn?: string;
  accessKeyId?: string;
}

export interface ConnectionInfo {
  status: ConnectionStatus;
  provider: CloudProviderName;
  accountId: string;
  lastSync: string | null;
  errorMessage?: string;
}
