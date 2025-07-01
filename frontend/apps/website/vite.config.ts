import { resolve } from 'path';

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import svgr from 'vite-plugin-svgr';
import { ViteEjsPlugin } from 'vite-plugin-ejs';
import tsMonoAlias from 'vite-plugin-ts-mono-alias';
import { visualizer } from 'rollup-plugin-visualizer';

// https://vitejs.dev/config/
export default defineConfig({
  base: '/labelU-Kit/',
  publicDir: resolve(__dirname, 'public'),

  server: {
    port: 3000,
  },

  optimizeDeps: {
    include: ['react/jsx-runtime'],
  },

  plugins: [
    react(),
    svgr(),
    ViteEjsPlugin(),
    process.env.ANALYZE && visualizer({ open: true, brotliSize: true, filename: './dist/_report.html' }),
    tsMonoAlias(),
  ].filter(Boolean),

  build: {
    minify: true,
    sourcemap: true,
    target: 'es2015',
    terserOptions: {
      compress: {
        drop_console: false,
        drop_debugger: false,
      },
    },
  },

  resolve: {
    alias: {
      '@': resolve(__dirname, 'src/'),
    },
  },
});
