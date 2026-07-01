import tailwindPreset from '@drawly/config/tailwind-preset';
import type { Config } from 'tailwindcss';

const config: Config = {
  presets: [tailwindPreset],
  content: ['./src/**/*.{ts,tsx}', '../../packages/ui/src/**/*.{ts,tsx}'],
};

export default config;
