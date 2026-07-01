import reactHooks from 'eslint-plugin-react-hooks';

import { baseConfig } from './base.js';

/**
 * Shared ESLint flat config for Drawly framework-agnostic React packages (e.g. packages/ui).
 * @type {import('eslint').Linter.Config[]}
 */
export const reactLibraryConfig = [
  ...baseConfig,
  {
    plugins: { 'react-hooks': reactHooks },
    rules: {
      ...reactHooks.configs.recommended.rules,
    },
  },
];

export default reactLibraryConfig;
