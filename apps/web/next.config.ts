import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  transpilePackages: [
    '@drawly/api-client',
    '@drawly/config',
    '@drawly/constants',
    '@drawly/types',
    '@drawly/ui',
    '@drawly/utils',
  ],
};

export default nextConfig;
