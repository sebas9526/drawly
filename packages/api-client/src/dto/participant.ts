export interface ParticipantDto {
  id: string;
  full_name: string;
  phone: string;
  email: string | null;
  address: string | null;
  city: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export type UpdateParticipantRequest = Partial<
  Pick<ParticipantDto, 'full_name' | 'phone' | 'email' | 'address' | 'city' | 'notes'>
>;

export interface ListParticipantsQuery {
  [key: string]: string | number | boolean | undefined | null;
  page?: number;
  page_size?: number;
  search?: string;
}
