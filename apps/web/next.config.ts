import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  transpilePackages: [
    '@drawly/api-client',
    '@drawly/config',
    '@drawly/constants',
    '@drawly/hooks',
    '@drawly/types',
    '@drawly/ui',
    '@drawly/utils',
    '@drawly/validators',
  ],
};

export default nextConfig;
