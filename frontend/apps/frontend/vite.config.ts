import { resolve } from 'path';

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
// import { viteMockServe } from 'vite-plugin-mock';
import svgr from 'vite-plugin-svgr';
import tsMonoAlias from 'vite-plugin-ts-mono-alias';
import { ViteEjsPlugin } from 'vite-plugin-ejs';

const isOnline = !!process.env.VITE_IS_ONLINE;
console.log('isOnline', isOnline);

// https://vitejs.dev/config/
export default defineConfig({
  base: '/',
  publicDir: resolve(__dirname, 'public'),
  envDir: resolve(__dirname, 'env'),
  server: {
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://127.0.0.1:8000',
        ws: true,
        changeOrigin: true,
      }
    },
  },

  optimizeDeps: {
    include: ['react/jsx-runtime'],
  },

  plugins: [
    react(),
    svgr(),
    ViteEjsPlugin(),
    !process.env.DIST && process.env.NODE_ENV !== 'production' && tsMonoAlias(),
  ].filter(Boolean),
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src/'),
    },
  },
  build: {
    target: 'es2015',
    terserOptions: {
      compress: {
        drop_console: false,
        drop_debugger: true,
      },
    },
  },
});
