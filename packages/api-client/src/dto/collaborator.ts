/**
 * Wire-format DTOs for the Collaborators domain (sales collaborators per raffle).
 * Field names are snake_case to mirror the API JSON (apps/api collaborators
 * module). See docs/04-api/API_SPECIFICATION.md ("Collaborators").
 */
export interface CollaboratorDto {
  id: string;
  raffle_id: string;
  name: string;
  phone: string | null;
  email: string | null;
  color: string;
  notes: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateCollaboratorRequest {
  raffle_id: string;
  name: string;
  phone?: string | undefined;
  email?: string | undefined;
  color?: string | undefined;
  notes?: string | undefined;
  is_active?: boolean | undefined;
}

export type UpdateCollaboratorRequest = Partial<Omit<CreateCollaboratorRequest, 'raffle_id'>>;

export type CollaboratorSort = 'created_at' | 'name' | 'is_active';
export type SortOrder = 'asc' | 'desc';

export interface ListCollaboratorsQuery {
  [key: string]: string | number | boolean | undefined | null;
  page?: number;
  page_size?: number;
  /** Matches name, phone, or email. */
  search?: string | undefined;
  raffle_id?: string | undefined;
  is_active?: boolean | undefined;
  sort?: CollaboratorSort | undefined;
  order?: SortOrder | undefined;
}

/** Per-collaborator sales figures within a raffle (derived from ticket status). */
export interface CollaboratorStatsDto {
  collaborator_id: string;
  name: string;
  color: string;
  reserved: number;
  paid: number;
  total: number;
  total_value: number;
}
