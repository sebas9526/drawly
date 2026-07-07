import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';

import { api } from '@/lib/api';

export interface AssignParticipantInput {
  ticketId: string;
  participantId: string;
}

/**
 * Ticket mutations (reserve / cancel / pay / assign / unassign participant).
 * Each invalidates every ticket query so the list reflects the new state. No
 * business rules here — the API enforces every transition; the UI only fires the
 * action and surfaces errors. Participant counts also change, so those queries
 * are invalidated too.
 */
export function useTicketActions() {
  const queryClient = useQueryClient();
  const invalidate = (): void => {
    void queryClient.invalidateQueries({ queryKey: ['tickets'] });
    void queryClient.invalidateQueries({ queryKey: ['participants'] });
  };

  const reserve = useMutation({
    mutationFn: (ticketId: string) => api.tickets.reserve(ticketId),
    onSuccess: invalidate,
  });

  const cancel = useMutation({
    mutationFn: (ticketId: string) => api.tickets.cancelReservation(ticketId),
    onSuccess: invalidate,
  });

  const pay = useMutation({
    mutationFn: (ticketId: string) => api.tickets.markAsPaid(ticketId),
    onSuccess: invalidate,
  });

  const assignParticipant = useMutation({
    mutationFn: (input: AssignParticipantInput) =>
      api.tickets.assignParticipant(input.ticketId, input.participantId),
    onSuccess: invalidate,
  });

  const unassignParticipant = useMutation({
    mutationFn: (ticketId: string) => api.tickets.unassignParticipant(ticketId),
    onSuccess: invalidate,
  });

  return { reserve, cancel, pay, assignParticipant, unassignParticipant };
}

export interface BulkActionResult {
  succeeded: number;
  failed: number;
}

/**
 * Sequential bulk variants of the same single-ticket endpoints (no bulk
 * endpoint exists server-side). Each item is applied independently so one
 * invalid transition (e.g. a paid ticket that can't be cancelled) doesn't
 * block the rest — the caller gets a succeeded/failed tally to display.
 */
export function useBulkTicketActions() {
  const queryClient = useQueryClient();
  const [isPending, setIsPending] = useState(false);

  const invalidate = (): void => {
    void queryClient.invalidateQueries({ queryKey: ['tickets'] });
    void queryClient.invalidateQueries({ queryKey: ['participants'] });
    void queryClient.invalidateQueries({ queryKey: ['collaborators'] });
  };

  const runBulk = async (
    ticketIds: string[],
    action: (ticketId: string) => Promise<unknown>,
  ): Promise<BulkActionResult> => {
    setIsPending(true);
    let succeeded = 0;
    let failed = 0;
    for (const ticketId of ticketIds) {
      try {
        await action(ticketId);
        succeeded += 1;
      } catch {
        failed += 1;
      }
    }
    invalidate();
    setIsPending(false);
    return { succeeded, failed };
  };

  return {
    isPending,
    bulkReserve: (ticketIds: string[]) => runBulk(ticketIds, (id) => api.tickets.reserve(id)),
    bulkCancel: (ticketIds: string[]) =>
      runBulk(ticketIds, (id) => api.tickets.cancelReservation(id)),
    bulkMarkPaid: (ticketIds: string[]) => runBulk(ticketIds, (id) => api.tickets.markAsPaid(id)),
    bulkSetCollaborator: (ticketIds: string[], collaboratorId: string | null) =>
      runBulk(ticketIds, (id) => api.tickets.setCollaborator(id, collaboratorId)),
  };
}
