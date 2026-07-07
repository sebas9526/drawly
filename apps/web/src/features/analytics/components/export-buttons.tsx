'use client';

import { isApiError, type AnalyticsExportFormat } from '@drawly/api-client';
import { Alert } from '@drawly/ui/Alert';
import { Button } from '@drawly/ui/Button';
import { FileSpreadsheet, FileText } from 'lucide-react';
import { useState } from 'react';

import { triggerBlobDownload } from '../services/download';

interface ExportButtonsProps {
  filenameBase: string;
  onExport: (format: AnalyticsExportFormat) => Promise<Blob>;
}

/** "Exportar Excel" / "Exportar PDF" — both formats are generated server-side
 * (openpyxl / reportlab) from the same rows the on-screen report shows. */
export function ExportButtons({ filenameBase, onExport }: ExportButtonsProps): React.JSX.Element {
  const [pending, setPending] = useState<AnalyticsExportFormat | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleExport = async (format: AnalyticsExportFormat): Promise<void> => {
    setPending(format);
    setError(null);
    try {
      const blob = await onExport(format);
      triggerBlobDownload(blob, `${filenameBase}.${format === 'excel' ? 'xlsx' : 'pdf'}`);
    } catch (err) {
      setError(isApiError(err) ? err.message : 'No se pudo generar el archivo.');
    } finally {
      setPending(null);
    }
  };

  return (
    <div className="flex flex-col items-end gap-2">
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          leftIcon={<FileSpreadsheet size={14} />}
          loading={pending === 'excel'}
          disabled={pending !== null}
          onClick={() => void handleExport('excel')}
        >
          Exportar Excel
        </Button>
        <Button
          variant="outline"
          size="sm"
          leftIcon={<FileText size={14} />}
          loading={pending === 'pdf'}
          disabled={pending !== null}
          onClick={() => void handleExport('pdf')}
        >
          Exportar PDF
        </Button>
      </div>
      {error && <Alert tone="danger">{error}</Alert>}
    </div>
  );
}
