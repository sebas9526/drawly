'use client';

import Link from 'next/link';

import { ROUTES } from '@drawly/constants';

import { AuthCard, RedirectAuthenticated, RegisterForm } from '@/features/auth';

export default function RegisterRoute(): React.JSX.Element {
  return (
    <RedirectAuthenticated>
      <AuthCard
        title="Crea tu cuenta"
        subtitle="Empieza a organizar rifas en minutos"
        footer={
          <>
            ¿Ya tienes cuenta?{' '}
            <Link href={ROUTES.LOGIN} className="text-primary font-medium hover:underline">
              Iniciar sesión
            </Link>
          </>
        }
      >
        <RegisterForm />
      </AuthCard>
    </RedirectAuthenticated>
  );
}
