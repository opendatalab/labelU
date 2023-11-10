const defaultTheme = require('tailwindcss/defaultTheme');

/** @type {import('tailwindcss').Config} */
module.exports = {
  theme: {
    screens: {
      xs: '375px',
      ...defaultTheme.screens,
    },
  },
  daisyui: {
    themes: ['winter'],
  },
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  plugins: [require('@tailwindcss/typography'), require('daisyui')],
};
