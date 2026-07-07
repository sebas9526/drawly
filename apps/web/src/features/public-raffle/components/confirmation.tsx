'use client';

import type { PublicReserveResult } from '@drawly/api-client';
import { Button } from '@drawly/ui/Button';
import { Card } from '@drawly/ui/Card';
import { CheckCircle2 } from 'lucide-react';

interface ConfirmationProps {
  result: PublicReserveResult;
  onReserveAnother: () => void;
}

export function Confirmation({ result, onReserveAnother }: ConfirmationProps): React.JSX.Element {
  return (
    <Card className="flex flex-col items-center gap-4 p-8 text-center">
      <div className="bg-success/10 text-success flex h-14 w-14 items-center justify-center rounded-full">
        <CheckCircle2 size={30} />
      </div>
      <h2 className="text-text-primary text-xl font-semibold">¡Reserva confirmada!</h2>
      <p className="text-text-secondary text-sm">
        Reservaste la boleta{' '}
        <span className="text-text-primary font-semibold">#{result.ticket_number}</span> de la rifa{' '}
        <span className="text-text-primary font-semibold">{result.raffle_title}</span>.
      </p>
      <p className="text-text-secondary text-sm">
        El organizador se pondrá en contacto contigo para completar el pago.
      </p>
      <Button variant="outline" onClick={onReserveAnother}>
        Reservar otra boleta
      </Button>
    </Card>
  );
}
