import { FlatCompat } from '@eslint/eslintrc';

import { baseConfig } from './base.js';

const compat = new FlatCompat({ baseDirectory: import.meta.dirname });

/**
 * Shared ESLint flat config for Drawly Next.js apps.
 * eslint-config-next still ships legacy eslintrc-style configs, so we
 * bridge them into flat config via FlatCompat (the same approach Next.js's
 * own `create-next-app` scaffolds).
 * @type {import('eslint').Linter.Config[]}
 */
export const nextConfig = [
  // next/core-web-vitals first: baseConfig's TypeScript parser/rules must come
  // last so they win for *.ts(x) files instead of Next's Babel-based parser.
  ...compat.extends('next/core-web-vitals'),
  ...baseConfig,
];

export default nextConfig;
