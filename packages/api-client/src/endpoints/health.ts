import type { ApiClient } from '../client/fetcher';

export interface HealthStatus {
  status: string;
}

export function createHealthEndpoints(client: ApiClient) {
  return {
    /** Unversioned infra probe — matches the actual FastAPI route (apps/api/app/api/health.py). */
    check: (): Promise<HealthStatus> => client.get<HealthStatus>('/health'),
  };
}
