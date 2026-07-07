import { ChevronRight } from 'lucide-react';

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

export function Breadcrumb({ items }: { items: BreadcrumbItem[] }): React.JSX.Element {
  return (
    <nav aria-label="Breadcrumb" className="text-text-secondary flex items-center gap-1 text-sm">
      {items.map((item, index) => {
        const isLast = index === items.length - 1;
        return (
          <span key={`${item.label}-${index}`} className="flex items-center gap-1">
            {item.href && !isLast ? (
              <a href={item.href} className="hover:text-text-primary transition-colors">
                {item.label}
              </a>
            ) : (
              <span className={isLast ? 'text-text-primary font-medium' : undefined}>
                {item.label}
              </span>
            )}
            {!isLast && <ChevronRight size={14} className="text-text-muted" aria-hidden />}
          </span>
        );
      })}
    </nav>
  );
}
