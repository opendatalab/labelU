/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#2126C0',
        success: '#00b365',
        warning: '#ff8800',
        error: '#f5483b',
        'base-color': '#121316',
        color: 'rgba(18, 19, 22, 0.8)',
        secondary: 'rgba(18, 19, 22, 0.5)',
        tertiary: 'rgba(18, 19, 22, 0.25)',
        quaternary: 'rgba(18, 19, 22, 0.20)',
        // ICON 颜色
        icon: '#4A4653',
        fill: '#b4b6bc', // 一级填充色
        'fill-secondary': '#EBECF0', // 二级填充色
        'fill-tertiary': '#F4F5F9', // 三级填充色
        'fill-quaternary': '#f9f9f9', // 四级填充色
        colorBorder: '#D7D8DD',
        borderSecondary: '#EBECF0',
        borderRadius: 2,
      },
    },
  },
  plugins: [],
  corePlugins: {
    preflight: false,
  },
};
