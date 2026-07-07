'use client';

import { isApiError } from '@drawly/api-client';
import { Alert } from '@drawly/ui/Alert';
import { Button } from '@drawly/ui/Button';
import { Field } from '@drawly/ui/Field';
import { Input } from '@drawly/ui/Input';
import { useForm } from 'react-hook-form';

import { useRegister } from '../hooks/use-auth-mutations';
import { registerFormSchema, type RegisterFormValues } from '../validators/auth-forms';

export function RegisterForm(): React.JSX.Element {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    defaultValues: { full_name: '', email: '', password: '' },
  });
  const registerUser = useRegister();

  const onSubmit = handleSubmit((values) => {
    const parsed = registerFormSchema.safeParse(values);
    if (!parsed.success) return;
    registerUser.mutate(parsed.data);
  });

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-4" noValidate>
      <Field label="Nombre completo" htmlFor="full_name" error={errors.full_name?.message}>
        <Input
          id="full_name"
          autoComplete="name"
          placeholder="María Pérez"
          {...register('full_name')}
        />
      </Field>
      <Field label="Correo" htmlFor="email" error={errors.email?.message}>
        <Input
          id="email"
          type="email"
          autoComplete="email"
          placeholder="tucorreo@ejemplo.com"
          {...register('email')}
        />
      </Field>
      <Field
        label="Contraseña"
        htmlFor="password"
        error={errors.password?.message}
        hint="Mínimo 8 caracteres"
      >
        <Input
          id="password"
          type="password"
          autoComplete="new-password"
          placeholder="••••••••"
          {...register('password')}
        />
      </Field>

      {registerUser.isError && (
        <Alert tone="danger">
          {isApiError(registerUser.error) && registerUser.error.status === 409
            ? 'Ese correo ya está registrado.'
            : 'No se pudo crear la cuenta. Intenta de nuevo.'}
        </Alert>
      )}

      <Button type="submit" className="w-full" loading={registerUser.isPending}>
        Crear cuenta
      </Button>
    </form>
  );
}
