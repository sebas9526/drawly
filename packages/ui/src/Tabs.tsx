import { cn } from '@drawly/utils';

export interface TabItem {
  value: string;
  label: string;
}

interface TabsProps {
  tabs: TabItem[];
  value: string;
  onChange: (value: string) => void;
}

export function Tabs({ tabs, value, onChange }: TabsProps): React.JSX.Element {
  return (
    <div className="border-border flex gap-1 border-b" role="tablist">
      {tabs.map((tab) => {
        const active = tab.value === value;
        return (
          <button
            key={tab.value}
            type="button"
            role="tab"
            aria-selected={active}
            onClick={() => onChange(tab.value)}
            className={cn(
              '-mb-px border-b-2 px-3 py-2 text-sm font-medium transition-colors',
              active
                ? 'border-primary text-primary'
                : 'text-text-secondary hover:text-text-primary border-transparent',
            )}
          >
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
