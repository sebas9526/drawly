import { API_V1_PREFIX } from '@drawly/constants';

import type { ApiClient } from '../client/fetcher';
import type { OrganizationDto, UpdateOrganizationRequest } from '../dto/organization';

const BASE_PATH = `${API_V1_PREFIX}/organizations`;

/** PROVISIONAL — see the note in ../dto/organization.ts. */
export function createOrganizationsEndpoints(client: ApiClient) {
  return {
    get: (id: string): Promise<OrganizationDto> =>
      client.get<OrganizationDto>(`${BASE_PATH}/${id}`),

    update: (id: string, payload: UpdateOrganizationRequest): Promise<OrganizationDto> =>
      client.put<OrganizationDto>(`${BASE_PATH}/${id}`, payload),
  };
}
