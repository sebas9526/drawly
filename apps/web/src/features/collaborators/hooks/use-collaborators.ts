import type {
  CreateCollaboratorRequest,
  ListCollaboratorsQuery,
  UpdateCollaboratorRequest,
} from '@drawly/api-client';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { QUERY_KEYS } from '@drawly/constants';

import { api } from '@/lib/api';

export function useCollaborators(
  filters: { raffleId?: string | undefined; search?: string | undefined } = {},
) {
  const query: ListCollaboratorsQuery = { page_size: 100 };
  if (filters.raffleId) query.raffle_id = filters.raffleId;
  if (filters.search) query.search = filters.search;
  return useQuery({
    queryKey: QUERY_KEYS.collaborators(filters.raffleId, filters.search),
    queryFn: () => api.collaborators.getAll(query),
  });
}

export function useRaffleCollaborators(raffleId: string) {
  return useQuery({
    queryKey: QUERY_KEYS.raffleCollaborators(raffleId),
    queryFn: () => api.collaborators.getByRaffle(raffleId),
    enabled: raffleId.length > 0,
  });
}

export function useCollaboratorStats(raffleId: string) {
  return useQuery({
    queryKey: QUERY_KEYS.collaboratorStats(raffleId),
    queryFn: () => api.collaborators.statsByRaffle(raffleId),
    enabled: raffleId.length > 0,
  });
}

function useCollaboratorsInvalidator() {
  const queryClient = useQueryClient();
  return (): Promise<void> => queryClient.invalidateQueries({ queryKey: ['collaborators'] });
}

export function useCreateCollaborator() {
  const invalidate = useCollaboratorsInvalidator();
  return useMutation({
    mutationFn: (payload: CreateCollaboratorRequest) => api.collaborators.create(payload),
    onSuccess: invalidate,
  });
}

export function useUpdateCollaborator() {
  const invalidate = useCollaboratorsInvalidator();
  return useMutation({
    mutationFn: (input: { id: string; payload: UpdateCollaboratorRequest }) =>
      api.collaborators.update(input.id, input.payload),
    onSuccess: invalidate,
  });
}

export function useSetCollaboratorActive() {
  const invalidate = useCollaboratorsInvalidator();
  return useMutation({
    mutationFn: (input: { id: string; isActive: boolean }) =>
      input.isActive
        ? api.collaborators.activate(input.id)
        : api.collaborators.deactivate(input.id),
    onSuccess: invalidate,
  });
}

export function useDeleteCollaborator() {
  const invalidate = useCollaboratorsInvalidator();
  return useMutation({
    mutationFn: (id: string) => api.collaborators.delete(id),
    onSuccess: invalidate,
  });
}
