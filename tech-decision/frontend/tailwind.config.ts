import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      boxShadow: {
        glass: '0 20px 80px rgba(15, 23, 42, 0.18)',
      },
      colors: {
        surface: '#0f172a',
      },
    },
  },
  plugins: [],
};

export default config;
