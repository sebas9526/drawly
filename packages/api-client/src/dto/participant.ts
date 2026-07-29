/**
 * Wire-format DTOs for the Participants domain. Field names are snake_case to
 * mirror the API JSON (apps/api participants module). `ticket_count` is a
 * server-computed convenience field for list/detail views.
 */
export interface ParticipantDto {
  id: string;
  full_name: string;
  phone: string;
  email: string | null;
  document: string | null;
  address: string | null;
  city: string | null;
  notes: string | null;
  ticket_count: number;
  /** Ascending; empty when the participant holds no tickets. */
  ticket_numbers: number[];
  /** Sellers credited on this participant's tickets, alphabetical, deduped. */
  collaborator_names: string[];
  created_at: string;
  updated_at: string;
}

export interface CreateParticipantRequest {
  full_name: string;
  phone: string;
  email?: string | undefined;
  document?: string | undefined;
  address?: string | undefined;
  city?: string | undefined;
  notes?: string | undefined;
}

export type UpdateParticipantRequest = Partial<CreateParticipantRequest>;

export interface ListParticipantsQuery {
  [key: string]: string | number | boolean | undefined | null;
  page?: number;
  page_size?: number;
  /** Matches name, phone, document, or email. */
  search?: string | undefined;
}
