import * as path from 'path';
import { defineConfig } from 'rspress/config';
import { pluginGoogleAnalytics } from 'rsbuild-plugin-google-analytics';

export default defineConfig({
  root: path.join(__dirname, 'docs'),
  title: 'LabelU',
  lang: 'zh',
  description: 'Rspack-based Static Site Generator',
  locales: [
    {
      lang: 'en',
      label: 'English',
      title: 'Modern.js',
      description: 'Modern.js 文档框架',
    },
    {
      lang: 'zh',
      // 导航栏切换语言的标签
      label: '简体中文',
      title: 'Modern.js',
      description: 'Rspress',
    },
  ],
  icon: '/logo.svg',
  logoText: "LabelU",
  logo: {
    light: '/logo.svg',
    dark: '/logo.svg',
  },
  builderConfig: {
    plugins: [
      pluginGoogleAnalytics({ id: 'G-VZ82VW0WEH' }),
    ],
    source: {
      alias: {
        'components': path.join(__dirname, 'components'),
        '@en': path.join(__dirname, 'docs/en'),
        '@zh': path.join(__dirname, 'docs/zh'),
      },
    },
  },
  route: {
    cleanUrls: true,
  },
  globalStyles: path.join(__dirname, 'styles/index.css'),
  themeConfig: {
    footer: {
      message: 'Powered by OpenDataLab',
    },
    locales: [
      {
        lang: 'en',
        label: 'English',
        title: 'LabelU',
        description: 'The Rspack-based build tool for the web',
        editLink: {
          docRepoBaseUrl:
            'https://github.com/opendatalab/labelU/tree/website',
          text: 'Edit this page on GitHub',
        },
      },
      {
        lang: 'zh',
        label: '简体中文',
        title: 'Rsbuild',
        outlineTitle: '目录',
        prevPageText: '上一页',
        nextPageText: '下一页',
        description: '基于 Rspack 的 Web 构建工具',
        editLink: {
          docRepoBaseUrl:
            'https://github.com/opendatalab/labelU/tree/website',
          text: '在 GitHub 上编辑此页',
        },
      },
    ],
    socialLinks: [
      {
        icon: {
          svg: `<div id="labelukit">
            LabelU-kit
            <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 24 24" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M13 3L16.293 6.293 9.293 13.293 10.707 14.707 17.707 7.707 21 11 21 3z"></path><path d="M19,19H5V5h7l-2-2H5C3.897,3,3,3.897,3,5v14c0,1.103,0.897,2,2,2h14c1.103,0,2-0.897,2-2v-5l-2-2V19z"></path></svg>
            <style>
              #labelukit {
                display: flex;
                align-items: center;
                gap: 0.5em;
              }
              .social-links:nth-child(1) > div {
                width: auto;
              }
            </style>
          </div>`
        },
        mode: 'link',
        content: 'https://github.com/opendatalab/labelU-kit#readme',
      },
      { icon: 'github', mode: 'link', content: 'https://github.com/opendatalab/labelU' },
    ],
  },
});
