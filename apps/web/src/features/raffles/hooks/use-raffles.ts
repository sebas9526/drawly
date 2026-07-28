import type {
  CreateRaffleRequest,
  ListRafflesQuery,
  RegisterWinnerRequest,
  UpdateRaffleRequest,
} from '@drawly/api-client';
import { fetchAllPages } from '@drawly/api-client';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { QUERY_KEYS } from '@drawly/constants';

import { api } from '@/lib/api';

export function useRaffles(query?: Pick<ListRafflesQuery, 'search'>) {
  return useQuery({
    queryKey: [...QUERY_KEYS.raffles, { search: query?.search ?? null }] as const,
    queryFn: () =>
      fetchAllPages((page, pageSize) =>
        api.raffles.list({ page, page_size: pageSize, search: query?.search }),
      ),
  });
}

export function useRaffle(raffleId: string) {
  return useQuery({
    queryKey: QUERY_KEYS.raffle(raffleId),
    queryFn: () => api.raffles.get(raffleId),
    enabled: raffleId.length > 0,
  });
}

export function useCreateRaffle() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateRaffleRequest) => api.raffles.create(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: QUERY_KEYS.raffles }),
  });
}

export function useGenerateTickets() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (raffleId: string) => api.raffles.generateTickets(raffleId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: QUERY_KEYS.ticketsAll });
      void queryClient.invalidateQueries({ queryKey: QUERY_KEYS.raffles });
    },
  });
}

export function usePublishRaffle() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (raffleId: string) => api.raffles.publish(raffleId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: QUERY_KEYS.raffles }),
  });
}

export function useRegisterWinner() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: { id: string; payload: RegisterWinnerRequest }) =>
      api.raffles.registerWinner(input.id, input.payload),
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({ queryKey: QUERY_KEYS.raffles });
      void queryClient.invalidateQueries({ queryKey: QUERY_KEYS.raffle(variables.id) });
      void queryClient.invalidateQueries({ queryKey: QUERY_KEYS.tickets(variables.id) });
      void queryClient.invalidateQueries({ queryKey: QUERY_KEYS.raffleTicketCounts(variables.id) });
    },
  });
}

export function useUpdateRaffle() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: { id: string; payload: UpdateRaffleRequest }) =>
      api.raffles.update(input.id, input.payload),
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({ queryKey: QUERY_KEYS.raffles });
      void queryClient.invalidateQueries({ queryKey: QUERY_KEYS.raffle(variables.id) });
    },
  });
}

export function useDeleteRaffle() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (raffleId: string) => api.raffles.remove(raffleId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: QUERY_KEYS.raffles }),
  });
}
