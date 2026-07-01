import { baseConfig } from '@drawly/eslint-config/base';

/**
 * Root ESLint config. Only lints root-level tooling files;
 * apps/* and packages/* define their own configs extending @drawly/eslint-config.
 * @type {import('eslint').Linter.Config[]}
 */
export default [
  ...baseConfig,
  {
    files: ['*.config.js', '*.config.mjs', 'commitlint.config.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
    },
  },
  {
    ignores: ['apps/**', 'packages/**', 'pnpm-lock.yaml'],
  },
];
