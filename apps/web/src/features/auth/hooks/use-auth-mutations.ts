'use client';

import type { LoginRequest, RegisterRequest } from '@drawly/api-client';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';

import { QUERY_KEYS, ROUTES } from '@drawly/constants';

import { api } from '@/lib/api';

export function useLogin() {
  const queryClient = useQueryClient();
  const router = useRouter();
  return useMutation({
    mutationFn: (payload: LoginRequest) => api.auth.login(payload),
    onSuccess: (user) => {
      queryClient.setQueryData(QUERY_KEYS.authMe, user);
      router.replace(ROUTES.DASHBOARD);
    },
  });
}

export function useRegister() {
  const queryClient = useQueryClient();
  const router = useRouter();
  return useMutation({
    mutationFn: (payload: RegisterRequest) => api.auth.register(payload),
    onSuccess: (user) => {
      queryClient.setQueryData(QUERY_KEYS.authMe, user);
      router.replace(ROUTES.DASHBOARD);
    },
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  const router = useRouter();
  return useMutation({
    mutationFn: () => api.auth.logout(),
    onSuccess: () => {
      // Drop every cached query so no owner-scoped data survives the session.
      queryClient.setQueryData(QUERY_KEYS.authMe, null);
      queryClient.clear();
      router.replace(ROUTES.LOGIN);
    },
  });
}
