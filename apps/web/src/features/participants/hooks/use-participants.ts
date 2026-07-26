import type { CreateParticipantRequest, UpdateParticipantRequest } from '@drawly/api-client';
import { fetchAllPages } from '@drawly/api-client';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { QUERY_KEYS } from '@drawly/constants';

import { api } from '@/lib/api';

export function useParticipants(search?: string) {
  return useQuery({
    queryKey: QUERY_KEYS.participants(search),
    queryFn: () =>
      fetchAllPages((page, pageSize) =>
        api.participants.list({ search, page, page_size: pageSize }),
      ),
  });
}

export function useParticipant(id: string) {
  return useQuery({
    queryKey: QUERY_KEYS.participant(id),
    queryFn: () => api.participants.getById(id),
    enabled: id.length > 0,
  });
}

export function useParticipantTickets(id: string) {
  return useQuery({
    queryKey: QUERY_KEYS.participantTickets(id),
    queryFn: () => api.participants.getTickets(id),
    enabled: id.length > 0,
  });
}

function useParticipantsInvalidator() {
  const queryClient = useQueryClient();
  return (): Promise<void> =>
    queryClient.invalidateQueries({ queryKey: QUERY_KEYS.participantsAll });
}

export function useCreateParticipant() {
  const invalidate = useParticipantsInvalidator();
  return useMutation({
    mutationFn: (payload: CreateParticipantRequest) => api.participants.create(payload),
    onSuccess: invalidate,
  });
}

export function useUpdateParticipant() {
  const invalidate = useParticipantsInvalidator();
  return useMutation({
    mutationFn: (input: { id: string; payload: UpdateParticipantRequest }) =>
      api.participants.update(input.id, input.payload),
    onSuccess: invalidate,
  });
}

export function useDeleteParticipant() {
  const invalidate = useParticipantsInvalidator();
  return useMutation({
    mutationFn: (id: string) => api.participants.remove(id),
    onSuccess: invalidate,
  });
}
