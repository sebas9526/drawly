/**
 * Future roles/permissions, as documented in docs/04-api/AUTHENTICATION.md.
 * Not enforced yet (auth is not part of the MVP) — defined now so the shape
 * is shared and stable once the auth module lands.
 */

export const ROLES = {
  OWNER: 'owner',
  ADMINISTRATOR: 'administrator',
  SELLER: 'seller',
  VIEWER: 'viewer',
} as const;

export type Role = (typeof ROLES)[keyof typeof ROLES];

export const PERMISSIONS = {
  CREATE_RAFFLES: 'create_raffles',
  DELETE_RAFFLES: 'delete_raffles',
  MANAGE_PARTICIPANTS: 'manage_participants',
  MANAGE_PAYMENTS: 'manage_payments',
  VIEW_REPORTS: 'view_reports',
  MANAGE_ORGANIZATION: 'manage_organization',
} as const;

export type Permission = (typeof PERMISSIONS)[keyof typeof PERMISSIONS];
