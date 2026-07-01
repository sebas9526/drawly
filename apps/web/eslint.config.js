import { nextConfig } from '@drawly/eslint-config/next';

const config = [
  ...nextConfig,
  {
    ignores: ['.next/**', 'next-env.d.ts'],
  },
];

export default config;
