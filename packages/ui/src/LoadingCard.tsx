import { Card } from './Card';
import { Skeleton } from './Skeleton';

interface LoadingCardProps {
  lines?: number;
}

export function LoadingCard({ lines = 3 }: LoadingCardProps): React.JSX.Element {
  return (
    <Card className="flex flex-col gap-3 p-5">
      <Skeleton className="h-4 w-1/3" />
      {Array.from({ length: lines }).map((_, index) => (
        <Skeleton key={index} className="h-3 w-full" />
      ))}
    </Card>
  );
}
