import { resolve } from 'path';

// import prerender from '@prerenderer/rollup-plugin';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import mdx from '@mdx-js/rollup';
import svgr from 'vite-plugin-svgr';
import { ViteEjsPlugin } from 'vite-plugin-ejs';

// https://vitejs.dev/config/
export default defineConfig({
  base: '/labelU/',
  publicDir: resolve(__dirname, 'public'),

  optimizeDeps: {
    include: ['react/jsx-runtime'],
  },

  plugins: [
    { enforce: 'pre' as const, ...mdx() },
    react(),
    svgr(),
    ViteEjsPlugin(),
    // prerender({
    //   routes: ['/', '/guide/install/windows', '/guide/install/macos', '/schema/image/point'],
    //   renderer: '@prerenderer/renderer-puppeteer',
    //   rendererOptions: {
    //     renderAfterDocumentEvent: 'custom-render-trigger',
    //   },
    //   postProcess(renderedRoute) {
    //     // Replace all http with https urls and localhost to your site url
    //     renderedRoute.html = renderedRoute.html
    //       .replace(/http:/i, 'https:')
    //       .replace(/(https:\/\/)?(localhost|127\.0\.0\.1):\d*/i, process.env.CI_ENVIRONMENT_URL || '');
    //   },
    // }),
  ].filter(Boolean),
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src/'),
    },
  },
  build: {
    target: 'es2015',
  },
});
