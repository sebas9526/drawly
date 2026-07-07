import { ApiClient } from './client/fetcher';
import { createAnalyticsEndpoints } from './endpoints/analytics';
import { createAuthEndpoints } from './endpoints/auth';
import { createCollaboratorsEndpoints } from './endpoints/collaborators';
import { createDashboardEndpoints } from './endpoints/dashboard';
import { createHealthEndpoints } from './endpoints/health';
import { createOrganizationsEndpoints } from './endpoints/organizations';
import { createParticipantsEndpoints } from './endpoints/participants';
import { createPublicEndpoints } from './endpoints/public';
import { createRafflesEndpoints } from './endpoints/raffles';
import { createTicketsEndpoints } from './endpoints/tickets';
import type { ApiClientConfig } from './types/config';

/**
 * Single entry point apps use to talk to the Drawly API.
 * Framework-agnostic: works the same from Next.js, a script, or (eventually)
 * a React Native app — only `fetch` and `config` differ per environment.
 */
export function createDrawlyApiClient(config: ApiClientConfig) {
  const client = new ApiClient(config);

  return {
    analytics: createAnalyticsEndpoints(client),
    auth: createAuthEndpoints(client),
    collaborators: createCollaboratorsEndpoints(client),
    dashboard: createDashboardEndpoints(client),
    health: createHealthEndpoints(client),
    organizations: createOrganizationsEndpoints(client),
    participants: createParticipantsEndpoints(client),
    public: createPublicEndpoints(client),
    raffles: createRafflesEndpoints(client),
    tickets: createTicketsEndpoints(client),
  };
}

export type DrawlyApiClient = ReturnType<typeof createDrawlyApiClient>;
