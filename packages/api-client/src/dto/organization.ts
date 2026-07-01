/**
 * PROVISIONAL — /organizations is listed under "Future Endpoints" in
 * docs/04-api/API_SPECIFICATION.md (MVP is single-organization). Fields
 * mirror docs/02-architecture/DOMAIN_MODEL.md's Organization entity.
 */

export interface OrganizationDto {
  id: string;
  name: string;
  email: string;
  phone: string | null;
  logo: string | null;
  created_at: string;
  updated_at: string;
}

export type UpdateOrganizationRequest = Partial<
  Pick<OrganizationDto, 'name' | 'email' | 'phone' | 'logo'>
>;
