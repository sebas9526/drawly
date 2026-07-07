import { ChevronLeft, ChevronRight } from 'lucide-react';

import { IconButton } from './IconButton';

interface PaginationProps {
  page: number;
  pageCount: number;
  onPageChange: (page: number) => void;
}

export function Pagination({ page, pageCount, onPageChange }: PaginationProps): React.JSX.Element {
  return (
    <div className="text-text-secondary flex items-center justify-end gap-2 text-sm">
      <IconButton
        size="sm"
        variant="outline"
        aria-label="Página anterior"
        disabled={page <= 1}
        onClick={() => onPageChange(page - 1)}
      >
        <ChevronLeft size={16} />
      </IconButton>
      <span>
        {page} / {Math.max(pageCount, 1)}
      </span>
      <IconButton
        size="sm"
        variant="outline"
        aria-label="Página siguiente"
        disabled={page >= pageCount}
        onClick={() => onPageChange(page + 1)}
      >
        <ChevronRight size={16} />
      </IconButton>
    </div>
  );
}
