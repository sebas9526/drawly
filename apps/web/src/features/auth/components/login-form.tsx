'use client';

import { isApiError } from '@drawly/api-client';
import { Alert } from '@drawly/ui/Alert';
import { Button } from '@drawly/ui/Button';
import { Field } from '@drawly/ui/Field';
import { Input } from '@drawly/ui/Input';
import { useForm } from 'react-hook-form';

import { useLogin } from '../hooks/use-auth-mutations';
import { loginFormSchema, type LoginFormValues } from '../validators/auth-forms';

export function LoginForm(): React.JSX.Element {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({ defaultValues: { email: '', password: '' } });
  const login = useLogin();

  const onSubmit = handleSubmit((values) => {
    const parsed = loginFormSchema.safeParse(values);
    if (!parsed.success) return;
    login.mutate(parsed.data);
  });

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-4" noValidate>
      <Field label="Correo" htmlFor="email" error={errors.email?.message}>
        <Input
          id="email"
          type="email"
          autoComplete="email"
          placeholder="tucorreo@ejemplo.com"
          {...register('email')}
        />
      </Field>
      <Field label="Contraseña" htmlFor="password" error={errors.password?.message}>
        <Input
          id="password"
          type="password"
          autoComplete="current-password"
          placeholder="••••••••"
          {...register('password')}
        />
      </Field>

      {login.isError && (
        <Alert tone="danger">
          {isApiError(login.error) && login.error.status === 401
            ? 'Correo o contraseña incorrectos.'
            : 'No se pudo iniciar sesión. Intenta de nuevo.'}
        </Alert>
      )}

      <Button type="submit" className="w-full" loading={login.isPending}>
        Iniciar sesión
      </Button>
    </form>
  );
}
