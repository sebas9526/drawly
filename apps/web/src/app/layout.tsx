import type { Metadata } from 'next';
import { Inter } from 'next/font/google';

import { themeInitScript } from '@drawly/ui/theme';

import { Providers } from './providers';
import './globals.css';

const inter = Inter({ subsets: ['latin'], variable: '--font-sans', display: 'swap' });

export const metadata: Metadata = {
  title: 'Drawly',
  description: 'Plataforma moderna de gestión de rifas',
};

export default function RootLayout({ children }: { children: React.ReactNode }): React.JSX.Element {
  return (
    <html lang="es" className={inter.variable} suppressHydrationWarning>
      <body className="font-sans" suppressHydrationWarning>
        {/* Sets the theme class before hydration to avoid a flash. */}
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
