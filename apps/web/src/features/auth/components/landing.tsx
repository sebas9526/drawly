'use client';

import {
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Link2,
  Share2,
  ShieldCheck,
  Ticket,
  Trophy,
  Users,
} from 'lucide-react';
import Link from 'next/link';

import { ROUTES } from '@drawly/constants';
import { Button } from '@drawly/ui/Button';
import { ThemeToggle } from '@drawly/ui/ThemeToggle';

const STEPS = [
  {
    icon: Ticket,
    title: 'Crea tu rifa',
    description: 'Define el premio, el precio y la cantidad de boletas en minutos.',
  },
  {
    icon: Share2,
    title: 'Comparte el enlace',
    description: 'Publica un enlace público para que los participantes reserven su boleta.',
  },
  {
    icon: Trophy,
    title: 'Elige al ganador',
    description: 'Administra reservas, pagos y selecciona la boleta ganadora.',
  },
];

const FEATURES = [
  {
    icon: Link2,
    title: 'Enlace público',
    description: 'Un portal de reservas listo para compartir.',
  },
  { icon: Users, title: 'Participantes', description: 'Registra y consulta a cada participante.' },
  {
    icon: BarChart3,
    title: 'Panel de control',
    description: 'Métricas de ventas y reservas en vivo.',
  },
  {
    icon: ShieldCheck,
    title: 'Datos privados',
    description: 'Cada organizador ve solo su información.',
  },
];

const BENEFITS = [
  'Sin instalaciones: funciona desde el navegador.',
  'Reservas en tiempo real con control de disponibilidad.',
  'Tus rifas, boletas y participantes siempre aislados por cuenta.',
  'Interfaz moderna en modo claro y oscuro.',
];

function TopBar(): React.JSX.Element {
  return (
    <header className="border-border/60 bg-background/80 sticky top-0 z-30 border-b backdrop-blur">
      <div className="mx-auto flex h-16 w-full max-w-6xl items-center gap-3 px-6">
        <span className="bg-primary text-primary-fg flex h-8 w-8 items-center justify-center rounded-lg">
          <Ticket size={18} />
        </span>
        <span className="text-lg font-semibold">Drawly</span>
        <div className="ml-auto flex items-center gap-2">
          <ThemeToggle />
          <Link href={ROUTES.LOGIN}>
            <Button variant="ghost" size="sm">
              Iniciar sesión
            </Button>
          </Link>
          <Link href={ROUTES.REGISTER}>
            <Button size="sm">Crear cuenta</Button>
          </Link>
        </div>
      </div>
    </header>
  );
}

export function Landing(): React.JSX.Element {
  return (
    <div className="bg-background text-text-primary min-h-screen">
      <TopBar />

      {/* Hero */}
      <section className="mx-auto flex w-full max-w-6xl flex-col items-center gap-6 px-6 py-20 text-center">
        <span className="border-border bg-surface text-text-secondary inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium">
          <Ticket size={13} /> Gestión de rifas, simple y profesional
        </span>
        <h1 className="max-w-3xl text-balance text-4xl font-semibold tracking-tight sm:text-5xl">
          Crea, comparte y administra tus rifas en un solo lugar
        </h1>
        <p className="text-text-secondary max-w-xl text-balance text-lg">
          Drawly es la plataforma para organizar rifas: genera boletas numeradas, recibe reservas
          desde un enlace público y elige al ganador con total control.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <Link href={ROUTES.REGISTER}>
            <Button size="lg" rightIcon={<ArrowRight size={16} />}>
              Crear cuenta gratis
            </Button>
          </Link>
          <Link href={ROUTES.LOGIN}>
            <Button size="lg" variant="outline">
              Iniciar sesión
            </Button>
          </Link>
        </div>
      </section>

      {/* Cómo funciona */}
      <section className="border-border/60 border-t">
        <div className="mx-auto w-full max-w-6xl px-6 py-16">
          <h2 className="text-center text-2xl font-semibold">Cómo funciona</h2>
          <p className="text-text-secondary mt-2 text-center">
            Tres pasos para poner tu rifa en marcha.
          </p>
          <div className="mt-10 grid gap-6 sm:grid-cols-3">
            {STEPS.map((step, index) => (
              <div
                key={step.title}
                className="border-border bg-surface flex flex-col gap-3 rounded-2xl border p-6"
              >
                <div className="flex items-center gap-3">
                  <span className="bg-primary/10 text-primary flex h-10 w-10 items-center justify-center rounded-xl">
                    <step.icon size={20} />
                  </span>
                  <span className="text-text-muted text-sm font-semibold">Paso {index + 1}</span>
                </div>
                <h3 className="text-lg font-medium">{step.title}</h3>
                <p className="text-text-secondary text-sm">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Beneficios + Features */}
      <section className="border-border/60 border-t">
        <div className="mx-auto grid w-full max-w-6xl gap-10 px-6 py-16 lg:grid-cols-2">
          <div className="flex flex-col gap-5">
            <h2 className="text-2xl font-semibold">Todo lo que necesitas para tu rifa</h2>
            <ul className="flex flex-col gap-3">
              {BENEFITS.map((benefit) => (
                <li key={benefit} className="flex items-start gap-3">
                  <CheckCircle2 size={18} className="text-success mt-0.5 shrink-0" />
                  <span className="text-text-secondary">{benefit}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            {FEATURES.map((feature) => (
              <div
                key={feature.title}
                className="border-border bg-surface flex flex-col gap-2 rounded-2xl border p-5"
              >
                <span className="bg-primary/10 text-primary flex h-9 w-9 items-center justify-center rounded-lg">
                  <feature.icon size={18} />
                </span>
                <h3 className="font-medium">{feature.title}</h3>
                <p className="text-text-secondary text-sm">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA final */}
      <section className="border-border/60 border-t">
        <div className="mx-auto w-full max-w-6xl px-6 py-16">
          <div className="bg-primary text-primary-fg flex flex-col items-center gap-4 rounded-3xl px-6 py-12 text-center">
            <h2 className="text-2xl font-semibold">¿Listo para tu próxima rifa?</h2>
            <p className="max-w-md opacity-90">
              Crea tu cuenta y publica tu primera rifa hoy mismo. Los planes de pago llegarán
              pronto.
            </p>
            <Link href={ROUTES.REGISTER}>
              <Button size="lg" variant="secondary" rightIcon={<ArrowRight size={16} />}>
                Crear cuenta gratis
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-border/60 border-t">
        <div className="text-text-secondary mx-auto flex w-full max-w-6xl flex-col items-center justify-between gap-3 px-6 py-8 text-sm sm:flex-row">
          <div className="flex items-center gap-2">
            <span className="bg-primary text-primary-fg flex h-6 w-6 items-center justify-center rounded-md">
              <Ticket size={13} />
            </span>
            <span className="text-text-primary font-medium">Drawly</span>
          </div>
          <p>© {new Date().getFullYear()} Drawly. Todos los derechos reservados.</p>
          <div className="flex items-center gap-4">
            <Link href={ROUTES.LOGIN} className="hover:text-text-primary">
              Iniciar sesión
            </Link>
            <Link href={ROUTES.REGISTER} className="hover:text-text-primary">
              Crear cuenta
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
