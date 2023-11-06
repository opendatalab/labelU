/** @type {import('tailwindcss').Config} */
module.exports = {
  daisyui: {
    themes: ['light', 'dark', 'winter'],
  },
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  plugins: [require('@tailwindcss/typography'), require('daisyui')],
};
