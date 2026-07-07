'use client';

import Link from 'next/link';

import { ROUTES } from '@drawly/constants';

import { AuthCard, LoginForm, RedirectAuthenticated } from '@/features/auth';

export default function LoginRoute(): React.JSX.Element {
  return (
    <RedirectAuthenticated>
      <AuthCard
        title="Bienvenido de nuevo"
        subtitle="Inicia sesión para administrar tus rifas"
        footer={
          <>
            ¿No tienes cuenta?{' '}
            <Link href={ROUTES.REGISTER} className="text-primary font-medium hover:underline">
              Crear cuenta
            </Link>
          </>
        }
      >
        <LoginForm />
      </AuthCard>
    </RedirectAuthenticated>
  );
}
